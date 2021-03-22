def line_generator(length, width, originX, originY, iterator):
    counter = 4 * iterator
    dx = originX + length
    dy = originY + width
    weldLines = "(Child) line_"+str(counter+1)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX)+", "+str(originY)+", fZ:); \n End_Point, Point("+str(dx)+", "+str(originY)+", fZ:); \n};\n\n(Child) line_"+str(counter+2)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx)+", "+str(originY)+", fZ:); \n End_Point, Point("+str(dx)+", "+str(dy)+", fZ:); \n};\n\n(Child) line_"+str(counter+3)+": {\n Class, ug_line; \n Start_Point, Point("+str(dx)+", "+str(dy)+", fZ:); \n End_Point, Point("+str(originX)+", "+str(dy)+", fZ:); \n};\n\n(Child) line_"+str(counter+4)+": {\n Class, ug_line; \n Start_Point, Point("+str(originX)+", "+str(dy)+", fZ:); \n End_Point, Point("+str(originX)+", "+str(originY)+", fZ:); \n};\n\n"
    fileString = ""
    fileString += weldLines    
    return fileString
 
def read_DFA(dfa_template):
    # Open dfa template
    file = open(dfa_template)
    s = ""
    for line in file:
        s += line # adding each line in a string.
        
    file.close()

    file = open("weldedMaze.dfa", "w")
         
    s = s.replace(dfa_template[:-4], "weldedMaze") #Rename new file
     
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

read_DFA("testMaze.dfa")
