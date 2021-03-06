# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.topology import event
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import dhcp
from ryu.lib.packet import ipv4
from datetime import timedelta
from datetime import time
import time

DHCP_COUNTER = 0
DHCP_LIMIT = 3
DHCP_INTERVAL = timedelta(seconds=60).total_seconds()
drop_checker = {}

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def delete_flow(self, datapath, in_port):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #for dst in self.mac_to_port[datapath.id].keys():
        match = parser.OFPMatch(in_port=in_port)
        mod = parser.OFPFlowMod(
            datapath, command=ofproto.OFPFC_DELETE,
            out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY,
            priority=1, match=match)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch

        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        try:
            drop_checker[in_port]
        except KeyError:
            drop_checker[in_port] = False


        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        ### Zanim zaczniemy zarzadzenie
        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)

        if pkt_dhcp:
            self.logger.info("It's DHCP")
            self._handle_dhcp(datapath, in_port, pkt, drop_checker)

        self.logger.info("DROP_CHECKER: %s", drop_checker)

        if drop_checker[in_port] == True:
            self.logger.info("<!!!> PODEJMUJE AKCJE <!!!>")
            self.delete_flow(datapath, in_port)
            return # powinno przesta procesowac wszystko z tego postu
        
        self.logger.info("Packet forwarding")
        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port
        if drop_checker[in_port] == False:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
            if out_port != ofproto.OFPP_FLOOD:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
                # verify if we have a valid buffer_id, if yes avoid to send both
                # flow_mod & packet_out
                if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(datapath, 1, match, actions)
                
            data = None
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                data = msg.data
        
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

    def get_state(self, pkt_dhcp):
        dhcp_state = ord(
            [opt for opt in pkt_dhcp.options.option_list if opt.tag == 53][0].value)
        if dhcp_state == 1:
            state = 'DHCPDISCOVER'
        elif dhcp_state == 2:
            state = 'DHCPOFFER'
        elif dhcp_state == 3:
            state = 'DHCPREQUEST'
        elif dhcp_state == 5:
            state = 'DHCPACK'
        else:
            state = 'DHCPREQUEST'
        return state


    def _handle_dhcp(self, datapath, port, pkt, drop_checker):
        global DHCP_COUNTER
        global DHCP_LIMIT
        global DHCP_INTERVAL
        global first_dhcp

        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)[0]
        dhcp_state = self.get_state(pkt_dhcp)
        self.logger.info("NEW DHCP %s PACKET RECEIVED.", dhcp_state)#%s" %
                        # (dhcp_state, pkt_dhcp))
        if dhcp_state == 'DHCPDISCOVER' or dhcp_state == 'DHCPREQUEST':  #DHCPREQUEST
            if DHCP_COUNTER == 0:
                first_dhcp = time.time()
                self.logger.info("Time of first registered: %s",first_dhcp)
            DHCP_COUNTER += 1
            self.logger.info("State of the DHCP Counter: %s",DHCP_COUNTER)
            if DHCP_COUNTER == DHCP_LIMIT:
                last_dhcp = time.time()
                self.logger.info("Time of %s registered: %s",DHCP_LIMIT,last_dhcp)
                self.logger.info("Time between the first and last: %s, the restrictions: %s", (last_dhcp - first_dhcp), DHCP_INTERVAL)
                if last_dhcp - first_dhcp < DHCP_INTERVAL:
                    self.logger.info("DHCP STARVATION ATTACK DISCOVERED ON PORT: %s", port)
                    
                    drop_checker[port] = True
                    DHCP_COUNTER = 0

                    return drop_checker
                else:
                    DHCP_COUNTER = 0

                    return drop_checker
            else:
                pass
        else:
            return
