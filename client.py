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
import copy

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
# Used by the sorted function
# #############################################################################
def GetKey(item):
    return item[0]


# #############################################################################
# Calculates the checksum based on data in the file
# #############################################################################
def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)


def CalculateChecksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        # w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        w = ord(msg[i])
        if (i+1) < len(msg):
            w += (ord(msg[i+1]) << 8) 
        s = carry_around_add(s, w)
    checksum = (~s & 0xffff)
    # print 'checksum = ', hex(~s & 0xffff)
    return checksum      


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
    s.connect(('127.0.0.1', port))
    s.send("Remember The Name.mp3")
    dataBuff = ''
    window = []
    writeQueue = []
    lastWriten = []
    total = 0

    with open('received_file', 'wb') as f:
        while True:
            recData = s.recv(1024)

            # Check if the server is done sending the file
            if re.search("About to close your connection", recData, re.IGNORECASE):
                break

            # Print debug info on packet size
            if Options.verbose > 1:
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
            unpack = struct.unpack('I', recData[4:8])
            checksum = unpack[0]

            # print 'checksum in packet ' + str(checksum)
            calcChecksum = CalculateChecksum(recData[0:4] + recData[8:])
            # print 'Calculated checksum ' + str(calcChecksum)

            # Check checksum, continue if correct
            # print 'recData[4:8] ==  CalculateChecksum(recData[8:]) > ', checksum == CalculateChecksum(recData[8:])
            if not checksum == calcChecksum:
                print 'Checksums didn\'t match'
                continue

            # Check if last packet was a resend
            if recData in window:
                continue

            # Save last ten packets in window
            if len(window) >= 10:
                window.pop(0)  # At most holds one of each packet index
            window.append(recData)

            # Get and save the last ten packets in order
            for data in window:
                inQueue = False
                unpack = struct.unpack('I', data[0:4])
                packetNum = unpack[0]
                packetData = data[8:]
                # Make sure only fresh data is stored in the write queue
                if [packetNum, packetData] in lastWriten or [packetNum, packetData] in writeQueue:
                        inQueue = True
                for writeData in writeQueue:
                    if writeData[0] == packetNum:
                        inQueue
                if not inQueue:
                    writeQueue.append([packetNum, packetData])

                    # Only send the response once the packet has been added to the write queue
                    # Send response indicating the packet has be received
                    response = 'got packet ' + str(packetNum)
                    s.send(response)

                    # Print debug info on response data
                    if Options.verbose > 2:
                        print response

                if len(writeQueue) == 10:
                    break

            # Sort the queue so everything gets writen in order
            writeQueue = sorted(writeQueue, key=GetKey)

            # Write data to file
            if len(writeQueue) == 10:
                for writeData in writeQueue:
                    f.write(writeData[1])

                # Copy the write queue and empty it
                lastWriten = copy.deepcopy(writeQueue)
                del(writeQueue[:])

        # Write left over data in the queue
        for writeData in writeQueue:
            # print "Writing packet " + str(writeData[0])
            f.write(writeData[1])

        print "Total packets received " + str(total)
        f.close()
        print 'Successfully received file'
        s.close()
        print 'Connection closed'
