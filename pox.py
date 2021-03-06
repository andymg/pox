#!/bin/sh -

# Copyright 2011-2012 James McCauley
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

# If you have PyPy 1.6+ in a directory called pypy alongside pox.py, we
# use it.
# Otherwise, we try to use a Python interpreter called python2.7, which
# is a good idea if you're using Python from MacPorts, for example.
# We fall back to just "python" and hope that works.

''''true
#export OPT="-u -O"
export OPT="-u"
export FLG=""
if [ "$(basename $0)" = "debug-pox.py" ]; then
  export OPT=""
  export FLG="--debug"
fi

if [ -x pypy/bin/pypy ]; then
  exec pypy/bin/pypy $OPT "$0" $FLG "$@"
fi

if type python2.7 > /dev/null 2> /dev/null; then
  exec python2.7 $OPT "$0" $FLG "$@"
fi
exec python $OPT "$0" $FLG "$@"
'''

from pox.boot import boot
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

if __name__ == '__main__':
  boot()
  cli.run()
