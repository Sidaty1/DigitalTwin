import numpy as np
import random

# Input Mesh: Obj/VTK or other 
mesh = "./data/mesh/vessels_refined.obj"

# Input text file where centerlines will be stored
skeleton_file = "./data/skeleton/output_skeleton.txt"

class Bezier: 
    """
    This class process a list of points in order to approximate 
    a Bezier Cubic curve, it also computes the tangentes, normals 
    and binormals at each point
    """
    
    def __init__(self, points):
        # Initializer
        self.points = points

    def get_bezier_coef(self):
        """
        Gets the Control points coefficients
        """
        points = self.points
        n = len(points) - 1

        C = 4 * np.identity(n) 
        np.fill_diagonal(C[1:], 1)
        np.fill_diagonal(C[:, 1:], 1)
        C[0, 0] = 2
        C[n - 1, n - 1] = 7
        C[n - 1, n - 2] = 2
        
        P = []
        for i in range(0, n):
            tmp = [4*points[i][0] + 2*points[i+1][0], 4*points[i][1] + 2*points[i+1][1], 4*points[i][2] + 2*points[i+1][2]]
            P.append(tmp)
        
        P[0] = [points[0][0] + 2*points[1][0], points[0][1] + 2*points[1][1], points[0][2] + 2*points[1][2]]
        P[n - 1] = [8*points[n - 1][0] + points[n][0], 8*points[n - 1][1] + points[n][1], 8*points[n - 1][2] + points[n][2]]

        P = np.asarray(P)


        A = np.linalg.solve(C, P)
        B = []
        for i in range(n):
            B.append([0, 0, 0])

        for i in range(n - 1):
            B[i] = [2*points[i+1][0] - A[i+1][0], 2*points[i+1][1] - A[i+1][1], 2*points[i+1][2] - A[i+1][2]]
        B[n - 1] = [(A[n-1][0] + points[n][0])/2, (A[n - 1][1] + points[n][1])/2, (A[n - 1][2] + points[n][2])/2]

        return A, B

    def get_bezier_cubic(self):
        """
        Gets coordonates at x y and z
        """
        points = self.points
        A, B = self.get_bezier_coef()

        list_x = [self.get_cubic_x(points[i], A[i], B[i], points[i + 1]) for i in range(len(points) - 1)]
        list_y = [self.get_cubic_y(points[i], A[i], B[i], points[i + 1]) for i in range(len(points) - 1)]
        list_z = [self.get_cubic_z(points[i], A[i], B[i], points[i + 1]) for i in range(len(points) - 1)]
        
        return list_x, list_y, list_z
    

    def evaluate_bezier(self, n):
        """
        Evaluate a bezier curve at a point
        """
        list_x, list_y, list_z = self.get_bezier_cubic()
        
        list_x = np.array([fun(t) for fun in list_x for t in np.linspace(0, 1, n)])
        list_y = np.array([fun(t) for fun in list_y for t in np.linspace(0, 1, n)])
        list_z = np.array([fun(t) for fun in list_z for t in np.linspace(0, 1, n)])

        return list_x, list_y, list_z
    

    def derivee_bernstein(self, a, b, c, d, t):
        """
        This function defines the derivate of a Bernstein cubic polynomial
        """
        return -3*np.power(1-t, 2)*a + 3*np.power(1-t, 2)*b -6*t*(1-t)*b + 6*t*(2-3*t)*c +3*np.power(t, 2)*d
    
    def get_cubic_x(self, a, b, c, d):
        """
        This function defines the Bernstein polynome of X
        """
        return lambda t: np.power(1 - t, 3) * a[0] + 3 * np.power(1 - t, 2) * t * b[0] + 3 * (1 - t) * np.power(t, 2) * c[0] + np.power(t, 3) * d[0]
    

    def get_cubic_y(self, a, b, c, d):
        """
        This function defines the Bernstein polynome of Y 
        """
        return lambda t: np.power(1 - t, 3) * a[1] + 3 * np.power(1 - t, 2) * t * b[1] + 3 * (1 - t) * np.power(t, 2) * c[1] + np.power(t, 3) * d[1]
    

    def get_cubic_z(self, a, b, c, d):
        """
        This function defines the Bernstein polynome of Z
        """
        return lambda t: np.power(1 - t, 3) * a[2] + 3 * np.power(1 - t, 2) * t * b[2] + 3 * (1 - t) * np.power(t, 2) * c[2] + np.power(t, 3) * d[2]
    

    def get_derivee_cubic(self, a, b, c, d, t):
        """
        This function evaluates the derivate at a point
        """
        return -3*np.power(1-t, 2)*a + 3*np.power(1-t, 2)*b -6*t*(1-t)*b + 3*t*(2-3*t)*c +3*np.power(t, 2)*d

   
    def tangenteAnalytic(self, index):
        """
        This function computes the analytical tangente at a given point
        It evalutes the derivate at x, y and z
        """
        points = self.points
        A, B = self.get_bezier_coef()

        if index == len(points)-1:
            A_index = A[index-1]
            B_index = B[index-1]

            point1 = points[index-1]
            point2 = points[index]

            tan_coord_x = self.get_derivee_cubic(point1[0], A_index[0], B_index[0], point2[0], 1)
            tan_coord_y = self.get_derivee_cubic(point1[1], A_index[1], B_index[1], point2[1], 1)
            tan_coord_z = self.get_derivee_cubic(point1[2], A_index[2], B_index[2], point2[2], 1)


            tangente = np.asarray([tan_coord_x, tan_coord_y, tan_coord_z])
            tangente = tangente/np.linalg.norm(tangente)
        else:
            A_index = A[index]
            B_index = B[index]

            point1 = points[index]
            point2 = points[index+1]

            tan_coord_x = self.get_derivee_cubic(point1[0], A_index[0], B_index[0], point2[0], 0)
            tan_coord_y = self.get_derivee_cubic(point1[1], A_index[1], B_index[1], point2[1], 0)
            tan_coord_z = self.get_derivee_cubic(point1[2], A_index[2], B_index[2], point2[2], 0)

            tangente = np.asarray([tan_coord_x, tan_coord_y, tan_coord_z])
            tangente = tangente/np.linalg.norm(tangente)

        return tangente
    
    def get_tangentes(self):
        """
        Getting the tangentes at a set of points
        """        

        points = self.points
        tangentes = []
        for i in range(len(points)):
            tangente = self.tangenteAnalytic(i)
            tangentes.append(tangente)
        return tangentes
    

    def AreCollinear(self, vector1, vector2):

        """
        Testing if two vectors are collinear, 
        
        this function should be mooved to a Helper
        """
        res = np.cross(vector1, vector2)
        if abs(res[0] + res[1] + res[2]) < 1e-10:
            return True
        return False
    

    def get_non_collinaire_vector(self, tangente):
        """
        This function generate a non collinear vector
        
        Also should be mooved to a Helper
        
        """
        found = False
        while(not found):
            
            x = random.random()
            y = random.random()
            z = random.random()

            vect = [x, y, z ]
            vect = vect/np.linalg.norm(vect)

            cross = np.cross(tangente, vect)
            
            if not self.AreCollinear(tangente, vect):
                found = True

        return cross
    
    def get_normals(self, tangentes):
        """
        Getting the normals, given a set of tangents, 
        we generate a set of non collinear vectors and 
        apply the cross product
        """
        non_collinaire = self.get_non_collinaire_vector(tangentes[0])

        normals = []
        for tangente in tangentes:
            normal = np.cross(tangente, non_collinaire)
            normal = normal/np.linalg.norm(normal)

            normals.append(normal)

        return normals
    

    def get_binormals(self, tangentes, normals):
        """
        Getting the binormals, given the tangents and the normals 
        We apply the cross product
        """
        binormals = []

        if len(tangentes) != len(normals):
            print("Error: Index out of range, tangentes and Normals sizes are not equal")
            return
        else: 
            for i in range(len(tangentes)):
                binormal = np.cross(tangentes[i], normals[i])
                binormal = binormal/np.linalg.norm(binormal)
                binormals.append(binormal)

            return binormals