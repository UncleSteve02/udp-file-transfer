# #############################################################################
"""
Authors: Travis Page & Steven Demers
Date: 04/06/2016
File Name: client.py
Project Name: udp-file-transfer
"""
# #############################################################################
usage = """

Description: Add description later

Options:
    -v, --verbose       increases verbosity level
    -q, --quiet         zero verbosity level, i.e. no error prints

Example: Add example later

"""


# #############################################################################
# Program Imports
# #############################################################################
import socket
from optparse import OptionParser
import sys
import struct
import re
import time

# #############################################################################
# Program Imports
# #############################################################################
class Packet:
    def __init__(self):
        self.int = 0
        self.data = [None] * 512

# #############################################################################
# Process Arguments
# #############################################################################
def ProcessArguments():
    global Options

    # Declare global variables here

    parser = OptionParser(usage=usage)

    # Set up parser options
    parser.add_option('-q', '--quiet',
                      action='store_true',
                      help='set verbosity to zero')
    parser.add_option('-v', '--verbose',
                      action='count', default=1,
                      help='Increase verbosity of output')
    parser.add_option('-p', '--performance',
                      action='count', default=0,
                      help='Display performance information')

    Options, Args = parser.parse_args()

    if Options.quiet:
        Options.verbose = 0

    if Options.verbose > 1:
        print 'Verbose: %d' % Options.verbose

    # Checks number of arguments given.
    if len(Args) < 0:
        print 'Not enough arguments given.'
        sys.exit()


# #############################################################################
# Function returns the next available number for the window
# #############################################################################
def GetNextAvailableNum(window):

    num = 0
    for data in window:
        unpack = struct.unpack('I', data[0:4])
        packetNum = unpack[0]
        packetNum += len(window)
        num = packetNum % 10
        break

    return num


# #############################################################################
# Function prints the packet numbers in the current window
# #############################################################################
def PrintPacketNum(window):

    tempStr = ''
    for data in window:
        if data is None:
            tempStr += ' None'
            continue
        unpack = struct.unpack('I', data[0:4])
        packetNum = unpack[0]
        tempStr += ' ' + str(packetNum)

    print tempStr


# #############################################################################
# Function slides position of current window
# #############################################################################
def SlideWindow(window):
    # Slide window
    while len(window) > 0:
        if window[0] is None:
            window.pop(0)
        else:
            break


# #############################################################################
# Function checks response from client and removes packet from window and 
# updates the window
# #############################################################################
def CheckClientResponse(window, s):
    # Check for the response packet from the client
    try:
        recData, temp = s.recvfrom(1024)  # Non Blocking
        if recData is not None:
            # Get response packet number
            match = re.search("^.*(\d).*$", recData)
            if match:
                # Remove the corresponding data from the window
                for data in window:
                    if data is None:
                        continue
                    unpack = struct.unpack('I', data[0:4])
                    packetNum = unpack[0]
                    if packetNum is int(match.group(1)):
                        window[window.index(data)] = None

        SlideWindow(window)
    except socket.error:
        pass


# #############################################################################
# Main function for server
# #############################################################################
if __name__ == '__main__':

    # Process Arguments
    ProcessArguments()

    # Reserve port
    port = 9876

    # Create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setblocking(0)
    #s.settimeout(0.0010)

    # Get local machine name
    host = socket.gethostname()

    # Bind to port
    s.bind(('', port))

    while True:
        try:
            recData, addr = s.recvfrom(1024)
        except socket.error:
            continue

        # Create list to hold data packets
        window = []
        filename = recData
        try:
            fileToTransfer = open(filename, 'rb')
            print 'Got connection from ', addr
            print 'Server received ', repr(recData)
        except IOError:
            continue

        fileData = fileToTransfer.read(512)
        total = 0
        while fileData:

            # Set up data packet available
            i = GetNextAvailableNum(window)
            header = struct.pack('I', i)
            dataPacket = header + fileData

            # Once the window is full doo not send new data
            while len(window) >= 5:
                # Resend data in window for which we have not received a response
                for data in window:
                    if data is None:
                        continue
                    s.sendto(data, addr)

                    time.sleep(0.001)
                    CheckClientResponse(window, s)

            # Add data packet to the window and send to client
            window.append(dataPacket)
            PrintPacketNum(window)
            s.sendto(dataPacket, addr)
            total += 1

            # Print debug info for data packet size
            if Options.verbose > 0:
                print sys.getsizeof(dataPacket)

            CheckClientResponse(window, s)

            # Print debug info data sent and received
            if Options.verbose > 2:
                print 'Sent ', repr(dataPacket)
                print recData

            # Read next data set from the file
            fileData = fileToTransfer.read(512)


        fileToTransfer.close()

        # When the file is done sending wait for responses
        while len(window) > 0:
            # Resend data in window for which we have not received a response
            for data in window:
                if data is None:
                    continue
                s.sendto(data, addr)

                time.sleep(0.001)
                CheckClientResponse(window, s)

        print "Total packets sent: " + str(total)
        s.sendto("About to close your connection", addr)

        print 'Finished sending'
    s.close()
