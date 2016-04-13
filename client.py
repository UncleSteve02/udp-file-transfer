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


# #############################################################################
# Process Arguments
# #############################################################################
def ProcessArguments():

    # Declare global variables here
    global Options

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
# Main function client
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

    # Connect to server
    s.connect(('10.0.0.1', port))
    s.send("Remember The Name.mp3")
    dataBuff = ''
    window = []
    total = 0

    with open('received_file', 'wb') as f:
        while True:
            #print 'Waiting for data'
            recData = s.recv(1024)

            # Check if the server is done sending the file
            if re.search("About to close your connection", recData, re.IGNORECASE):
                break

            # Print debug info on packet size
            if Options.verbose > 0:
                print sys.getsizeof(recData)

            # Print debug info on packet data
            if Options.verbose > 2:
                print 'data=' + repr(recData)

            if not recData:
                if Options.verbose > 1:
                    print 'Did not get any data'
                break

            total += 1
            # Unpack packet header
            unpack = struct.unpack('I', recData[0:4])
            packetNum = unpack[0]

            # Send response indicating the packet has be received
            response = 'got packet ' + str(packetNum)
            s.send(response)

            # Print debug info on response data
            if Options.verbose > 2:
                print response

            # Check if last packet was a resend
            if recData in window:
                continue

            # Save last ten packets in window
            if len(window) >= 10:
                window.pop(0)
            window.append(recData)

            # Write data to file
            packetData = recData[4:]
            print "Writing packet " + str(packetNum)
            f.write(packetData)

        print "Total packets received " + str(total)
        f.close()
        print 'Successfully received file'
        s.close()
        print 'Connection closed'
