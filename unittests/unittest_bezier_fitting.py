import sys
import os
import random
import vedo 
import numpy as np 

dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir, 'src')
sys.path.append(os.path.abspath(dir))
print(dir)

from BaseDigitalTwin import BaseDigitalTwin
from beam import Beam

if __name__ == '__main__':
    """
        Given the centerlines and a sample_rate, this generates and plot the Bezier curve fitting and sampling 
    """

    # Input mesh 
    mesh = "../data/mesh/processed_porteveine.stl"

    # Input text file where centerlines will be stored
    skeleton_file = "../data/skeleton/output_skeleton.txt"

    # Structuring centerlines into a list of polylines 
    baseDT = BaseDigitalTwin()
    baseDT.get_centerlines(mesh, skeleton_file)
    vessel = baseDT.getSkeletonData(skeleton_file)

    # Bezier curves
    BezierCurves = []

    # Sampled points 
    SampledPoints = []

    # List of colors
    chars = '0123456789ABCDEF'
    colors = ['#'+''.join(random.sample(chars,6)) for i in range(100)]
    
    for branch in vessel: 

        # Using the Beam class, we approximate a bezier curve on the centerlines and sampe points each 0.005 
        beam = Beam(branch, 0.005)
        sample = beam.sample

        # Vedo Points data Structure
        sample = vedo.Points(sample, r=5)
        color = np.random.choice(colors)
        sample.c(color)
        SampledPoints.append(sample)

        # Vedo Bezier Curves visualization 
        BezierCurves.append(vedo.Bezier(beam.sample).c(color))

    # Plotting
    vedo.show(SampledPoints, BezierCurves)