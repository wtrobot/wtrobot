# This Python file uses the following encoding: utf-8
# Copyright (c) 2006 Red Hat, Inc. All rights reserved. This copyrighted material
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General
# Public License v.2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Author: Greg Nichols

import sys, os
import io
from xml.sax.saxutils import escape
 
class Log(io.RawIOBase):
 
    def __init__(self, filePath):
        sys.stdout.flush()
        try:
            size = os.path.getsize(filePath)
        except os.error:
            size = 0
        self.terminal = sys.stdout
        self.log = io.open(filePath, "ab")
        if not size:
            self.log.write("<output>\n".encode("utf-8"))
 
    def __escapeAndEncode(self, value):
        value = escape(value).encode("utf-8")
        return value
        '''
        # another solution:
        # Check if any non-printable char is present
        import string
        if not all(c in string.printable for c in value):
            value = ''.join(filter(lambda x:x in string.printable, value))
        return value
        '''
 
    def write(self, message):
        self.terminal.write(message)
        if self.log:
            self.log.write(self.__escapeAndEncode(message))
 
    def logOnly(self, message):
        self.log.write(message.encode("utf-8"))
    
    def flush(self):
        self.terminal.flush()
        if self.log:
            self.log.flush()
 
    def close(self):
        self.log.write("</output>\n".encode("utf-8"))
        self.log.close()
        self.log = None
 
def unitTest():
    print("Creating log qq.txt")
    log = Log("qq.txt")
    realStdout = sys.stdout
    sys.stdout = log
    print("this should go to both console and log")
    print(u'some unicode: hiçŒ«')
    sys.stdout.logOnly("in log")
    # sys.stdout.flush()
    sys.stdout = realStdout
    print("this should only go to the console")
    sys.stdout.flush()
    log.close()
    logfile = open("qq.txt", "r")
    lines = logfile.readlines()
    if lines[1] ==  "this should go to both console and log\n":
        return True
    else:
        return False
 
 
if __name__ == "__main__":
    if not unitTest():
        print("log.py unit test FAILED")
        exit(1)
    print("log.py unit test passed")
    exit(0)
