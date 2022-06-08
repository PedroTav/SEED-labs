#!/usr/bin/env python3

import threading
import socket
import ssl
import pprint

cadir = './client-certs'

SERVER_CERT = './server-certs/certs/server.crt'
SERVER_PRIVATE = './server-certs/certs/server.key'

context_srv = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context_srv.load_cert_chain(SERVER_CERT, SERVER_PRIVATE)

sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock_listen.bind(('0.0.0.0', 443))
sock_listen.listen(5)

def process_request(ssock_for_browser):
	hostname = "www.pedro2022.com"	

	# Make a connection to the real server
	context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
	context.load_verify_locations(capath=cadir)
	context.verify_mode = ssl.CERT_REQUIRED
	context.check_hostname = True
	sock_for_server  = socket.create_connection((hostname, 443))
	ssock_for_server = context.wrap_socket(sock_for_server, server_hostname=hostname,
                            do_handshake_on_connect=True) # [Code omitted]: Wrap the socket using TLS

	request = ssock_for_browser.recv(2048)
	print(request)
	if request:
		# Forward request to server
		ssock_for_server.sendall(request)
		
		# Get response from server, and forward it to browser
		response = ssock_for_server.recv(2048)
		print(response)
		while response:
			ssock_for_browser.sendall(response) # Forward to browser
			response = ssock_for_server.recv(2048)
			
	ssock_for_browser.shutdown(socket.SHUT_RDWR)
	ssock_for_browser.close()

while True:
	sock_for_browser, fromaddr = sock_listen.accept()
	ssock_for_browser = context_srv.wrap_socket(sock_for_browser,
						server_side=True)
	x = threading.Thread(target=process_request, args=(ssock_for_browser,))
	x.start()
