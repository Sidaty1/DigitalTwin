from beam import Beam

class VGraph: 
    def __init__(self, vaisseau, sampling_rate):
        self.sampling_rate = sampling_rate
        self.vaisseau = vaisseau 
        self.graph = self.get_graph()
     
    def get_graph(self):
        """
        Generate the graph of the vessel tree

        Grphe format: dictionnary 

            graph = {'branche 0': list of branch 0 adjacent branchs, 

                        ...

                     'branche N': list of branch N adjacent branchs    
                    }

            
            list of branch i adjacent branch = [left adjacent branches, right adjacent branches]
            
            left/right adjacent branche = list of left/right adjacent branches index
        """
        graph = {}
        number_of_branch = len(self.vaisseau)
        for i in range(number_of_branch): 
            adjacent_branchs = self.get_adjacent_branchs(i)
            graph[str(i)] = adjacent_branchs

        return graph
        
    
    def get_adjacent_branchs(self, index):
        """
        List of adjacent branchs of a branch

        :index : index of the input branch
        """
        beam = Beam(self.vaisseau[index], self.sampling_rate)

        vertices = beam.get_vertices()
        adjacent_branchs = []
        for i in range(len(vertices)): 
            at_this_vertice = []
            for j in range(len(self.vaisseau)): 
                if vertices[i] in self.vaisseau[j] and not self.equal(self.vaisseau[index], self.vaisseau[j]):
                    at_this_vertice.append(j)
            adjacent_branchs.append(at_this_vertice)
        return adjacent_branchs
    

    def equal(self, list1, list2): 
        """
        Testing if two lists are equal, 
        
        this function should be mooved to a Helper
        """
        return list1 == list2