import math as m
import numpy as np
from numpy.lib.scimath import arccos
from generatePath import pathFinder




def railgenerator_to_dfa(target_list):
    radius = 2000 #as in the problem description
    
    rail_list = []


    for i in target_list:
        
        #checking the list achieved after analyze_points() to 
        if i[0] == 'line':
            #TODO: add line to dfa
            rail_list.append([i[1], i[2]]) #adding start and end point
            pass
        elif i[0] == 'arc':

            #need to calculate angles from radians given from the list
            arc_start_angle = np.rad2deg(i[2])
            arc_end_angle = np.rad2deg(i[3])
            #converting to normal angle for the end angle if necessary
            if arc_end_angle < arc_start_angle:
                arc_end_angle += 360

            rail_list.append([i[1], radius, arc_start_angle, arc_end_angle])
    for j in rail_list:
        print(j)


#railgenerator_to_dfa(rail_list)
