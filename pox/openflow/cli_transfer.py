# Copyright 2014 Andy Meng
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pox.core import core
import pox
import pox.lib.util
from pox.lib.addresses import EthAddr
from pox.lib.revent.revent import EventMixin
import pox.openflow.libopenflow_01 as of
import datetime
import time
from pox.lib.socketcapture import CaptureSocket
import pox.openflow.debug
from pox.openflow.util import make_type_to_unpacker_table
from pox.openflow import *
from errno import EAGAIN, ECONNRESET, EADDRINUSE, EADDRNOTAVAIL

log = core.getLogger()

import socket
import binascii
import thread
import struct

class Cli_Transfer_Task (object):
	"""
	This is the main task for cli transfer, the client socket to port 6633 is created in this task
	All the data analysis is done in socket class
	"""
	def __init__ (self,port=6633,address = '0.0.0.0'):
		#thread.__init__(self)
		self.port = int(port)
		self.address = address
		self.started = False
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.telnet = do_telnet(address,'admin','','>')
		#self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		log.debug("Created new socket socket Cli_Transfer_Task")
		log.debug("cli transfer initialed on %s:%s",self.address,self.port)

	def analysis_data(self,data):
		log.debug("controller -->switch: %s" % binascii.hexlify(data))
		self.version = ord(data[0])
		self.header_type = ord(data[1])
		self.of_len = ord(data[2])*256+ord(data[3])
		self.of_load= data[4:]
		if self.version != 1:
			log.debug("The openflow protocol is not supported, it is %d"% of_ver)
		if self.header_type == 0: # this is the hello message
			log.debug("controller -->switch hello message")
			self.xid = ord(data[6])*256+ord(data[7])
			hello_reply = of.ofp_hello()
			log.debug("switch --> controller: %s"%binascii.hexlify(hello_reply.pack()))
			self.socket.send(hello_reply.pack())

		elif self.header_type == 5: # this is the feature request message
			log.debug("controller --> switch feature request package")
			feature_reply = of.ofp_features_reply()
			log.debug("switch --> controller: %s"% binascii.hexlify(feature_reply.pack()))
			self.socket.send(feature_reply.pack())

		elif self.header_type == 9: # the set config package
			log.debug("controller --> switch set config package")

		elif self.header_type == 14: # barrier request
			log.debug("controller --> switch barrier request package")
			
			# the xid must the same as barrier request
			barrier_reply = of.ofp_barrier_reply()
			barrier_reply.xid = ord(data[-1])
			log.debug("switch --> controller: %s"% binascii.hexlify(barrier_reply.pack()))
			self.socket.send(barrier_reply.pack())

		else:
			log.debug("controller --> switch  unknow package")
			self.telnet.write("%s"%binascii.hexlify(data)) # write testin data to cli
			log.debug("controller --> switch: %s"%binascii.hexlify(data))

	def run (self):
		log.debug("Cli_Transfer_Task.run is called")
		try:
			self.socket.connect(('0.0.0.0',self.port))
			while core.running:
				data = self.socket.recv(1024)
				if not data:
					break
				self.analysis_data(data)
			self.socket.close()
			self.telnet.close()
		except socket.error as (errno, strerror):			#log.error("Error %i while cli_client connect on socket: %s",errno,strerror)
			if errno == EADDRNOTAVAIL:
				log.error("You may be specifying a local address which is not assigned to any interface.")
			else:
				log.error("the client connect failed")
			return
def do_telnet(Host, username, password, finish):
    import telnetlib
    import time
    """
    The telnet function for telnet device
    """
    en = '\r\n'
    tn = telnetlib.Telnet(Host, port=23, timeout=50)
    tn.set_debuglevel(1)
     
    tn.read_until('\n\rUsername: ')
    tn.write(username+en)
    
    #tn.read_until('dmin')
    tn.read_until('Password: ')
    tn.write(password + en)
    tn.read_until(finish)
    return tn

def launch(port=6633,address='0.0.0.0'):
	"""
	The main launch function for cli transfer task.
	"""
	cli = Cli_Transfer_Task(port=int(port),address=address)
	time.sleep(1)
	cli.run()
	core.register("cli_transfer",cli)
	return cli

if "__main__" == __name__:
	cli.run()