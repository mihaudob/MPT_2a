# Copyright (C) 2016 Li Cheng BUPT www.muzixing.com.
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
#
# Author:muzixing
# Time:2016/04/13
#

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER, HANDSHAKE_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib.packet import icmp
from ryu.lib.packet import ether_types
from ryu import utils


class MULTIPATH_13(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(MULTIPATH_13, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self.datapaths = {}
		self.FLAGS = True
		self.path_to_port = {1: 3, #WRR paths only
				2: 4,
				3: 5, 
				4: 6} 
		self.priority_port = 7 #QoS path
		self.path_weight = {1: 4,
				2: 3,
				3: 2,
				4: 1}
		self.servers = ["00:00:00:00:00:01","00:00:00:00:00:02"]
		global path 
		path = 1
		global counter
		counter = 0
		#self.mac_to_port.setdefault(dpid, {})
		#self.mac_to_port[dpid][src_mac] = in_port
		self.mac_to_port.setdefault(1, {})
		self.mac_to_port[1]["00:00:00:00:00:01"] = 1
		self.mac_to_port[1]["00:00:00:00:00:02"] = 2
		self.mac_to_port[1]["00:00:00:00:00:03"] = 3
		self.mac_to_port[1]["00:00:00:00:00:04"] = 3
		self.mac_to_port[1]["00:00:00:00:00:05"] = 3
		self.mac_to_port.setdefault(4, {})
		self.mac_to_port[4]["00:00:00:00:00:01"] = 1
		self.mac_to_port[4]["00:00:00:00:00:02"] = 1
		self.mac_to_port[4]["00:00:00:00:00:03"] = 6
		self.mac_to_port[4]["00:00:00:00:00:04"] = 7
		self.mac_to_port[4]["00:00:00:00:00:05"] = 8
		self.mac_to_port.setdefault(11, {})
		self.mac_to_port[11]["00:00:00:00:00:01"] = 1
		self.mac_to_port[11]["00:00:00:00:00:02"] = 1
		self.mac_to_port[11]["00:00:00:00:00:03"] = 2
		self.mac_to_port[11]["00:00:00:00:00:04"] = 2
		self.mac_to_port[11]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(12, {})
		self.mac_to_port[12]["00:00:00:00:00:01"] = 1
		self.mac_to_port[12]["00:00:00:00:00:02"] = 1
		self.mac_to_port[12]["00:00:00:00:00:03"] = 2
		self.mac_to_port[12]["00:00:00:00:00:04"] = 2
		self.mac_to_port[12]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(13, {})
		self.mac_to_port[13]["00:00:00:00:00:01"] = 1
		self.mac_to_port[13]["00:00:00:00:00:02"] = 1
		self.mac_to_port[13]["00:00:00:00:00:03"] = 2
		self.mac_to_port[13]["00:00:00:00:00:04"] = 2
		self.mac_to_port[13]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(14, {})
		self.mac_to_port[14]["00:00:00:00:00:01"] = 1
		self.mac_to_port[14]["00:00:00:00:00:02"] = 1
		self.mac_to_port[14]["00:00:00:00:00:03"] = 2
		self.mac_to_port[14]["00:00:00:00:00:04"] = 2
		self.mac_to_port[14]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(22, {})
		self.mac_to_port[22]["00:00:00:00:00:01"] = 1
		self.mac_to_port[22]["00:00:00:00:00:02"] = 1
		self.mac_to_port[22]["00:00:00:00:00:03"] = 2
		self.mac_to_port[22]["00:00:00:00:00:04"] = 2
		self.mac_to_port[22]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(23, {})
		self.mac_to_port[23]["00:00:00:00:00:01"] = 1
		self.mac_to_port[23]["00:00:00:00:00:02"] = 1
		self.mac_to_port[23]["00:00:00:00:00:03"] = 2
		self.mac_to_port[23]["00:00:00:00:00:04"] = 2
		self.mac_to_port[23]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(24, {})
		self.mac_to_port[24]["00:00:00:00:00:01"] = 1
		self.mac_to_port[24]["00:00:00:00:00:02"] = 1
		self.mac_to_port[24]["00:00:00:00:00:03"] = 2
		self.mac_to_port[24]["00:00:00:00:00:04"] = 2
		self.mac_to_port[24]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(33, {})
		self.mac_to_port[33]["00:00:00:00:00:01"] = 1
		self.mac_to_port[33]["00:00:00:00:00:02"] = 1
		self.mac_to_port[33]["00:00:00:00:00:03"] = 2
		self.mac_to_port[33]["00:00:00:00:00:04"] = 2
		self.mac_to_port[33]["00:00:00:00:00:05"] = 2
		self.mac_to_port.setdefault(34, {})
		self.mac_to_port[34]["00:00:00:00:00:01"] = 1
		self.mac_to_port[34]["00:00:00:00:00:02"] = 1
		self.mac_to_port[34]["00:00:00:00:00:03"] = 2
		self.mac_to_port[34]["00:00:00:00:00:04"] = 2
		self.mac_to_port[34]["00:00:00:00:00:05"] = 2
		
	@set_ev_cls(
		ofp_event.EventOFPErrorMsg,
		[HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
	def error_msg_handler(self, ev):
		msg = ev.msg
		self.logger.info('OFPErrorMsg received: type=0x%02x code=0x%02x '
						  'message=%s', msg.type, msg.code,
						  utils.hex_array(msg.data))

	@set_ev_cls(ofp_event.EventOFPStateChange,
				[MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if not datapath.id in self.datapaths:
				self.logger.info('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.info('unregister datapath: %016x', datapath.id)
				del self.datapaths[datapath.id]

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		dpid = datapath.id
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		# install table-miss flow entry
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
		self.add_flow(datapath, 0, 0, match, actions)
		self.logger.info("switch:%s connected", dpid)

	def add_flow_wrr(self, datapath, hard_timeout, idle_timeout, priority, match, actions):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

		mod = parser.OFPFlowMod(datapath=datapath, priority=priority, idle_timeout = idle_timeout,
								hard_timeout=hard_timeout,
								match=match, instructions=inst)
		datapath.send_msg(mod)
		
	def add_flow(self, datapath, hard_timeout, priority, match, actions):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

		mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
								hard_timeout=hard_timeout,
								match=match, instructions=inst)
		datapath.send_msg(mod)

	def _build_packet_out(self, datapath, buffer_id, src_port, dst_port, data):
		actions = []
		if dst_port:
			actions.append(datapath.ofproto_parser.OFPActionOutput(dst_port))

		msg_data = None
		if buffer_id == datapath.ofproto.OFP_NO_BUFFER:
			if data is None:
				return None
			msg_data = data

		out = datapath.ofproto_parser.OFPPacketOut(
			datapath=datapath, buffer_id=buffer_id,
			data=msg_data, in_port=src_port, actions=actions)
		return out

	def send_packet_out(self, datapath, buffer_id, src_port, dst_port, data):
		out = self._build_packet_out(datapath, buffer_id, src_port, dst_port, data)
		if out:
			datapath.send_msg(out)

	def flood(self, msg):
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		out = self._build_packet_out(datapath, ofproto.OFP_NO_BUFFER,
									 ofproto.OFPP_CONTROLLER,
									 ofproto.OFPP_FLOOD, msg.data)
		datapath.send_msg(out)
		#self.logger.info("Flooding msg")

	def arp_forwarding(self, msg, src_ip, dst_ip, eth_pkt):
		datapath = msg.datapath
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']

		out_port = self.mac_to_port[datapath.id].get(eth_pkt.dst)
		if out_port is not None:
			match = parser.OFPMatch(in_port=in_port, eth_dst=eth_pkt.dst,
									eth_type=eth_pkt.ethertype)
			actions = [parser.OFPActionOutput(out_port)]
			self.add_flow(datapath, 0, 1, match, actions)
			self.send_packet_out(datapath, msg.buffer_id, in_port,
								 out_port, msg.data)
			#self.logger.info("Reply ARP to knew host")
		else:
			self.flood(msg)

	def mac_learning(self, dpid, src_mac, in_port):
		self.mac_to_port.setdefault(dpid, {})
		if src_mac in self.mac_to_port[dpid]:
			if in_port != self.mac_to_port[dpid][src_mac]:
				return False
		else:
			self.mac_to_port[dpid][src_mac] = in_port
			return True

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		global path
		global counter
		msg = ev.msg
		datapath = msg.datapath
		dpid = datapath.id
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']
		ofproto = datapath.ofproto

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocols(ethernet.ethernet)[0]
		arp_pkt = pkt.get_protocol(arp.arp)
		ip_pkt = pkt.get_protocol(ipv4.ipv4)
		tcp_pkt = pkt.get_protocol(tcp.tcp)
		udp_pkt = pkt.get_protocol(udp.udp)
		icmp_pkt = pkt.get_protocol(icmp.icmp)

		ip_pkt_6 = pkt.get_protocol(ipv6.ipv6)
		if isinstance(ip_pkt_6, ipv6.ipv6):
			actions = []
			match = parser.OFPMatch(eth_type=ether.ETH_TYPE_IPV6)
			self.add_flow(datapath, 0, 1, match, actions)
			return

		if isinstance(arp_pkt, arp.arp):
			#self.logger.info("ARP processing")
			if self.mac_learning(dpid, eth.src, in_port) is False:
				#self.logger.info("ARP packet enter in different ports")
				return

			self.arp_forwarding(msg, arp_pkt.src_ip, arp_pkt.dst_ip, eth)
			return

		if isinstance(ip_pkt, ipv4.ipv4):
			mac_to_port_table = self.mac_to_port.get(dpid)
			if mac_to_port_table is None:
				#self.logger.info("Dpid is not in mac_to_port")
				return

			out_port = None
			if eth.dst in mac_to_port_table:
				if dpid == 1 and eth.src in self.servers and eth.dst not in self.servers:
					l4_port = 0
					if isinstance(tcp_pkt, tcp.tcp):
						l4_port = tcp_pkt.dst_port
					if isinstance(udp_pkt, udp.udp):
						l4_port = udp_pkt.dst_port
					if l4_port == 7777: #QoS
						out_port=self.priority_port
						self.logger.info("from "+eth.src+" to "+ eth.dst +" path: 5 port layer 4: " +str(l4_port))
					else: #WRR
						if counter < self.path_weight[path]:
							counter += 1
						else:
							counter = 1
							path=(path%len(self.path_to_port))+1
						out_port=self.path_to_port[path]
						self.logger.info("from "+eth.src+" to "+ eth.dst +" path: "+str(path) +" port layer 4: " +str(l4_port))
					if isinstance(tcp_pkt, tcp.tcp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=6, tcp_dst=tcp_pkt.dst_port, eth_type=eth.ethertype)
					elif isinstance(udp_pkt, udp.udp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=17, udp_dst=udp_pkt.dst_port, eth_type=eth.ethertype)
					elif isinstance(icmp_pkt, icmp.icmp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=1, eth_type=eth.ethertype)
					else:
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_type=eth.ethertype)
					
				else:
					#Normal flows
					out_port = mac_to_port_table[eth.dst]
					if isinstance(tcp_pkt, tcp.tcp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=6, eth_type=eth.ethertype)
					elif isinstance(udp_pkt, udp.udp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=17, eth_type=eth.ethertype)
					elif isinstance(icmp_pkt, icmp.icmp):
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, ip_proto=1, eth_type=eth.ethertype)
					else:
						match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_type=eth.ethertype)
							
				actions = [parser.OFPActionOutput(out_port)]
				self.add_flow_wrr(datapath, 0, 5, 10, match, actions)
				self.send_packet_out(datapath, msg.buffer_id, in_port, out_port, msg.data)
			else:
				if self.mac_learning(dpid, eth.src, in_port) is False:
					#self.logger.info("IPV4 packet enter in different ports")
					return
				else:
					self.flood(msg)
