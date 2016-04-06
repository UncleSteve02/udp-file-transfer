import socket

# Reserve port
port = 9876
# Create socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Get local machine name
host = socket.gethostname()

s.connect(('10.0.0.1', port))
s.send("Hello server!")

with open('received_file', 'wb') as f:
	print 'file opened'
	while True:
		print 'receiving data...'
		data = s.recv(1024)
		print 'data=%s', (data)
		if not data:
			break
		# Write data to file
		f.write(data)

	f.close()
	print 'Successfully received file'
	s.close()
	print 'Connection closed'
