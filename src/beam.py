import numpy as np
from pyquaternion import Quaternion
import math


from bezier import Bezier


class Beam: 
    """
    Data structure for a Beam
    :branche : a list of points 
    :sampling_rate : desired distance between two points in the branch
    """
    #Initializer
    def __init__(self, branche, sampling_rate):
        self.branche = branche
        self.sampling_rate = sampling_rate
        self.sample = self.get_sample()
        self.vertices = self.get_vertices()
        self.num_nodes = len(self.sample)


    def get_topology(self): 
        """ 
        Get the topology of the beam
        """ 
        longuer = len(self.sample)

        topology = ""
        for i in range(longuer-1): 
            topology += str(i) + " " + str(i+1) + " "

        return topology
    

    def get_sample(self): 
        """ 
        Sampling the beam, according to the choosed sampling rate 
        """ 
        sample = []
        branche = self.branche
        next_value = branche[0]
        sampler = self.sampling_rate
        sample.append(next_value)
        for i in range(1, len(self.branche)):
            next_value = self.branche[i]
            norm = self.get_distance(sample[len(sample)-1], next_value)
            if norm >= sampler:
                sample.append(next_value)

        for i in range(len(sample)-1): 
            distance = self.get_distance(sample[i], sample[i+1])
            if distance <= 0.5*sampler: 
                del sample[i+1]
        
        if branche[-1] not in sample: 
            sample.append(branche[-1])
        return sample

    
    def get_norm(self, point):
        """ 
        Computes norm 2
        """ 
        return math.sqrt(np.power(point[0], 2) + np.power(point[1], 2) + np.power(point[2], 2))
    
    def get_distance(self, point1, point2):
        """ 
        Computes distant between two points
        """ 
        point = [point1[0] - point2[0], point1[1] - point2[1], point1[2] - point2[2]]
        return self.get_norm(point)
    

    def get_list_of_xyz(self):
        """
        Get list of coordonates
        """
        list_of_x, list_of_y, list_of_z = [], [], []
        for point in self.sample:
            list_of_x.append(point[0])
            list_of_y.append(point[1])
            list_of_z.append(point[2])

        return list_of_x, list_of_y, list_of_z

    
    def get_quaternion(self, tangente, normal, binormal):
        """
        Get The quaternion given a rotation matrix,
        This function should be added to a Helper
        """
        rotation = np.array([
                            [tangente[0], normal[0], binormal[0]],
                            [tangente[1], normal[1], binormal[1]], 
                            [tangente[2], normal[2], binormal[2]]
                            
                        ])

        quaternion = Quaternion(matrix=rotation)

        return quaternion


    
    def get_MO_rigid(self): 
        """
        Compute the Mechanical Object string of the branch: positions + rotations(represented as a quaternion)
        """
        sampled_data = self.sample
        MO = ""

        bezier = Bezier(sampled_data)
        try:
            tangentes = bezier.get_tangentes()
        except:
            print("--- Brache ---")
            print(self.branche)
            print("--- Sampled ---")
            print(sampled_data)
            print("-----")
            
        normals = bezier.get_normals(tangentes)
        binormals = bezier.get_binormals(tangentes, normals)

        list_of_x, list_of_y, list_of_z = self.get_list_of_xyz()

        if not (len(tangentes) == len(normals) and len(normals) == len(binormals)): 
            print("Error: Index out of range, len of tangentes, normals and binormals are not equal")
        else: 
            longueur = len(tangentes)
            for i in range(longueur): 
                quaternion = self.get_quaternion(tangentes[i], normals[i], binormals[i])
                
                quat_i_0 = quaternion[1]
                quat_i_1 = quaternion[2]
                quat_i_2 = quaternion[3]
                quat_i_3 = quaternion[0]

                MO += str(list_of_x[i]) + " " + str(list_of_y[i]) + " " + str(list_of_z[i]) + " " + str(quat_i_0) + " " + str(quat_i_1) + " " + str(quat_i_2) + " " + str(quat_i_3) + " "
        return MO

    
    def get_MO_vec(self): 
        """
        Compute the Mechanical Object string of the branch: only the positions
        """
        
        MO = ""
        list_of_x, list_of_y, list_of_z = self.get_list_of_xyz()

        for i in range(len(list_of_x)): 

            MO += str(list_of_x[i]) + " " + str(list_of_y[i]) + " " + str(list_of_z[i]) + " " 
        return MO
    
    def get_vertices(self):
        """ 
        Get the coordonates of the beam vertices
        """
        return  [self.sample[0], self.sample[-1]]
    

    def get_index_bif(self, bif): 
        """
        Geting the index of the bifurcation
        """
        if bif not in self.sample: 
            print("Error: Bifurcation not in branche")
            return
        else: 
            for i in range(len(self.sample)): 
                if self.sample[i] == bif: 
                    return str(i)
    
    
    def get_box_coordonates(self): 
        """
        Geting the box ROI coordinates: the bounding box of a branch
        """
        sample = self.sample
        first = sample[0]
        end = sample[-1]

        min_x = first[0]
        min_y = first[1]
        min_z = first[2]

        max_x = end[0]
        max_y = end[1]
        max_z = end[2]

        for element in sample: 
            if element[0] <= min_x: 
                min_x = element[0]
            if element[0] >= max_x: 
                max_x = element[0]

            if element[1] <= min_y: 
                min_y = element[1]
            if element[1] >= max_y: 
                max_y = element[1]

            if element[2] <= min_z: 
                min_z = element[2]
            if element[2] >= max_z: 
                max_z = element[2]
        slicing = 0.001
        box = str(min_x-slicing) + " " + str(min_y-slicing) + " " + str(min_z-slicing) + " " + str(max_x+slicing) + " " + str(max_y+slicing) + " " + str(max_z+slicing) + " "

        return box
                