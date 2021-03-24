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
userinterface_error = Path("templates/userinterface_error.html")
userinterface_correct = Path("templates/userinterface_correct.html")
#image_file = Path("theMaze.png") # Husk å sette inn bildefil i mappa!

def isolate_dfa(s): #removing start and end of fetched file
    new_string = s.split("', b'")[1]
    newer_string = new_string.split("')])")[0]
    return newer_string

def line_extruder(lines, number):
    extruded_lines = ""
    vector = ["(0,-1,0)", "(1,0,0)", "(0,1,0)", "(-1,0,0)"]
    ex_old_lines = lines.replace("line_", "extrusion_weld_").replace("ug_line", "ug_extruded")
    extrudable_lines = ex_old_lines.split("};")
    
    colored_lines = ""
    c_old_lines = lines.replace("line_", "colored_weld_").replace("ug_line", "ug_body")
    colorable_lines = c_old_lines.split("};")
        
    for i in range(4):
        counter = number + i + 1

        profile = "Profile, {line_" + str(counter) + ":};"
        direction = " \n Direction, Vector" + vector[i] + ";"
        limits = "\n Start_Limit, 0; \n End_Limit, 3;"
        extruded_line = extrudable_lines[i].split("Start")[0] + profile + direction + limits + "\n};"     
        extruded_lines += extruded_line

        feature = " Feature, {extrusion_weld_" + str(counter) + ":};"
        layer = "\n Layer, 1;"
        color = "\n color, ug_askClosestColor(DARK_DULL_GREEN);"
        colored_line = colorable_lines[i].split("Start")[0] + feature + layer + color + "\n};"
        colored_lines += colored_line
    
    weldPath = extruded_lines + colored_lines
    return weldPath

def line_generator(length, width, originX, originY, iterator):
    counter = 4 * iterator
    dx = originX + length
    dy = originY + width
    weldLines = "\n\n(Child) line_"+str(counter+1)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX-3)+", "+str(originY)+", fZ:+0.1); \n End_Point, Point("+str(dx+3)+", "+str(originY)+", fZ:+0.1); \n};\n\n(Child) line_"+str(counter+2)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx)+", "+str(originY-3)+", fZ:+0.1); \n End_Point, Point("+str(dx)+", "+str(dy+3)+", fZ:+0.1); \n};\n\n(Child) line_"+str(counter+3)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx+3)+", "+str(dy)+", fZ:+0.1); \n End_Point, Point("+str(originX-3)+", "+str(dy)+", fZ:+0.1); \n};\n\n(Child) line_"+str(counter+4)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX)+", "+str(dy+3)+", fZ:+0.1); \n End_Point, Point("+str(originX)+", "+str(originY-3)+", fZ:+0.1); \n};\n\n"
    extruded_lines = line_extruder(weldLines, counter)
    fileString = ""
    fileString += weldLines
    fileString += extruded_lines  
    return fileString

def rename(fileString): #rename the dfa file from the template name. Maybe we won't use this.
    name = fileString.split("DefClass: ")[1].split(" (ug_base_part);")[0]
    renamedFile = fileString.replace(name, "weldedMaze")
    return renamedFile
 
def read_DFA(dfa_template): #reading the uploaded dfa file and writing to a new file.
    s = dfa_template.replace('\\r', '')
    s = s.replace('\\n', '\n')
    #s = rename(s)

    file = open("weldedMaze.dfa", "w")

    walls = s.split("\n\n")
    i = 0
    while i < (len(walls) - 3):
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

"""
def error_message(error_filename):
    file = error_filename
"""


def reload_nx():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display

    workPart.RuleManager.Reload(True)

def export_nx_img():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display

    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    theUI = NXOpen.UI.GetUI()

    imageExportBuilder1 = theUI.CreateImageExportBuilder()

    imageExportBuilder1.RegionMode = False

    regiontopleftpoint1 = [None] * 2
    regiontopleftpoint1[0] = 0
    regiontopleftpoint1[1] = 0
    imageExportBuilder1.SetRegionTopLeftPoint(regiontopleftpoint1)

    imageExportBuilder1.RegionWidth = 1

    imageExportBuilder1.RegionHeight = 1

    imageExportBuilder1.FileFormat = NXOpen.Gateway.ImageExportBuilder.FileFormats.Png

    imageExportBuilder1.FileName = "<YOUR PATH HERE>"

    imageExportBuilder1.BackgroundOption = NXOpen.Gateway.ImageExportBuilder.BackgroundOptions.Original

    imageExportBuilder1.EnhanceEdges = False

    nXObject1 = imageExportBuilder1.Commit()

    theSession.DeleteUndoMark(markId1, "Export Image")

    imageExportBuilder1.Destroy()


class MyHandler(BaseHTTPRequestHandler): #the server
    def write_HTML_file(self, filename):
        self.wfile.write(bytes(open(filename).read(), 'utf-8'))

    def do_GET(self):
        if self.path == '/' or self.path == "/weldMaze":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)

        elif(self.path == '/theMaze.png') != -1:
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            bReader = open(image_file, "rb")
            theImg = bReader.read()
            self.wfile.write(theImg)

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Error. The file " + self.path + " does not exist.", 'utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()

        
        form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
        filename = form['filename'].filename
        if filename[-4:] != ".dfa":
           self.write_HTML_file(userinterface_error)
        
        else:
            if self.path.find("/weldMaze") != -1:
                #content_len = int(self.headers.get('Content-Length'))
                #post_body = self.rfile.read(content_len)
                dfa_file = isolate_dfa(str(form))
                read_DFA(dfa_file)
                
                self.write_HTML_file(userinterface_correct)
                #reload_nx()

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
