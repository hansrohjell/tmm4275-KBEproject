def line_generator(length, width, originX, originY, iterator):
    counter = 4 * iterator
    #Regne ut koordinater her? Blir appendet i neste linje
    weldLines = "(Child) line_"+str(counter+1)+": {\n Class, ug_line; \n Start_Point, Point("+str(int(originX))+", "+str(int(originY))+", fZ:); \n End_Point, Point("+str(int(originX+length))+", "+str(int(originY))+", fZ:); \n};\n\n(Child) line_"+str(counter+2)+": {\n Class, ug_line; \n Start_Point, Point("+str(int(originX+length))+", "+str(int(originY))+", fZ:); \n End_Point, Point("+str(int(originX+length))+", "+str(int(originY+width))+", fZ:); \n};\n\n(Child) line_"+str(counter+3)+": {\n Class, ug_line; \n Start_Point, Point("+str(int(originX+length))+", "+str(int(originY+width))+", fZ:); \n End_Point, Point("+str(int(originX))+", "+str(int(originY+width))+", fZ:); \n};\n\n(Child) line_"+str(counter+4)+": {\n Class, ug_line; \n Start_Point, Point("+str(int(originX))+", "+str(int(originY+width))+", fZ:); \n End_Point, Point("+str(int(originX))+", "+str(int(originY))+", fZ:); \n};\n\n"
    fileString = ""
    fileString += weldLines    
    return fileString
    

def read_DFA(dfa_template):
    # Open dfa template
    file = open(dfa_template)
    s = ""
    for line in file:
        s+= line # adding each line in a string.
        
    file.close()

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
        
        weldLines = line_generator(length, width, originX, originY, i)
        s += weldLines
        
        i += 1
                     
    file.write(s) # Hvordan endre navn på filen? Nødvendig?    
    file.close()


read_DFA("testMaze.dfa")