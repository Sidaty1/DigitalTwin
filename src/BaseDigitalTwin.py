from platform import node
import Sofa.Core

from beam import Beam

class BaseDigitalTwin: 
    """
        Base class of Digital Twin 
    """
    def __init__(self) -> None:
        pass
    def getSkeletonData(self, filename): 
        """
            Reads centerlines data from the file and gets structered data as follows 

                Vessel = list of branchs 

                branch = list of points coordinates

            :filename : file path 
        """
        branches = []
        branch = []
        file = open(filename)
        lines = file.readlines()
        for line in lines: 
            if line == "\n":
                branches.append(branch)
                branch = []

            else: 
                line = line.split()
                line = [float(val) for val in line]
                branch.append(line)
            
        return branches


    def get_centerlines(self, loader, outputflie):
        '''
            Apply the CGALSkeletonization Sofa plugin to get centerlines data

            :loader : Mesh file path 
        '''
        
        fileFormat = loader.split('.')[-1]
        if fileFormat == 'stl': 
            fileLoader = 'MeshSTLLoader'
        elif fileFormat == 'obj': 
            fileLoader = 'MeshObjLoader'
        elif fileFormat == 'vtk':
            fileLoader = 'MeshVTKLoader'
        else: 
            print("Unknown file format ", fileFormat)
            return
        node = Sofa.Core.Node()
        node.addObject('RequiredPlugin', name='MeshSkeletonizationPlugin')
        node.addObject('RequiredPlugin', name='SofaGeneralLoader')
        node.addObject('RequiredPlugin', name='SofaLoader')
        node.addObject(fileLoader, name='MeshLoader', filename=loader)
        node.addObject('MeshSkeletonization', template="Vec3d", inputFile=outputflie,  name="skel", inputVertices="@MeshLoader.position", inputTriangles="@MeshLoader.triangles")
        node.init()

    def required(self, node): 
        """
            Adding Sofa required plugins 
        """
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

        return node

    def addSolver(self, node, solver_parameters):
        node.addObject('EulerImplicitSolver', rayleighStiffness=solver_parameters['rayleighStiffness'],  
                                                    rayleighMass=solver_parameters['rayleighMass'], 
                                                    vdamping=solver_parameters['vdamping'])

        node.addObject('CGLinearSolver',  threshold=solver_parameters['threshold'], 
                                                tolerance=solver_parameters['tolerance'], 
                                                iterations=solver_parameters['iterations'],  printLog="false")

        return node

    def addParenchyma(self, node, parenchyma_parameters):
        """
            Given the parenchyma domain and specificities, we create its FEM model
        """
        parenchyma = node.addChild('parenchyma')
        parenchyma.addObject('MeshSTLLoader', name='LiverSurface', filename=parenchyma_parameters["meshFile"])
        parenchyma.addObject('FictitiousGrid',
                    template='Vec3',
                    name='integration_grid',
                    surface_positions="@LiverSurface.position", 
                    surface_triangles="@LiverSurface.triangles",
                    n=parenchyma_parameters['n'],
                    printLog=True
                    )
        parenchyma.addObject('MechanicalObject', name="dofs", src="@integration_grid")
        parenchyma.addObject('HexahedronSetTopologyContainer', name='topo', src='@integration_grid')
        parenchyma.addObject(parenchyma_parameters['material'], young_modulus=parenchyma_parameters['young_modulus'], poisson_ratio=parenchyma_parameters['poissonRatio'])
        parenchyma.addObject('HyperelasticForcefield', template="Hexahedron", printLog=True)
        parenchyma.addObject('FixedConstraint', name="FixedConstraint", indices=parenchyma_parameters['bc_indices'])
        parenchyma.addObject('UniformMass', totalMass=parenchyma_parameters['totalMass'])
        
        # parenchyma visualisation
        visu = parenchyma.addChild('Visu', tags="Visual")
        visu.addObject('OglModel', name="VisualModel", color=parenchyma_parameters['visualColor'], src="@../LiverSurface")
        visu.addObject('BarycentricMapping')
        return node

    def VesselMechanicalModeling(self, graph_node, vessel, vessels_parameter, bc=False):
        """
            Given a vessel tree, here we model each branch as a Beam with a specific material parameters 
        """
        graph = vessel.graph
        

        # List of branchs 
        branches = vessel.vaisseau
        # Modeling each vessel as a Beam using BeamForceField
        for key, adjacents in graph.items(): 

            # Beam infos: index and name
            beam_index = int(key)
            beam_name = "beam" + str(beam_index)

            # Adding the beam to the graph node
            beam = graph_node.addChild(beam_name)
            
            # Bezier curve fitting and sampling
            beam_structure = Beam(branches[beam_index], vessels_parameter['sampling_rate'])

            # Computing the quaternions and getting the MechanicalObject of the beam in the right format
            MO = beam_structure.get_MO_rigid()
            MO_vec = beam_structure.get_MO_vec()

            # Getting the Topology of the beam, used in the BeamForceField
            topology = beam_structure.get_topology()

            # MechanicalObject templated on Rigdi3d, x y z quaterniion
            beam.addObject('MechanicalObject', name="mo", template="Rigid3d", position=MO)
            
            # Uniform mass 
            beam.addObject('UniformMass', totalMass=vessels_parameter['totalMass'], showAxisSizeFactor=vessels_parameter['showAxisSizeFactor'])
            
            # Mesh Topology 
            beam.addObject('MeshTopology', name="topology", lines=topology)

            # Gets the indice of the will be fixed point of the vessel => Boudery Condition
            if len(adjacents[0]) ==  0 and len(adjacents[1]) != 0: 
                fixed_indices = "0"
            elif len(adjacents[0]) != 0 and len(adjacents[1]) == 0:
                fixed_indices = str(len(beam_structure.get_sample())-1)
            elif len(adjacents[0]) == 0 and len(adjacents[1]) == 0:
                fixed_indices = "0 " + str(len(beam_structure.get_sample())-1)
            else: 
                fixed_indices = ""
            
            # Boundery Condition
            if bc:
                beam.addObject("FixedConstraint", name="bc", indices=fixed_indices)
            
            # BeamForceField defines the FEM model of the beam
            beam.addObject('BeamFEMForceField', name="FEM", radius=vessels_parameter['radius'], radiusInner=vessels_parameter['radiusInner'],  youngModulus=vessels_parameter['young_modulus'], poissonRatio=vessels_parameter['poissonRatio'] )
            
            # Beam Vec is a clone of the beam that contains only x y z dofs in the mechanicalObject, it allows to map the beam with the Parenchyma
            beam_vec = beam.addChild('beam_vec')
            beam_vec.addObject('MechanicalObject', name="beam_vec_mo", position=MO_vec)
            beam_vec.addObject('UniformMass', totalMass=vessels_parameter['totalMass'], showAxisSizeFactor=vessels_parameter['showAxisSizeFactor'])
            beam_vec.addObject('IdentityMapping')

        return graph_node

    def addVessels(self, node, vessels_parameters):
        """
            Loading vessel mesh and adding visualisatio
        """
        # Vessels node
        vaisseau = node.addChild('vessels')
        vaisseau.addObject('MeshSTLLoader', name='MeshLoader', filename=vessels_parameters['meshFile'])
        
        # Vessels visual model 
        vaisseau.addObject('OglModel', name="VisualModel", color=vessels_parameters["visualColor"], src="@./MeshLoader")
        vaisseau.addObject('BarycentricMapping', input='@../parenchyma', output='@./')
        
        return node

    def VesselMechanicalCoupling(self, graph_node, vessel, vessels_parameter):
        """
            Given a set of branch, here we do mechanical coupling at biforcations using Springs
        """
        # Graph structure
        graph = vessel.graph

        # List of branchs 
        branches = vessel.vaisseau
        # Mechanical coupling between beams
        for key, adjacents in graph.items(): 

            # Curent beam infos: index and name
            beam_index = int(key)

            # Source Beam structure
            beam_structure = Beam(branches[beam_index], vessels_parameter['sampling_rate'])
            vertices = beam_structure.get_vertices()

            # Iterate on the first extremity of the vessel to find other connected vessels and do the mechanical coupling
            for elem in adjacents[0]: 

                # Target Beam infos
                external_rest_shape = "@../beam" + str(elem) + "/mo" 
                beam_target = Beam(branches[elem], vessels_parameter['sampling_rate'])

                # Get the biforcation point 
                biforcation = vertices[0]

                # Indexes of the biforcation in the  source and target beams
                indices1 = beam_structure.get_index_bif(biforcation)
                indices2 = beam_target.get_index_bif(biforcation)

                # Spring name describe its rool 
                spring_name = "join_beam" + key + " and beam" + str(elem)

                # Source beam infos
                this_beam_name = "beam" + key
                
                # Get the Source beam Sofa Node
                this_beam = graph_node.getChild(this_beam_name)
                
                # Coupling source and target beam with a Spring using RestShapeSpringsForceField
                this_beam.addObject('RestShapeSpringsForceField', name=spring_name, stiffness="1000", angularStiffness="10", external_rest_shape=external_rest_shape,  points=indices1, external_points=indices2)
            

            # Iterating on the second extremity of the vessel 
            for elem in adjacents[1]:

                # Target Beam infos                    
                external_rest_shape = "@../beam" + str(elem)  + "/mo"
                beam_target = Beam(branches[elem], vessels_parameter['sampling_rate'])

                # Gets the biforcation point 
                biforcation = vertices[1]

                # Indexes of the biforcation in the  source and target beams
                indices1 = beam_structure.get_index_bif(biforcation)
                indices2 = beam_target.get_index_bif(biforcation)

                # Spring name describes its rool 
                spring_name = "join_beam" + key + " and beam" + str(elem)

                # Source beam name
                this_beam_name = "beam" + key

                # Get the Source beam Sofa Node
                this_beam = graph_node.getChild(this_beam_name)

                # Coupling source and target beam with a Spring using RestShapeSpringsForceField
                this_beam.addObject('RestShapeSpringsForceField', name=spring_name, 
                                stiffness=vessels_parameter['vesselsCoupling']['stiffness'], 
                                angularStiffness=vessels_parameter['vesselsCoupling']['angularStiffness'], external_rest_shape=external_rest_shape,  points=indices1, external_points=indices2)
                
        return graph_node



    def LiverToVesselMapping(self, node, vessel, parenchyma_parameters, vessels_parameters, mapping_parameters):
        """
            Given a parenchyma and vessel node, here we map both using springs. Thus, creating the digital twin
        """
        # Getting the parenchyma node
        parenchyma = node.getChild("parenchyma")

        # Graph tree 
        graph = vessel.graph
        branches = vessel.vaisseau

        # Target Beam Vec
        target = parenchyma.addChild('target')
        target.addObject('MechanicalObject')

        # Iterating on all vessels beams
        for key, adjacents in graph.items(): 

            # Current beam infos
            beam_index = int(key)
            beam_name = "target_beam" + str(beam_index)
            beam = target.addChild(beam_name)
            
            # Getting the MechanicalObject Vec3d infos
            beam_structure = Beam(branches[beam_index], vessels_parameters['sampling_rate'])
            MO_vec = beam_structure.get_MO_vec()
            beam.addObject('MechanicalObject', name='mo', template="Vec3d", position=MO_vec)
            

            myobject1 = "@../../../vessels/Graphe_node/beam" + key + "/beam_vec"
            
            # Coupling each point of the BeamVec to its corresponding point in the BeamRigid
            for i in range(beam_structure.num_nodes): 
                spring_name = "index " + str(i) + " of the beam " + beam_name
                beam.addObject('StiffSpringForceField', name=spring_name, template="Vec3d", spring=str(i) + " " + str(i) + mapping_parameters['stiffness'], object1=myobject1, object2="@./")
        
            # Mapping The BeamVec with the Parenchyma 
            beam.addObject('BarycentricMapping', input="@../../dofs", output='@.')
        return parenchyma