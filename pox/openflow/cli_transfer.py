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
import datetime
import time
from pox.lib.socketcapture import CaptureSocket
import pox.openflow.debug
from pox.openflow.util import make_type_to_unpacker_table
from pox.openflow import *
import binascii
from errno import EAGAIN, ECONNRESET, EADDRINUSE, EADDRNOTAVAIL

log = core.getLogger()

import socket
import select
import binascii
import threading

class Cli_Transfer_Task (threading.Thread):
	"""
	This is the main task for cli transfer, the client socket to port 6633 is created in this task
	All the data analysis is done in socket class
	"""
	def __init__ (self,port=6633,address = '0.0.0.0'):
		threading.Thread.__init__(self)
		self.port = int(port)
		self.address = address
		self.started = False
		log.info("cli transfer initialed on %s:%s",self.address,self.port)
		self.cli_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		#self.cli_client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		log.info("Created new cli_client socket Cli_Transfer_Task")

	def run (self):
		log.info("Cli_Transfer_Task.run is called")
		try:
			self.cli_client.connect((self.address,self.port))
			while core.running:
				data = self.cli_client.recv(1024)
				if not data:
					break
				log.info("received data: %s" % binascii.hexlify(data))
			self.cli_client.close()
		except socket.error as (errno, strerror):
			log.error("Error %i while cli_client connect on socket: %s",errno,strerror)
			if errno == EADDRNOTAVAIL:
				log.error("You may be specifying a local address which is not assigned to any interface.")
			else:
				log.error("the client connect failed")
			return


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