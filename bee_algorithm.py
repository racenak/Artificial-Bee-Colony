import random
from scipy.io import mmread
import networkx as nx
# Placeholder imports for required dependencies
# from your_module import Graph, getRandomNumberInRange, Logger

class ArtificialBeeColonyConfig:
    def __init__(self, employed_bees_count=2, onlooker_bees_count=28, verbose=False):
        self.employed_bees_count = employed_bees_count
        self.onlooker_bees_count = onlooker_bees_count
        self.verbose = verbose

class ArtificialBeeColony:
    def __init__(self, graph, config=ArtificialBeeColonyConfig()):
        self.EMPLOYED_BEES_COUNT = config.employed_bees_count
        self.ONLOOKER_BEES_COUNT = config.onlooker_bees_count
        self.PALETTE_SIZE = 10000
        self.IS_VERBOSE = config.verbose

        self.initial_graph = graph
        self.graph = self.initial_graph.copy()
        self.palette = self.generate_palette()
        self.available_vertices = list(self.graph.nodes)
        self.used_colors = []

        self.no_improvement_counter = {node: 0 for node in self.graph.nodes}  
        self.SCOUT_THRESHOLD = 5 

    def get_colors(self):
        colors = {}
        for node in self.graph.nodes:
            colors[node] = self.graph.nodes[node].get('color', None)  # Get color or None if not colored
        return colors


    def get_chromatic_number(self):
        self.log('===== STARTING ALGORITHM =====\n')
        while not self.is_completed():
            self.log('SENDING Employed bees\n')
            chosen_vertices = self.send_employed_bees()
    
            self.log('CHOSEN VERTICES:')
            self.log(None, {'array': chosen_vertices})
    
            self.log('SENDING Onlooker bees\n')
            self.send_onlooker_bees(chosen_vertices)
    
            self.log('CURRENT COLORING: ')
            self.log(None, {'array': self.get_colors()})  # Use the new method to get colors
    
        chromatic_number = len(set(self.get_colors().values()))  # Unique colors used
        return chromatic_number


    def reset(self):
        self.used_colors = []
        self.available_vertices = self.graph.get_vertex_array()
        self.graph = self.initial_graph.get_copy()

    def send_employed_bees(self):
        chosen_vertices = []
        for _ in range(self.EMPLOYED_BEES_COUNT):
            random_vertex = random.choice(self.available_vertices)
            self.available_vertices.remove(random_vertex)
            chosen_vertices.append(random_vertex)

            if self.no_improvement_counter[random_vertex] >= self.SCOUT_THRESHOLD:
                self.scout_bee(random_vertex)
                self.no_improvement_counter[random_vertex] = 0  # Reset bộ đếm sau khi scout bee tìm kiếm
            else:
                self.no_improvement_counter[random_vertex] += 1 
            
        return chosen_vertices

    def send_onlooker_bees(self, chosen_vertices):
        degrees_of_chosen_vertices = self.get_degrees_of_chosen_vertices(chosen_vertices)
        onlooker_bees_distribution = self.get_onlooker_bees_distribution(degrees_of_chosen_vertices)

        for chosen_vertex, onlooker_bees_count in zip(chosen_vertices, onlooker_bees_distribution):
            adjacent_vertices = list(self.graph.neighbors(chosen_vertex))  # Correct method
            self.color_adjacent_vertices(adjacent_vertices, onlooker_bees_count)
            self.color_vertex(chosen_vertex)


    def get_onlooker_bees_distribution(self, degrees_of_chosen_vertices):
        nectar_values = self.get_nectar_values(degrees_of_chosen_vertices)
        number_of_left_onlooker_bees = self.ONLOOKER_BEES_COUNT

        distribution = []
        for i, nectar in enumerate(nectar_values):
            if i == len(nectar_values) - 1:
                distribution.append(number_of_left_onlooker_bees)
            else:
                bees_for_spot = int(nectar * number_of_left_onlooker_bees)
                number_of_left_onlooker_bees -= bees_for_spot
                distribution.append(bees_for_spot)
        return distribution
    
    def scout_bee(self, vertex):
        self.log(f"SCOUT BEE ACTIVATED for vertex {vertex}")
        
        new_color = self.get_next_color()
        self.used_colors.append(new_color)
        self.graph.nodes[vertex]['color'] = new_color
        self.log(f"New color {new_color} assigned to vertex {vertex} by scout bee")

    def get_nectar_values(self, degrees_of_chosen_vertices):
        sum_of_degrees = sum(degrees_of_chosen_vertices)
        return [degree / sum_of_degrees for degree in degrees_of_chosen_vertices]

    def color_adjacent_vertices(self, adjacent_vertices, onlooker_bees_count):
        for vertex in adjacent_vertices[:onlooker_bees_count]:
            self.color_vertex(vertex)

    def can_color(self, vertex, color):
        for neighbor in self.graph.neighbors(vertex):
            if self.graph.nodes[neighbor].get('color') == color:  # Check neighbor color
                return False
        return True


    def color_vertex(self, vertex):
        available_colors = self.used_colors[:]
        is_colored = False

        while not is_colored:
            if not available_colors:
                new_color = self.get_next_color()
                self.used_colors.append(new_color)
                self.graph.nodes[vertex]['color'] = new_color  # Color the vertex
                break

            color = random.choice(available_colors)
            available_colors.remove(color)

            if self.can_color(vertex, color):
                self.graph.nodes[vertex]['color'] = color  # Color the vertex
                is_colored = True


    def get_next_color(self):
        return self.palette[len(self.used_colors)]

    def get_degrees_of_chosen_vertices(self, chosen_vertices):
        return [self.graph.degree(vertex) for vertex in chosen_vertices]


    def generate_palette(self):
        return list(range(self.PALETTE_SIZE))

    def is_completed(self):
        # Check if all nodes have a color and that the coloring is valid
        for vertex in self.graph.nodes:
            if 'color' not in self.graph.nodes[vertex]:  # Not all nodes are colored
                return False
            if not self.can_color(vertex, self.graph.nodes[vertex]['color']):  # Check for conflicts
                return False
        return True


    def log(self, message, array=None):
        if self.IS_VERBOSE:
            if array is not None:
                print(array)
            else:
                print(message)


# Step 1: Load the .mtx file into a sparse matrix
matrix_file_path = 'johnson8-2-4.mtx'
sparse_matrix = mmread(matrix_file_path)

# Step 2: Convert the sparse matrix to a NetworkX graph
graph = nx.from_scipy_sparse_array(sparse_matrix)

# Now `graph` can be used in any algorithm, e.g., the Artificial Bee Colony for graph coloring
# Assuming `ArtificialBeeColony` is already implemented:
config = ArtificialBeeColonyConfig(employed_bees_count=28, onlooker_bees_count=42, verbose=True)
abc = ArtificialBeeColony(graph, config)
chromatic_number = abc.get_chromatic_number()
print("Chromatic Number:", chromatic_number)


        