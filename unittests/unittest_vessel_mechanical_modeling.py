import sys, os

import Sofa
import SofaCaribou
import SofaRuntime
import Sofa.Gui

dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.pardir, 'src')
sys.path.append(os.path.abspath(dir))



from BaseDigitalTwin import BaseDigitalTwin
from vessel import VGraph

# Input Mesh: Obj/VTK or other 
mesh = "../data/mesh/processed_porteveine.stl"

# Input text file where centerlines will be stored
skeleton_file = "../data/skeleton/output_skeleton.txt"

# Using the digitaltwin dictionnary to get some standard parameters of the model
from parameters import digitaltwin


class ControlFrame(Sofa.Core.Controller, BaseDigitalTwin):
    def __init__(self, node):
        super().__init__(self)
        self.root = self.CreateGraph(node)

    def CreateGraph(self, node): 
        node.name = "root"
        node.dt = 0.01
        node.gravity = [0, 0, 0]

        # Required plugins
        node.addObject('RequiredPlugin', name='SofaOpenglVisual')
        node.addObject('RequiredPlugin', name='SofaGeneralSimpleFem')
        node.addObject('RequiredPlugin', name='SofaLoader')
        node.addObject('RequiredPlugin', name='SofaGeneralEngine')
        node.addObject('RequiredPlugin', name='SofaBoundaryCondition')
        node.addObject('RequiredPlugin', name='SofaImplicitOdeSolver')
        node.addObject('RequiredPlugin', name='SofaCaribou')
        node.addObject('VisualStyle', displayFlags='showVisualModels showWireframe showBehaviorModels showCollisionModels')

        # Solver
        node.addObject('EulerImplicitSolver', rayleighStiffness="0",  rayleighMass="0.1", vdamping="3")
        node.addObject('CGLinearSolver',  threshold="0.000000001", tolerance="0.0000000001", iterations="100", printLog="false")

        # Vessels Node
        vaisseau = node.addChild('vessel')
        
        # Loading the mesh
        vaisseau.addObject('MeshObjLoader', name='MeshLoader', filename=mesh)
        
        # Structuring centerlines into a list of polylines 
        points = self.getSkeletonData(skeleton_file)
        
        # defining a sampling ratio
        sampling_rate = 0.005
        
        # Creating the Graph data structure 
        vessel = VGraph(points, sampling_rate)
        graph = vessel.graph
        
        # Sofa graph node
        graph_node = vaisseau.addChild('Graphe_node')

        
        # Display the Vessels graph data structure
        print("\n")
        print("==============          The Graph          =================")
        print(graph)
        print("===========          End of the Graph          =============")
        print("\n")

        # Sofa graph node
        graph_node = vaisseau.addChild('Graphe_node')
        
        # Modeling vessels with beams
        graph_node = self.VesselMechanicalModeling(graph_node, vessel, digitaltwin['vessels'], bc=False)
        
        # Display somme infos about the Vessels Graph
        print('Total number of branch ', len(graph))
        print("The sampling rate is: ", digitaltwin['vessels']['sampling_rate'])

        # Coupling Beams 
        graph_node = self.VesselMechanicalCoupling(graph_node, vessel, digitaltwin['vessels'])


def createScene(node): 
    node.addObject(ControlFrame(node))


def main(): 
    SofaRuntime.importPlugin("SofaOpenglVisual")
    SofaRuntime.importPlugin("SofaImplicitOdeSolver")
    SofaRuntime.importPlugin("SofaLoader")

    root = Sofa.Core.Node("root")
    createScene(root)
    Sofa.Simulation.init(root)

    Sofa.Gui.GUIManager.Init("Scene", "qglviewer")
    Sofa.Gui.GUIManager.createGUI(root, __file__)
    Sofa.Gui.GUIManager.SetDimension(1080, 1080)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI(root, __file__)
    Sofa.Gui.GUIManager.MainLoop(root)
    Sofa.Gui.GUIManager.closeGUI()



if __name__ == '__main__':
    # Storing the centeralines in the given text file 
    baseDT = BaseDigitalTwin()
    baseDT.get_centerlines(mesh, skeleton_file)

    # Mechanical modeling and coupling of the vessels
    main()