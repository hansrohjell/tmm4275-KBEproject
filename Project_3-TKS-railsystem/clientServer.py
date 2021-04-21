from http.server import BaseHTTPRequestHandler, HTTPServer
from os import write
import re
from pathlib import Path
import math
from producibilityCheck import producibilityCheck
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
#image_file = Path("theProduct.png")

variable_to_DFA = {
    # Rail system
    "start_point": "0,0",
    "end_point": "0,0",    
    "grid_width": "50000", # Må være >> 100 pga bjelkens dimensjoner, 50 000?
    "grid_length": "50000",

    # Obstacle
    "obstacle_position": [],
    "obstacle_width": [],
    "obstacle_length": [],

    # Feeding rail
    "feeding_start": [],
    "feeding_stop": [],
    
    # Rail path - legger til elementer her ettersom rail-pathen forlenges, alle delene blir satt sammen og bygget opp som et I-profil
    "rail_path": ["rail_path_1"]
}

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

"""
def create_DFA(params, dfa_filename, dfa_template):
    # Open dfa template
    file = open(dfa_template)
    dfa_data = file.read()
    file.close()

    # Insert parameter values
    for param_pair in params:
        find = "<" + variable_to_DFA[param_pair[0]] + ">"
        dfa_data = dfa_data.replace(find, param_pair[1])

    # Write to new dfa file
    file = open(dfa_filename, "wt")
    file.write(dfa_data)
    file.close()
"""

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


def lock_and_order(filename):
    with open(filename, "r+") as file:
        data = file.read()
        find = 'input type="text"'
        replace = 'input readonly style="background-color:#80FF80;" type="text"'
        data = re.sub(find, replace, data)
        find = '<input type="submit" value="Check values">'
        replace = '<p>Chair is producible. </p><input type="submit" value="Create chair">'
        data = re.sub(find, replace, data)
        find = '</form>'
        replace = '</form><p></p><form action="/changeChair" method="post">\n<input type="submit" value="Re-enter values">\n</form>'
        data = re.sub(find, replace, data)
        find = 'orderChair'
        replace = 'submitChair'
        data = re.sub(find, replace, data)

        file.seek(0)
        file.write(data)
        file.truncate()
        
        
def update_rail_system(parameter_string):
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
    initial_rail = "(Child) rail_path_1: {\n Class, ug_line;\n Start_Point, Point(0,0,1000);\n End_Point, Point(0,100,1000);\n};\n\n"
    rail = "(child) rail_profile: {\nclass, ug_curve_join;\nprofile, {line_1:, line_2:, line_3:, line_4:,line_5:,line_6:,line_7:,line_8:,line_9:,line_10:,line_11:,line_12:};\n};\n\n(child) rail_path: {\nclass, ug_curve_join;\nprofile, {" + variable_to_DFA["rail_path"][0] + ":};\n};\n\n(child) rail: {\nclass, ug_swept;\nguide, {{forward, rail_path:}};\nsection, {{forward, rail_profile:}};\nscaling, {scale_constant, 1};\nalignment_init, parameter;\norientation, {orientation_fixed};\ntolerances, {0, 0, 0};\n};\n\n(child) rail_colored: {\nclass, ug_body;\nfeature, {rail:};\nlayer, 1;\ncolor, ug_askClosestColor(RED);\n};\n\n"
    #rail_path - Bør nok legges til med feeding rails
    grid = "(Child) grid: {\n Class, ug_block;\n length, " + variable_to_DFA["grid_length"] + ";\n width, " + variable_to_DFA["grid_width"] + ";\n height, 0.01;\n origin, point(0,0,0);\n};\n\n"
    s = initial_lines + parameters + lines + initial_rail + rail + grid
    file = open("dfa_test.dfa", "w")
    file.write(s)
    file.close


obstacle_counter = 0    
    
def update_obstacles(parameter_string, counter): 
    start_x = parameter_string.split("obstacle_position=")[1].split('%2C')[0]
    start_y = parameter_string.split('%2C')[1].split('&')[0]
    position = start_x + "," + start_y
    variable_to_DFA["obstacle_position"].append(position)

    width = parameter_string.split('obstacle_width=')[1].split('&')[0]
    variable_to_DFA["obstacle_width"].append(width)

    length = parameter_string.split('obstacle_length=')[1]
    variable_to_DFA["obstacle_length"].append(length)
    
    global obstacle_counter
    obstacle_counter = counter + 1
    s = "(Child) obstacle" + str(obstacle_counter) + ": {\n Class, ug_block;\n length, " + length + ";\n width, " + width + ";\n height, 2000;\n origin, point(" + position + ",0);\n};\n\n"
    file = open("dfa_test.dfa", "a")
    file.write(s)
    file.close

    
feeding_line_counter = 0    

def update_feeding_lines(parameter_string, counter):
    start_x = parameter_string.split('feeding_start=')[1].split('%2C')[0]
    start_y = parameter_string.split('%2C')[1].split('&')[0]
    start_position = start_x + "," + start_y
    variable_to_DFA["feeding_start"].append(start_position)

    end_x = parameter_string.split('feeding_end=')[1].split('%2C')[0]
    end_y = parameter_string.split('%2C')[2]
    end_position = end_x + "," + end_y
    variable_to_DFA["feeding_stop"].append(end_position)
    
    global feeding_line_counter
    feeding_line_counter = counter + 1
    s = "" #TODO: Sett inn ug_line her, bygges senere til rail med railpath
    file = open("dfa_test.dfa", "a")
    file.write(s)
    file.close


# def set_error_message(min, max, variable, error_filename):
#       # Sets the default values in html file
#     file = open(error_filename)
#     data = file.read()
#     file.close()
#     find = 'name="' + variable[0] + '"' + ' value=".*?">'
#     # name="cdepth" value="123456"><br>
#     replace = 'style="background-color:#FF0000;" name="' + variable[0] + '"' + ' value="' + \
#         variable[1] + '">' + \
#         " Please insert a value between " + \
#         str(round(min)) + " and " + str(round(max))
#     data = re.sub(find, replace, data)
#     file = open(error_filename, "wt")
#     file.write(data)
#     file.close()


def add_error_messages(error_messages, error_filename):
    file = open(error_filename)
    data = file.read()
    file.close()
    for param, message in error_messages.items():
        find = 'name="' + param + '"' + ' value=".*?">'
        replace = 'style="background-color:#FF0000;" name="' + param + '"' + ' value="' + \
            str(round(message[1])) + '">' + message[0]
        data = re.sub(find, replace, data)
    file = open(error_filename, "wt")
    file.write(data)
    file.close()


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

            # Check for illegal parameter
            #not_producible, error_message = producibilityCheck(params)

            # html interface to show
            """
            if not_producible:
                # Add error message to html
                add_error_messages(error_message, userinterface_error)
                self.write_HTML_file(userinterface_error)

                lock_and_order(userinterface_order)
                self.write_HTML_file(userinterface_order)
            """
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
            update_feeding_lines(param_line, feeding_rail_counter)
            self.write_HTML_file(userinterface_addFeedingLine)



        """
        elif self.path.find("/submitGrid") != -1:
            # Get the paramters
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            param_line = post_body.decode()
            params = parse_parameters(param_line)
            create_DFA(params, "user_chair.dfa",
                       dfa_template)
            self.write_HTML_file(userinterface_file)
            self.wfile.write(bytes('<script>', 'utf-8'))
            self.wfile.write(bytes('function myFunction() {', 'utf-8'))
            self.wfile.write(bytes('var txt;', 'utf-8'))
            self.wfile.write(
                bytes('var r = confirm("Chair created!");', 'utf-8'))
            self.wfile.write(bytes('}', 'utf-8'))
            self.wfile.write(bytes('myFunction()', 'utf-8'))
            self.wfile.write(bytes('</script>', 'utf-8'))
            # self.wfile.write(bytes('<img src="theProduct.png" alt="The product comes here" width="800" height="420">', 'utf-8'))
        elif self.path.find("/changeChair") != -1:
            self.write_HTML_file(userinterface_tmp)
"""

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
