import sys, os
from matplotlib import  pyplot as plt
import vedo 
import numpy as np

dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir, 'src')
sys.path.append(os.path.abspath(dir))
print(dir)

from BaseDigitalTwin import BaseDigitalTwin
from beam import Beam
from bezier import Bezier

if __name__ == '__main__':
    """
        Given sampled points from the centerlines, this plots quaternions at each point, 
            -> Blue: tangent 
            -> Red: Normals 
            -> Green: Binormals
    """


    # Input mesh 
    mesh = "../data/mesh/processed_porteveine.stl"

    # Input text file where centerlines will be stored
    skeleton_file = "../data/skeleton/output_skeleton.txt"

    # Structuring centerlines into a list of polylines 
    basedt = BaseDigitalTwin()
    basedt.get_centerlines(mesh, skeleton_file)
    vessel = basedt.getSkeletonData(skeleton_file)

    # Plotting specifications
    fig = plt.figure(figsize=(20, 15))
    ax = fig.add_subplot(projection='3d')
    ax.set_xlabel('axe X')
    ax.set_ylabel('axe Y')
    ax.set_zlabel('axe Z')

    # Iterating on each branch of the vessel
    for branch in vessel: 

        # Using the Beam class, we approximate a bezier curve on the centerlines and sampe points each 0.005 
        beam = Beam(branch, 0.005)
        sample = beam.sample

        # Tangents, normals and binormals are computed using the analytical expression of the Bezier Curve
        tangentes = Bezier(sample).get_tangentes()
        normals = Bezier(sample).get_normals(tangentes)
        binomials = Bezier(sample).get_binormals(tangentes, normals)

        # Plotting the vectors 
        for i in range(len(sample)):

            # Tangents
            ax.quiver(sample[i][0], sample[i][1], sample[i][2], 
                        tangentes[i][0], tangentes[i][1], tangentes[i][2], 
                        length=0.006, arrow_length_ratio=0.004, color='blue')
            # Normals
            ax.quiver(sample[i][0], sample[i][1], sample[i][2], 
                        normals[i][0], normals[i][1], normals[i][2], 
                        length=0.006, arrow_length_ratio=0.004, color='red')
            # Binormals
            ax.quiver(sample[i][0], sample[i][1], sample[i][2], 
                        binomials[i][0], binomials[i][1], binomials[i][2], 
                        length=0.006, arrow_length_ratio=0.004, color='green')

    # Plot
    plt.show()

        

        
