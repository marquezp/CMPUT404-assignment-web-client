#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Jorge Marquez Peralta, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # return the status code sent by the server
    def get_code(self, data):
        status_line = data.split("\r\n")[0]
        return int(status_line.split(" ")[1])

    def get_headers(self,data):
        return None

    # return the body of the server response
    def get_body(self, data):
        return data.split("\r\n")[-1]
    
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
    
    # Send off the request and process the response
    def process_request(self, request, host, port):
        if port == None:
            port = 80

        # connect to the server and send the request
        self.connect(host, port)
        self.sendall(request)
        # process the response
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        # print the code and body out for the user to see
        print(code)
        print(body)
        return code, body


    # Create a GET request
    def GET(self, url, args=None):
        # REQUEST LINE
        url_parsed = urllib.parse.urlparse(url)
        # make sure its an http:// scheme
        if url_parsed.scheme != "http":
            raise Exception("Client only supports http scheme")
            
        host = url_parsed.hostname
        port = url_parsed.port
        path = url_parsed.path if url_parsed.path else "/"
    
        # create the query string
        query_string = ""
        if url_parsed.query:
            query_string = url_parsed.query
        request = ("GET %s" % path)
        # add args to the query string
        if args:
            e_args = urllib.parse.urlencode(args)
            if query_string: # path included a query
                query_string += ("&" + e_args)
            else: # no query in path
                query_string += e_args
        if query_string:
            request += ("?%s" %query_string)
        request += " HTTP/1.1\r\n"
        # REQUEST LINE
    
        # fill out headers
        request += ("Host: %s\r\n" % host)
        request += "Connection: close\r\n"
        request += "Accept: */*\r\n\r\n"
        # process the request
        code, body = self.process_request(request, host, port)
        return HTTPResponse(code, body)

    # Create a POST request
    def POST(self, url, args=None):
        # CREATE REQUEST LINE
        url_parsed = urllib.parse.urlparse(url)
        # make sure its an http:// scheme
        if url_parsed.scheme != "http":
            raise Exception("Client only supports http scheme")

        host = url_parsed.hostname
        port = url_parsed.port
        path = url_parsed.path if url_parsed.path else "/"

        request = ("POST %s HTTP/1.1\r\n" %path)
        # add arg queries to the request string
        e_args = ""
        if args:
            e_args = urllib.parse.urlencode(args)
        
        # fill out headers
        request += ("Host: %s\r\n" % host)
        request += "Connection: close\r\n"
        request += "Accept: */*\r\n"
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += ("Content-Length: %s\r\n\r\n" %(len(e_args.encode("utf-8"))))
        # add the body
        request += e_args

        # process the request
        code, body = self.process_request(request, host, port)
        return HTTPResponse(code, body)
        
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
