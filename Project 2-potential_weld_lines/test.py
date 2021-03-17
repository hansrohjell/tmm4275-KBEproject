

def read_DFA(dfa_template):
    # Open dfa template
    file = open(dfa_template)
    s = ""
    for line in file:
        s+= line # adding each line in a string.
        
    file.close()

    walls = s.split("\n\n") #walls[3] = wall1
    i = 0
    while i < (len(walls) - 3):
        #Splitte for å finne verdier
        wall = walls[i+3].split("; \n") #Mellomrom kan være mulig feilkilde ved ny maze

        length_param = wall[1].split(" ")
        length = length_param[2]
        #length.split(", ")

        width_param = wall[2].split(" ")
        width = width_param[2]
        #print(width)

        print("\n Wall " + str(i+1) + "\n Length: " + str(length) + "\n Width: " + str(width) + "\n")
        
        #originX =
        #originY =
        i +=1

    return s





read_DFA("testMaze.dfa")





"""

info = {}
with open('testMaze.dfa') as input_file:
    for line in input_file:
        wall, Length , width, origin = (
            item.strip() for item in line.split('\n', 3))
        info[wall] = dict(zip(('Length', 'width', 'origin'),
                                (Length, width, origin)))

print('Walls:')
for wall, record in info.items():
    print('  wall %r:' % wall)
    for field, value in record.items():
        print('    %s: %s' % (field, value))

# sample usage
player = 'Fizz'
print('\n%s had %s kills in the game' % (player, info[player]['stats']['kills']))

"""