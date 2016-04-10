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
# Main function for server
# #############################################################################
if __name__ == '__main__':

    # Process Arguments
    ProcessArguments()

    # Reserve port
    port = 9876

    # Create socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Get local machine name
    host = socket.gethostname()

    # Bind to port
    s.bind(('', port))

    while True:
        revData, addr = s.recvfrom(1024)
        print 'Got connection from ', addr
        print 'Server received ', repr(revData)

        # Create list to hold data packets
        window = []
        filename = 'Remember The Name.mp3'
        fileToTransfer = open(filename, 'rb')
        fileData = fileToTransfer.read(512)
        i = 0
        while fileData:

            # Set up data packet
            header = struct.pack('I', i)
            dataPacket = header + fileData
            i += 1

            # Once the window is full doo not send new data
            if len(window) >= 5:
                del window[:5]
                i = 0

            # Add data packet to the window and send to client
            window.append(dataPacket)
            s.sendto(dataPacket, addr)

            # Print debug info for data packet size
            if Options.verbose > 0:
                print sys.getsizeof(dataPacket)

            # Check for the response packet from the client
            revData, addr = s.recvfrom(1024)

            # Print debug info data sent and received
            if Options.verbose > 2:
                print 'Sent ', repr(dataPacket)
                print revData

            # Read next data set from the file
            fileData = fileToTransfer.read(512)

        fileToTransfer.close()
        s.sendto("About to close your connection", addr)

        print 'Finished sending'
    s.close()
