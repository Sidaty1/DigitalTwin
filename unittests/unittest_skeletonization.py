import sys, os
import random
import vedo 
import numpy as np 

dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir, 'src')
sys.path.append(os.path.abspath(dir))
print(dir)

from BaseDigitalTwin import BaseDigitalTwin

if __name__ == '__main__':
    """
        This code generates the centerlines of a given mesh, it plots the centerlines. 
    """

    # Input Mesh: Obj/VTK or other 
    #mesh = "../data/mesh/vessels_refined.obj"
    mesh = "../data/mesh/processed_porteveine.stl"
    # Input text file where centerlines will be stored
    skeleton_file = "../data/skeleton/output_skeleton.txt"

    print("Plotting: ")
    print("1 - Only centerlines ")
    print("Other - Mesh and its centerlines ")

    PlotMesh = input()
    PlotMesh = (PlotMesh != str(1))

    # Storing the centeralines in the given text file 
    basedt = BaseDigitalTwin()
    basedt.get_centerlines(mesh, skeleton_file)
    # Structuring centerlines into a list of polylines 
    vessel = basedt.getSkeletonData(skeleton_file)

    # Loading the input mesh
    mesh = vedo.Mesh(mesh)

    # Setting the view to Wireframe
    mesh.wireframe(True)
    
    # List of Vedo Points data structure 
    vedoVessel = []

    # List of colors
    chars = '0123456789ABCDEF'
    colors = ['#'+''.join(random.sample(chars,6)) for i in range(100)]
    
    # Creating Vedo Data Structures 
    for i, branch in enumerate(vessel): 

        branch = vedo.Points(branch, r=7)
        branch.c(np.random.choice(colors))
        vedoVessel.append(branch)

    # Plot 
    if PlotMesh:
        vedo.show(vedoVessel, mesh)
    else: 
        vedo.show(vedoVessel)