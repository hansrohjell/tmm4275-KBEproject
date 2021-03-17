

def read_DFA(dfa_template):
    # Open dfa template
    file = open(dfa_template)
    s = ""
    for line in file:
        s+= line # adding each line in a string.
        
    file.close()
    return s





s = read_DFA("testMaze.dfa")
print(s)