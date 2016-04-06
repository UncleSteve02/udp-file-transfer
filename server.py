import socket

# Reserve port
port = 9876
# Create socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Get local machine name
host = socket.gethostname()
# Bind to port
s.bind(('', port))
# Start to listen for client connection
s.listen(5)

print 'Listening...'

while True:
	# Establish connection with client
	conn, addr = s.accept() 
	print 'Got connection from ', addr
	data = conn.recv(1024)
	print 'Server received ', repr(data)

	filename = 'server_to_client_file.txt'
	f = open(filename, 'rb')
	l = f.read(1024)
	while (l):
		conn.send(l)
		print 'Sent ', repr(l)
		l = f.read(1024)
	f.close()

	print 'Finished sending to ', repr(data)
	conn.send('About to close your connection')
	conn.close()
