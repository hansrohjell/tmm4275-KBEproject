from os import error
import numpy as np
import math as m


#Class for finding path via points 
#Using a heuristic algorithm to find the path and
#Missing obstacle avoidance and not sure if optimal path is found.
#Also in need of feeding line

class pathFinder():
    
    def __init__(self):
        super(pathFinder, self).__init__()
        self.start_point = []
        self.path = []
        self.visiting_points = []
        self.min_radius_turn = 2000 # Minimum possible turning radius [mm]

        self.construction_lines = []
        self.construction_arcs = []


    #Function for finding the path with given points
    def analyze_points(self):
        self.construct_lines()
        self.arc_center()
        self.pathGenerator()

    def set_start(self, point): #setting start point for the path.
        self.start_point.append(point)

    def set_target(self, point):
        self.visiting_points.append(point) #points that the rail needs to visit.

    #function for appending the construction lines
    def construct_lines(self):
        lines = []
        points = self.start_point + self.visiting_points
        #print(points)
        for k, p in enumerate(points):
            try:
                #print(p)
                lines.append([p, points[k+1]])
            except Exception as e:
                error
        self.construction_lines = lines
        #print(lines)


    #function for finding direction vector when given two points
    def direction_vector(self, a, b):
        dir_vec = [b[0]-a[0], b[1]-a[1]]
        return dir_vec

    #Function for calculating angle of line when turning
    def angle_of_line(self, line):
        dir = [line[1][0] - line[0][0], line[1][1] - line[0][1]]

        if dir[0] != 0:
            phi = m.atan(dir[1]/dir[0]) #atan(x/y)
        else:
            phi = m.pi/2
        return phi

    def circle_point(self, center, rad):
        radius = self.min_radius_turn
        point = [radius*m.cos(rad) + center[0], radius*m.sin(rad) + center[1]]
        return point


    def find_distance(self, a, b):
        dist = m.sqrt(a**2 + b**2)
        return dist

    def pathGenerator(self):
        lines = self.construction_lines
        arcs = self.construction_arcs

        prev_line_dir = m.pi/2

        for i in range(len(lines)):
            curr_line = lines[i]
            print("Curr line:")
            print(curr_line)
            curr_line_dir = self.angle_of_line(curr_line)
            
            if i > 0:
                prev_line = lines[i-1]
                prev_line_dir = self.angle_of_line(prev_line)
            
            
            if i < len(lines) - 1:
                nxt_line = lines[i + 1]
                nxt_line_dir = self.angle_of_line(nxt_line)
                
                if nxt_line_dir < curr_line_dir:
                    next_turn = 1
                else: 
                    next_turn = -1
            else:
                nxt_line = False
                nxt_line_dir = False
                next_turn = 0

            curr_arc_center = arcs[i][0]

            try:
                nxt_arc_center = arcs[i+1][0]
                arc_to_arc_direction = self.direction_vector(curr_arc_center, nxt_arc_center)
                arc_to_arc_angle = self.angle_of_line([curr_arc_center, nxt_arc_center])
            except Exception as e:
                nxt_arc_center = False
                arc_to_arc_direction = False
                arc_to_arc_angle = False

            
            if curr_line_dir > prev_line_dir:
                current_direction = -1 #left
                if i == 0:
                    prev_arc_tan_angle = 0
            else:
                current_direction = 1 #right
                if i == 0:
                    prev_arc_tan_angle = m.pi

            #current_turn = 0 means center.

            #Cases for the different scenarios of steps
            if current_direction == -1 and next_turn == 1:
                arc_to_arc_dir_mid = [arc_to_arc_direction[0]/2,arc_to_arc_direction[1]/2]
                arc_to_arc_dir_mid_distance = self.find_distance(arc_to_arc_dir_mid[0],arc_to_arc_dir_mid[1])

                phi = m.acos(self.min_radius_turn / arc_to_arc_dir_mid_distance)

                current_tangent_angle = arc_to_arc_angle - phi
                next_tangent_angle = arc_to_arc_angle + m.pi - phi

                tangent_point_a = self.circle_point(curr_arc_center,current_tangent_angle)
                tangent_point_b = self.circle_point(nxt_arc_center,next_tangent_angle)

                self.path.append(['turn',curr_arc_center, prev_arc_tan_angle, current_tangent_angle])
                
                prev_arc_tan_angle = next_tangent_angle

            elif current_direction == 1 and next_turn == -1:
                arc_to_arc_dir_mid = [arc_to_arc_direction[0]/2,arc_to_arc_direction[1]/2]
                arc_to_arc_dir_mid_distance = self.find_distance(arc_to_arc_dir_mid[0],arc_to_arc_dir_mid[1])

                
                phi = m.acos(self.min_radius_turn / arc_to_arc_dir_mid_distance)

                current_tangent_angle = arc_to_arc_angle + phi
                next_tangent_angle = arc_to_arc_angle + m.pi + phi

                tangent_point_a = self.circle_point(curr_arc_center,current_tangent_angle)
                tangent_point_b = self.circle_point(nxt_arc_center,next_tangent_angle)

                self.path.append(['turn',curr_arc_center, current_tangent_angle, prev_arc_tan_angle])
                prev_arc_tan_angle = next_tangent_angle

               

            elif current_direction == -1 and next_turn == -1:
                tangent_angle = arc_to_arc_angle - (m.pi/2)
                tangent_point_a = self.circle_point(curr_arc_center, tangent_angle)
                tangent_point_b = self.circle_point(nxt_arc_center, tangent_angle)

                self.path.append(['turn',curr_arc_center, prev_arc_tan_angle, tangent_angle])
                prev_arc_tan_angle = tangent_angle

                

            elif current_direction == 1 and next_turn == 1:
                tangent_angle = arc_to_arc_angle + (m.pi/2)
                tangent_point_a = self.circle_point(curr_arc_center, tangent_angle)
                tangent_point_b = self.circle_point(nxt_arc_center, tangent_angle)

                self.path.append(['turn',curr_arc_center, tangent_angle, prev_arc_tan_angle])
                prev_arc_tan_angle = tangent_angle
                

            elif current_direction == 1 and next_turn == 0:

                arc_to_goal_direction = self.direction_vector(curr_arc_center, curr_line[1])
                arc_to_goal_direction_distance = self.find_distance(arc_to_goal_direction[0], arc_to_goal_direction[1])

                arc_to_goal_angle = self.angle_of_line([curr_arc_center, curr_line[1]])
                
                
                phi = m.acos(self.min_radius_turn / arc_to_goal_direction_distance)
                tangent_angle = arc_to_goal_angle + phi
                tangent_point_a = self.circle_point(curr_arc_center, tangent_angle)
                tangent_point_b = curr_line[1]

                self.path.append(['turn',curr_arc_center, tangent_angle, prev_arc_tan_angle])
                prev_arc_tan_angle = tangent_angle


            elif current_direction == -1 and next_turn == 0:

                arc_to_goal_direction = self.direction_vector(curr_arc_center, curr_line[1])
                arc_to_goal_direction_distance = self.find_distance(arc_to_goal_direction[0],arc_to_goal_direction[1])

                arc_to_goal_angle = self.angle_of_line([curr_arc_center, curr_line[1]])

                phi = m.acos(self.min_radius_turn / arc_to_goal_direction_distance)

                tangent_angle = arc_to_goal_angle - phi
                tangent_point_a = self.circle_point(curr_arc_center, tangent_angle)
                tangent_point_b = curr_line[1]

                self.path.append(['turn',curr_arc_center, prev_arc_tan_angle, tangent_angle])
                prev_arc_tan_angle = tangent_angle

                

            self.path.append(['line',tangent_point_a, tangent_point_b])
            

    #finding center for arcs which lies in middle of two lines, and has a distance of R from the intercection point for creating turns.
    def arc_center(self):
        lines = self.construction_lines
        for k, line in enumerate(lines):
            rad = self.min_radius_turn
            intersect = lines[k][0]

            if k > 0:
                ref_direct = [intersect[0] + 1, intersect[1]]
                ref_direct_ = [intersect[0], intersect[1]-1]

                ref_angle_1 = self.angle_from_center(intersect, lines[k-1][0], ref_direct)
                ref_angle_1_ = self.angle_from_center(intersect, lines[k-1][0], ref_direct_)

                ref_angle_2 = self.angle_from_center(intersect, lines[k][1], ref_direct)
                ref_angle_2_ = self.angle_from_center(intersect, lines[k][1], ref_direct_)

                #if line is below the half circle in angle and points "downward"
                if ref_angle_1_ < m.pi/2:
                    ref_angle_1 = m.pi*2 - ref_angle_1
                if ref_angle_2_ < m.pi/2:
                    ref_angle_2 = m.pi*2 - ref_angle_2

                global_angleOfCenter = (ref_angle_1 + ref_angle_2)

                center = [rad * m.cos(global_angleOfCenter) + intersect[0], rad * m.sin(global_angleOfCenter) + intersect[1]]
                self.construction_arcs.append([center, intersect])

            else:
                #TODO: kommenter her
                if line[1][0] > 0:
                    self.construction_arcs.append([[rad, 0], intersect])
                elif line[1][0] < 0:
                    self.construction_arcs.append([[-rad, 0], intersect])

    def angle_from_center(self, center, a, b):
        v = [a[0] - center[0], a[1] - center[1]]
        w = [b[0] - center[0], b[1] - center[1]]

        magnitude_v = v/ np.linalg.norm(v)
        magnitude_w = w/np.linalg.norm(w)
        point_product = np.dot(magnitude_v, magnitude_w)
        angle = np.arccos(point_product)
        return angle

    def length_of_Vector(self, vector):
        magnitude = m.sqrt(vector[0]**2 + vector[1]**2)
        return magnitude

    def line_vector(self, line):
        vector = []
        # slow code.. would probably execute a lot faster with numpy
        for val_1, val_2 in zip(line[0], line[1]):
            vector.append(val_1-val_2)
        return vector



    """ Not finished!

    def obstacle_avoidance(self, obstacles, path):
        new_path = []

        if obstacles:
            for p in path:
                pass

        else:
            return path
        
        return new_path

    """

        

    


if __name__ == '__main__':


    
    test = pathFinder()
    test.set_start([0,0]) # start point
    test.set_target([5000,5000])
    test.set_target([10000, 10000])
    test.set_target([0,15000])
    test.set_target([0,10000])
    test.analyze_points() #run the path analyzer

    for a in test.path:
        print(a)
