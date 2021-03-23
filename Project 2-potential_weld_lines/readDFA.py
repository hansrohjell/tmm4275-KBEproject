import cgi, os
import cgitb; cgitb.enable()
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
from pathlib import Path
import math
from typing import Text
#import NXopen

HOST_NAME = '127.0.0.1'  # localhost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80


#file paths

dfa_template = Path("templates/testMaze.dfa")
userinterface_file = Path("templates/htmlServer.html")


def isolate_dfa(s): #removing start and end of fetched file
    new_string = s.split("stream\\r\\n\\r\\n")[1]
    newer_string = new_string.split("------Web")[0]
    return newer_string

def line_generator(length, width, originX, originY, iterator):
    counter = 4 * iterator
    dx = originX + length
    dy = originY + width
    weldLines = "(Child) line_"+str(counter+1)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX)+", "+str(originY)+", fZ:); \n End_Point, Point("+str(dx)+", "+str(originY)+", fZ:); \n};\n\n(Child) line_"+str(counter+2)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx)+", "+str(originY)+", fZ:); \n End_Point, Point("+str(dx)+", "+str(dy)+", fZ:); \n};\n\n(Child) line_"+str(counter+3)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx)+", "+str(dy)+", fZ:); \n End_Point, Point("+str(originX)+", "+str(dy)+", fZ:); \n};\n\n(Child) line_"+str(counter+4)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX)+", "+str(dy)+", fZ:); \n End_Point, Point("+str(originX)+", "+str(originY)+", fZ:); \n};\n\n"
    fileString = ""
    fileString += weldLines    
    return fileString

def rename(fileString): #rename the dfa file from the template name
    name = fileString.split("DefClass: ")[1].split(" (ug_base_part);")[0]
    renamedFile = fileString.replace(name, "weldedMaze")
    return renamedFile
 
def read_DFA(dfa_template): #reading the uploaded dfa file and writing to a new file.
    s = dfa_template.replace('\\r', '')
    s = s.replace('\\n', '\n')
    s = rename(s)

    file = open("weldedMaze.dfa", "w")

    walls = s.split("\n\n")
    i = 0
    while i < (len(walls) - 4):
        wall = walls[i+3].split("; \n")
        
        length_param = wall[1].split(" ")
        length = length_param[2]

        width_param = wall[2].split(" ")
        width = width_param[2]
        
        origin_param = wall[4].split("(")[1].split(",")
        originX = origin_param[0]
        originY = origin_param[1]

        print("\nWall " + str(i+1) + "\n Length: " + str(length) + "\n Width: " + str(width) + "\n OriginX: " + str(originX) + "\n OriginY: " + str(originY) + "\n")      
        
        weldLines = line_generator(int(length), int(width), int(originX), int(originY), i)
        s += weldLines
        
        i += 1
             
    file.write(s)   
    file.close()   


class MyHandler(BaseHTTPRequestHandler): #the server
    def write_HTML_file(self, filename):
        self.wfile.write(bytes(open(filename).read(), 'utf-8'))

    def do_GET(self):
        if self.path == '/' or self.path == "/weldMaze":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Error. The file" + self.path + "does not exist.", 'utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()

        if self.path.find("/weldMaze") != -1:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            dfa_file = isolate_dfa(str(post_body))
            read_DFA(dfa_file)

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
