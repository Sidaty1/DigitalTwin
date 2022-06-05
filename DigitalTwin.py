import Sofa
import SofaCaribou
import SofaRuntime
import Sofa.Gui
import os, sys

dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src')
sys.path.append(os.path.abspath(dir))


# Source code importation
from vessel import VGraph
from BaseDigitalTwin import BaseDigitalTwin

# Solvers, parenchyma, vessels and mapping parameters included in the digitaltwin dictionnary
from parameters import digitaltwin


class ControlFrame(Sofa.Core.Controller, BaseDigitalTwin):
    def __init__(self, node):
        super().__init__(self)
        self.root = self.CreateGraph(node)

    def CreateGraph(self, node): 
        
        node = self.required(node)

        # Solver
        node = self.addSolver(node, digitaltwin['solver'])

        # Add parenchyma 
        node = self.addParenchyma(node, digitaltwin['parenchyma'])
        
        # Add vessels
        node = self.addVessels(node, digitaltwin['vessels'])

        # Structuring centerlines into a list of polylines 
        points = self.getSkeletonData(digitaltwin['vessels']['skeleton_output'])

        # Creating the Graph data structure 
        vessel = VGraph(points,digitaltwin['vessels']['sampling_rate'])
        graph = vessel.graph

        # Display the Vessels graph data structure
        print("\n")
        print("==============          The Graph          =================")
        print(graph)
        print("===========          End of the Graph          =============")
        print("\n")

        # Sofa graph node
        vaisseau = node.getChild("vessels")
        graph_node = vaisseau.addChild('Graphe_node')
        
        # Modeling vessels with beams
        graph_node = self.VesselMechanicalModeling(graph_node, vessel, digitaltwin['vessels'], bc=False)
        
        # Display somme infos about the Vessels Graph
        print('Total number of branch ', len(graph))
        print("The sampling rate is: ", digitaltwin['vessels']['sampling_rate'])

        # Coupling Beams 
        graph_node = self.VesselMechanicalCoupling(graph_node, vessel, digitaltwin['vessels'])

        # Mapping between the Parenchyma and Vessels: BeamRigid <-> BeamVec <-> Parenchyma
        node = self.LiverToVesselMapping(node, vessel, digitaltwin['parenchyma'], digitaltwin['vessels'], digitaltwin['mapping'])
            

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
    baseDT.get_centerlines(digitaltwin['vessels']['meshFile'], digitaltwin['vessels']['skeleton_output'])

    # Mechanical modeling and coupling of the vessels
    main()