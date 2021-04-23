from http.server import BaseHTTPRequestHandler, HTTPServer 
from os import write
import re
from pathlib import Path
import math # overflødig?
import math as m
import numpy as np
from numpy.lib.scimath import arccos
#from producibilityCheck import producibilityCheck
from generatePath import pathFinder
#import NXopen

HOST_NAME = '127.0.0.1'  # locathost - http://127.0.0.1
# Maybe set this to 1234 / So, complete address would be: http://127.0.0.1:1234
PORT_NUMBER = 1234
# Web servers example: http://www.ntnu.edu:80

# File paths
#dfa_template = Path("templates/chair_template.dfa")
userinterface_file = Path("html/userinterface.html")
userinterface_error = Path("tmp/userinterface_error.html")
userinterface_tmp = Path("tmp/userinterface_tmp.html")
userinterface_order = Path("tmp/userinterface_order.html")
userinterface_addObstacle = Path("html/userinterface_addObstacle.html")
userinterface_addFeedingLine = Path("html/userinterface_addFeedingLine.html")
userinterface_addFeedingPoint = Path("html/userinterface_addFeedingPoint.html")
userinterface_generateRailSystem = Path("html/userinterface_generateRailSystem.html")
#image_file = Path("theProduct.png")

variable_to_DFA = {
    # Rail system
    "start_point": "0,0",
    "end_point": "0,0",    
    "grid_width": "50000",
    "grid_length": "50000",

    # Obstacle
    "obstacle_position": [],
    "obstacle_width": [],
    "obstacle_length": [],

    # Feeding rail
    "feeding_start": [],
    "feeding_stop": [],

    # Feeding point
    "feeding_points": [],

    # Path points
    "path_points": [],

    # Rail path - legger til elementer her ettersom rail-pathen forlenges, alle delene blir satt sammen og bygget opp som et I-profil
    "rail_path": [] # "rail_path_1:"
}

'''
def reload_nx():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display

    workPart.RuleManager.Reload(True)


def export_nx_img():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display

    markId1 = theSession.SetUndoMark(
        NXOpen.Session.MarkVisibility.Visible, "Start")
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

    imageExportBuilder1.FileName = "C:\\Users\\hansro\\Downloads\\TMM4275-main\\theProduct.png"

    imageExportBuilder1.BackgroundOption = NXOpen.Gateway.ImageExportBuilder.BackgroundOptions.Original

    imageExportBuilder1.EnhanceEdges = False

    nXObject1 = imageExportBuilder1.Commit()

    theSession.DeleteUndoMark(markId1, "Export Image")

    imageExportBuilder1.Destroy()
'''

def parse_parameters(string):
    # Returns list of elements of ["param", "value"]
    params = string.split("&")
    for i, val in enumerate(params):
        params[i] = val.split("=")
    return params


def update_defaults(template_filename, tmp_filename, params):
    # Sets the default values in html file
    file = open(template_filename)
    data = file.read()
    file.close()
    for param in params:
        find = 'name="' + param[0] + '"' + ' value=".*?"'
        # name="cdepth" value="123456"><br>
        replace = 'name="' + param[0] + '"' + ' value="' + param[1] + '"'
        data = re.sub(find, replace, data)
    file = open(tmp_filename, "wt")
    file.write(data)
    file.close()


def update_rail_system(parameter_string): # Har ikke tatt hensyn til start og slutt til rail i dfa-fil
    start_x = parameter_string.split('start_point=')[1].split('%2C')[0]
    start_y = parameter_string.split('%2C')[1].split('&')[0]
    variable_to_DFA["start_point"] = start_x + "," + start_y

    end_x = parameter_string.split('end_point=')[1].split('%2C')[0]
    end_y = parameter_string.split('%2C')[2].split('&')[0]
    variable_to_DFA["end_point"] = end_x + "," + end_y

    variable_to_DFA["grid_width"] = parameter_string.split('grid_width=')[1].split('&')[0]
    variable_to_DFA["grid_length"] = parameter_string.split('grid_length=')[1]

    initial_lines = "#! NX/KF 10.0\n\nDefClass: dfa_test (ug_base_part);\n\n"
    parameters = "(number parameter) rail_width: 167;\n(number parameter) rail_height: 291;\n(number parameter) rail_base_height: 11.17;\n(number parameter) rail_wall_width: 6.6;\n\n"
    lines = "(Child) line_1: {\n Class, ug_line;\n Start_Point, Point(0,0,1000);\n End_Point, Point(rail_width:,0,1000);\n};\n\n(Child) line_2: {\n Class, ug_line;\n Start_Point, Point(rail_width:,0,1000);\n End_Point, Point(rail_width:,0,rail_base_height:+1000);\n};\n\n(Child) line_3: {\n Class, ug_line;\n Start_Point, Point(rail_width:,0,rail_base_height:+1000);\n End_Point, Point((rail_width:/2)+(rail_wall_width:/2),0,rail_base_height:+1000);\n};\n\n(Child) line_4: {\n Class, ug_line;\n Start_Point, Point((rail_width:/2)+(rail_wall_width:/2),0,rail_base_height:+1000);\n End_Point, Point((rail_width:/2)+(rail_wall_width:/2),0,rail_base_height:+rail_height:+1000);\n};\n\n(Child) line_5: {\n Class, ug_line;\n Start_Point, Point((rail_width:/2)+(rail_wall_width:/2),0,rail_base_height:+rail_height:+1000);\n End_Point, Point(rail_width:,0,rail_base_height:+rail_height:+1000);\n};\n\n(Child) line_6: {\n Class, ug_line;\n Start_Point, Point(rail_width:,0,rail_base_height:+rail_height:+1000);\n End_Point, Point(rail_width:,0,(rail_base_height:*2)+rail_height:+1000);\n};\n\n(Child) line_7: {\n Class, ug_line;\n Start_Point, Point(rail_width:,0,(rail_base_height:*2)+rail_height:+1000);\n End_Point, Point(0,0,(rail_base_height:*2)+rail_height:+1000);\n};\n\n(Child) line_8: {\n Class, ug_line;\n Start_Point, Point(0,0,rail_base_height:*2+rail_height:+1000);\n End_Point, Point(0,0,rail_base_height:+rail_height:+1000);\n};\n\n(Child) line_9: {\n Class, ug_line;\n Start_Point, Point(0,0,rail_base_height:+rail_height:+1000);\n End_Point, Point((rail_width:/2)-(rail_wall_width:/2),0,rail_base_height:+rail_height:+1000);\n};\n\n(Child) line_10: {\n Class, ug_line;\n Start_Point, Point((rail_width:/2)-(rail_wall_width:/2),0,rail_base_height:+rail_height:+1000);\n End_Point, Point((rail_width:/2)-(rail_wall_width:/2),0,rail_base_height:+1000);\n};\n\n(Child) line_11: {\n Class, ug_line;\n Start_Point, Point((rail_width:/2)-(rail_wall_width:/2),0,rail_base_height:+1000);\n End_Point, Point(0,0,rail_base_height:+1000);\n};\n\n(Child) line_12: {\n Class, ug_line;\n Start_Point, Point(0,0,rail_base_height:+1000);\n End_Point, Point(0,0,1000);\n};\n\n"
    
    # TODO: Denne må fjernes for å ta hensyn til startpunkt og sluttpunkt
    #initial_rail = "(Child) rail_path_1: {\n Class, ug_line;\n Start_Point, Point(0,0,1000);\n End_Point, Point(0,100,1000);\n};\n\n"
    
    rail = "(child) rail_profile: {\nclass, ug_curve_join;\nprofile, {line_1:, line_2:, line_3:, line_4:,line_5:,line_6:,line_7:,line_8:,line_9:,line_10:,line_11:,line_12:};\n};\n\n(child) rail: {\nclass, ug_swept;\nguide, {{forward, rail_path:}};\nsection, {{forward, rail_profile:}};\nscaling, {scale_constant, 1};\nalignment_init, parameter;\norientation, {orientation_fixed};\ntolerances, {0, 0, 0};\n};\n\n(child) rail_colored: {\nclass, ug_body;\nfeature, {rail:};\nlayer, 1;\ncolor, ug_askClosestColor(RED);\n};\n\n"
    #rail_path - Bør nok legges til med feeding rails
    grid = "(Child) grid: {\n Class, ug_block;\n length, " + variable_to_DFA["grid_length"] + ";\n width, " + variable_to_DFA["grid_width"] + ";\n height, 0.01;\n origin, point(0,0,0);\n};\n\n"
    s = initial_lines + parameters + lines + rail + grid #  + initial_rail
    file = open("dfa_test.dfa", "w")
    file.write(s)
    file.close


obstacle_counter = 0

def obstacle_checker(position_x, position_y, width, length, grid_x, grid_y):
    if (position_x < 0) or (position_y < 0) or (width < 0) or (length < 0):
        print("Feil: Negativt parameter (obstacle)")
        return False
    if (position_x + length > grid_x) or (position_y + width > grid_y):
        print("Feil: Utenfor grid (obstacle)")
        return False
    return True
    
def update_obstacles(parameter_string, counter): 
    start_x = parameter_string.split("obstacle_position=")[1].split('%2C')[0]
    start_y = parameter_string.split('%2C')[1].split('&')[0]
    position = start_x + "," + start_y
    variable_to_DFA["obstacle_position"].append(position)

    width = parameter_string.split('obstacle_width=')[1].split('&')[0]
    variable_to_DFA["obstacle_width"].append(width)

    length = parameter_string.split('obstacle_length=')[1]
    variable_to_DFA["obstacle_length"].append(length)

    if not obstacle_checker(int(start_x),int(start_y),int(width),int(length),int(variable_to_DFA["grid_length"]),int(variable_to_DFA["grid_width"])):
        return

    global obstacle_counter
    obstacle_counter = counter + 1
    s = "(Child) obstacle_" + str(obstacle_counter) + ": {\n Class, ug_block;\n length, " + length + ";\n width, " + width + ";\n height, 2000;\n origin, point(" + position + ",0);\n};\n\n"
    file = open("dfa_test.dfa", "a")
    file.write(s)
    file.close
    

feeding_line_counter = 0

def feeding_line_checker(start_x, start_y, end_x, end_y, grid_x, grid_y): # Tar ikke hensyn til bjelkens bredde
    if (start_x < 0) or (start_y < 0) or (end_x < 0) or (end_y < 0):
        print("Feil: Negativt parameter (feeding rail)")
        return False
    if (start_x > grid_x) or (start_y > grid_y) or (end_x > grid_x) or (end_y > grid_y):
        print("Feil: Utenfor grid (feeding rail)")
        return False
    return True

def update_feeding_lines(parameter_string, counter):
    start_x = parameter_string.split('feeding_start=')[1].split('%2C')[0]
    start_y = parameter_string.split('%2C')[1].split('&')[0]
    start_position = start_x + "," + start_y
    variable_to_DFA["feeding_start"].append(start_position)

    end_x = parameter_string.split('feeding_end=')[1].split('%2C')[0]
    end_y = parameter_string.split('%2C')[2]
    end_position = end_x + "," + end_y
    variable_to_DFA["feeding_stop"].append(end_position)

    if not feeding_line_checker(int(start_x), int(start_y), int(end_x), int(end_y), int(variable_to_DFA["grid_length"]), int(variable_to_DFA["grid_width"])):
        return

    global feeding_line_counter
    feeding_line_counter = counter + 1
    rail_name = "feeding_rail_" + str(feeding_line_counter) + ":"
    variable_to_DFA["rail_path"].append(rail_name)
    s = "(Child) " + rail_name + " {\n Class, ug_line;\n Start_Point, Point(" + start_position + ",1000);\n End_Point, Point(" + end_position + ",1000);\n};\n\n"
    rail_path = rail_path_updater(variable_to_DFA["rail_path"]) # Skaper duplikat, men overstyrer tidligere versjoner
    rail_path_update = "(child) rail_path: {\nclass, ug_curve_join;\nprofile, {" + rail_path + "};\n};\n\n"
    file = open("dfa_test.dfa", "a")
    file.write(s)
    file.write(rail_path_update)
    file.close


def feeding_point_checker(x,y,grid_x,grid_y):
    if (x < 0) or (y < 0):
        print("Feil: Negativt parameter (feeding point)")
        return False
    if (x > grid_x) or (y > grid_y):
        print("Feil: Utenfor grid (feeding point)")
        return False
    return True

def update_feeding_points(parameter_string):
    point_x = parameter_string.split("feeding_point=")[1].split("%2C")[0]
    point_y = parameter_string.split('%2C')[1].split('&')[0]

    if not feeding_point_checker(int(point_x), int(point_y), int(variable_to_DFA["grid_length"]), int(variable_to_DFA["grid_width"])):
        return

    position = point_x + "," + point_y
    variable_to_DFA["feeding_points"].append(position)


def generate_path(start_point,list): # Tar inn liste med punkter, feeding points enn så lenge
    test = pathFinder()

    start = [int(variable_to_DFA["start_point"].split(",")[0]), int(variable_to_DFA["start_point"].split(",")[1])]

    test.set_start(start)
    for i in list:
        point = [int(i.split(",")[0]), int(i.split(",")[1])]
        test.set_target(point) 

    variable_to_DFA["path_points"] = test.analyze_points()


def railgenerator_to_dfa(target_list):
    radius = 2000 #as in the problem description
    s = "" 
    element_counter = 1

    print(target_list)

    for i in target_list:        
        #checking the list achieved after analyze_points() to
        if i[0] == 'line':
            element_name = "element_" + str(element_counter) + ":"
            s += "(Child) " + element_name + "{\nclass, ug_line;\nstart_point, point(" + str(i[1][0]) + "," + str(i[1][1]) + ",1000);\nend_point, point(" + str(i[2][0]) + "," + str(i[2][1]) + ",1000);\n};\n\n"
            variable_to_DFA["rail_path"].append(element_name)
            element_counter += 1

        elif i[0] == 'turn':
            #need to calculate angles from radians given from the list
            arc_start_angle = np.rad2deg(i[2])
            arc_end_angle = np.rad2deg(i[3])
            #converting to normal angle for the end angle if necessary
            if arc_start_angle > arc_end_angle:
                arc_end_angle = arc_end_angle + 360
            element_name = "element_" + str(element_counter) + ":"
            s += "(Child) " + element_name + "{\nclass, ug_arc;\ncenter, point(" + str(i[1][0]) + "," + str(i[1][1]) + ",1000);\nstart_angle, " + str(arc_start_angle) + ";\nend_angle, " + str(arc_end_angle) + ";\nradius, " + str(radius) + ";\n};\n\n"
            variable_to_DFA["rail_path"].append(element_name)
            element_counter += 1
        
        rail_path = rail_path_updater(variable_to_DFA["rail_path"]) # Skaper duplikat, men overstyrer tidligere versjoner
        rail_path_update = "(child) rail_path: {\nclass, ug_curve_join;\nprofile, {" + rail_path + "};\n};\n\n"

    file = open("dfa_test.dfa", "a")
    file.write(s)
    file.write(rail_path_update)
    file.close



def rail_path_updater(list): # Tar inn listen med rail-elementer fra dict, gjør dem om til en sammenhengende string
    s = ""
    for i in list:
        s += i + ","
    return s


# Handler of HTTP requests / responses


class MyHandler(BaseHTTPRequestHandler):

    # Function for displaying html file
    def write_HTML_file(self, filename):
        self.wfile.write(bytes(open(filename).read(), 'utf-8'))

    def do_GET(self):
        if self.path == '/' or self.path == "/orderRailSys":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)
        
        elif self.path.find('/addObstacle'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)
        elif self.path.find('/addFeedingLine'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)
        elif self.path.find('/addFeedingPoint'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.write_HTML_file(userinterface_file)
               
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("Error. The file " +
                                   self.path + " does not exist.", 'utf-8'))

    def do_POST(self):

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        if self.path.find("/orderRailwaySys") != -1:
            # Get the paramters
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            update_rail_system(param_line)          
            self.write_HTML_file(userinterface_file)
            # Update values in html files from param
            update_defaults(userinterface_file,
                            userinterface_tmp,
                            params)
            update_defaults(userinterface_file,
                            userinterface_error,
                            params)
            update_defaults(userinterface_file,
                            userinterface_order,
                            params)

        elif self.path.find("/addObstacle") != -1:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            update_obstacles(param_line, obstacle_counter)
            self.write_HTML_file(userinterface_addObstacle)    

        elif self.path.find("/addFeedingLine") != -1:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            update_feeding_lines(param_line, feeding_line_counter)
            self.write_HTML_file(userinterface_addFeedingLine)
        
        elif self.path.find("/addFeedingPoint") != -1:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            update_feeding_points(param_line)
            self.write_HTML_file(userinterface_addFeedingPoint)

        elif self.path.find("/submitRailSys") != -1:
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            generate_path(variable_to_DFA["start_point"], variable_to_DFA["feeding_points"])
            railgenerator_to_dfa(variable_to_DFA["path_points"])
            self.write_HTML_file(userinterface_generateRailSystem)


if __name__ == '__main__':

    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()