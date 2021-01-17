# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import struct
import time

from ryu.base import app_manager
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib import dpid as dpid_lib
from ryu.lib import stplib
from ryu.lib.mac import haddr_to_str
from ryu.lib.packet import packet
from ryu.lib.packet import dhcp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from datetime import timedelta
from datetime import time

DHCP_COUNTER = 0
DHCP_LIMIT = 5
DHCP_INTERVAL = timedelta(seconds=5)

class SimpleSwitchStp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
    _CONTEXTS = {'stplib': stplib.Stp}
    

    def __init__(self, *args, **kwargs):
        super(SimpleSwitchStp, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.stp = kwargs['stplib']

        # Sample of stplib config.
        #  please refer to stplib.Stp.set_config() for details.
        """
        config = {dpid_lib.str_to_dpid('0000000000000001'):
                     {'bridge': {'priority': 0x8000,
                                 'max_age': 10},
                      'ports': {1: {'priority': 0x80},
                                2: {'priority': 0x90}}},
                  dpid_lib.str_to_dpid('0000000000000002'):
                     {'bridge': {'priority': 0x9000}}}
        self.stp.set_config(config)
        """

    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto

        wildcards = ofproto_v1_0.OFPFW_ALL
        wildcards &= ~ofproto_v1_0.OFPFW_IN_PORT
        wildcards &= ~ofproto_v1_0.OFPFW_DL_DST

        match = datapath.ofproto_parser.OFPMatch(
            wildcards, in_port, 0, dst,
            0, 0, 0, 0, 0, 0, 0, 0, 0)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)

    def delete_flow(self, datapath):
        ofproto = datapath.ofproto

        wildcards = ofproto_v1_0.OFPFW_ALL
        match = datapath.ofproto_parser.OFPMatch(
            wildcards, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_DELETE)
        datapath.send_msg(mod)

    @set_ev_cls(stplib.EventPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        port = msg.match['in_port']
        pkt = packet.Packet(data=msg.data)

        ofproto = datapath.ofproto

        dst, src, _eth_type = struct.unpack_from('!6s6sH', buffer(msg.data), 0)

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.debug("packet in %s %s %s %s",
                          dpid, haddr_to_str(src), haddr_to_str(dst),
                          msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dst, actions)

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions)
        datapath.send_msg(out)

        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)
        if not pkt_dhcp:
            return
        else:
            self._handle_dhcp(datapath, port, pkt)
        return

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
        return state

    def _handle_dhcp(self, datapath, port, pkt):
        global DHCP_COUNTER
        global DHCP_LIMIT
        global DHCP_INTERVAL

        pkt_dhcp = pkt.get_protocols(dhcp.dhcp)[0]
        dhcp_state = self.get_state(pkt_dhcp)
        self.logger.info("NEW DHCP %s PACKET RECEIVED: %s" %
                         (dhcp_state, pkt_dhcp))
        if dhcp_state == 'DHCPDISCOVER':
            # self._send_packet(datapath, port, self.assemble_offer(pkt))
            pass
        elif dhcp_state == 'DHCPREQUEST':
            DHCP_COUNTER += 1
            if DHCP_COUNTER == 1:
                first_dhcp = time.time()
            elif DHCP_COUNTER == DHCP_LIMIT:
                last_dhcp = time.time()
                if first_dhcp - last_dhcp < DHCP_INTERVAL:
                    pass
                # shutdown port
            else:
                pass
            # self._send_packet(datapath, port, self.assemble_ack(pkt))
        else:
            return

    @set_ev_cls(stplib.EventTopologyChange, MAIN_DISPATCHER)
    def _topology_change_handler(self, ev):
        dp = ev.dp
        dpid_str = dpid_lib.dpid_to_str(dp.id)
        msg = 'Receive topology change event. Flush MAC table.'
        self.logger.debug("[dpid=%s] %s", dpid_str, msg)

        if dp.id in self.mac_to_port:
            del self.mac_to_port[dp.id]
        self.delete_flow(dp)

    @set_ev_cls(stplib.EventPortStateChange, MAIN_DISPATCHER)
    def _port_state_change_handler(self, ev):
        dpid_str = dpid_lib.dpid_to_str(ev.dp.id)
        of_state = {stplib.PORT_STATE_DISABLE: 'DISABLE',
                    stplib.PORT_STATE_BLOCK: 'BLOCK',
                    stplib.PORT_STATE_LISTEN: 'LISTEN',
                    stplib.PORT_STATE_LEARN: 'LEARN',
                    stplib.PORT_STATE_FORWARD: 'FORWARD'}
        self.logger.debug("[dpid=%s][port=%d] state=%s",
                          dpid_str, ev.port_no, of_state[ev.port_state])
