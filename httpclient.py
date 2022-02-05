#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust and Victor Lieu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Resources Used:
# https://docs.python.org/3/library/urllib.parse.html | For documentation on using urllip.parse


import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return self.socket

    def get_code(self, data):
        """
        Uses regex to match the first 3 consecutive integers which represents the status code
        """
        pattern = r'\b\d{3}\b'
        return re.findall(pattern, data)[0]

    def get_headers(self,data):
        """
        Uses partition on the sequence of carriage returns and newlines to separate the response header from data
        """
        pattern = '\r\n\r\n'
        return data.partition(pattern)[0]

    def get_body(self, data):
        """
        Uses partition on the sequence of carriage returns and newlines to separate the body from data
        """
        pattern = '\r\n\r\n'
        return data.partition(pattern)[2]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def sendHeaders(self, method, path, host_name, args = None):
        """
        Sends the required headers using the input HTTP method, path, hostname and arguments
        """
        self.sendall("{0} {1} HTTP/1.1\r\n".format(method, path))
        self.sendall("Host: {0}\r\n".format(host_name))
        self.sendall("User-Agent: Assignment 2 Web-Client\r\n")
        self.sendall("Accept: */*\r\n")
        # Sends additional headers if method is a POST request
        if method is "POST":
            self.sendall("Content-Type: application/x-www-form-urlencoded\r\n")
            self.sendall("Content-Length: {0}\r\n".format(len(args) if args else 0))
        self.sendall("Connection: close\r\n\r\n")
        # Sends optional args in the request body if there are any from a POST Request
        if args:
            self.sendall(args)

    def sendRequest(self, method, url, args = None):
        """
        Sends a request using the input HTTP method, url and optional arguments
        """
        o = urlparse(url)
        # Default port will be 80 if port is not provided
        default_port = o.port if o.port else 80
        # Default path will be / if path is not provided
        default_path = o.path if o.path else "/"
        # Use urlencode to parse dictionary form arguments
        default_args = urlencode(args) if args else None

        try:
            # Connect to the entered server
            socket = self.connect(o.hostname, default_port)
            
            # Sends required request headers based on HTTP method
            self.sendHeaders(method, default_path, o.hostname, default_args)

            # Receive and parse response data
            data = self.recvall(socket)
            code = self.get_code(data)
            body = self.get_body(data)

            #Close connection afterwards
            self.close()
        except Exception as e:
            # Send a 400 error code if there was an issue in the try block
            print(e)
            code = 400
            body = "Bad Request"
        
        return (code, body)
        
    def GET(self, url, args=None):
        """
        Helper Function that handles GET Requests
        """
        code, body = self.sendRequest("GET", url)

        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):
        """
        Helper Function that handles POST Requests
        """
        code, body = self.sendRequest("POST", url, args)

        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
