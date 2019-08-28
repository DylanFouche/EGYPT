from collections import defaultdict

import numpy as np
from matplotlib.colors import to_hex
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from egypt_model import EgyptModel, HouseholdAgent


def __agent_portrayal__(agent):
    if type(agent) == HouseholdAgent:
        portrayal = {
            "Shape": "circle",
            "Color": "orange",
            "Filled": "true",
            "Layer": 2,
            "r": agent.workers / 5
        }
    else:
        portrayal = {
            "Shape": "circle",
            "Color": "red",
            "Filled": "true",
            "Layer": 1,
            "r": 0.5
        }
    return portrayal


class EgyptGrid(VisualizationElement):
    package_includes = ["GridDraw.js", "CanvasModule.js", "InteractionHandler.js"]
    
    def __init__(self, portrayal_method, grid_width, grid_height,
                 canvas_width=500, canvas_height=500):
        """ Instantiate a new EgyptGrid.

        Args:
            portrayal_method: function to convert each object on the grid to
                              a portrayal, as described above.
            grid_width, grid_height: Size of the grid, in cells.
            canvas_height, canvas_width: Size of the canvas to draw in the
                                         client, in pixels. (default: 500x500)

        """
        self.portrayal_method = portrayal_method
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        new_element = ("new CanvasModule({}, {}, {}, {})"
                       .format(self.canvas_width, self.canvas_height,
                               self.grid_width, self.grid_height))
        
        self.js_code = "elements.push(" + new_element + ");"
    
    def render(self, model):
        # create a mapping from fertility values to colours
        colour_map = ScalarMappable(norm=Normalize(vmin=-0.5, vmax=np.max(model.grid.fertility)*1.2), cmap='Greens')
        
        # create list of hex colour strings for each column of the grid
        colours = []
        for x in range(self.grid_width):
            colours.append(to_hex(colour_map.to_rgba(model.grid.fertility[0, x])))
        
        grid_state = defaultdict(list)
        for x in range(model.grid.width):
            for y in range(model.grid.height):
                portrayal = {
                    "Shape": "rect",
                    "x": x,
                    "y": y,
                    "w": 1,
                    "h": 1,
                    "Color": colours[x],
                    "Filled": "true",
                    "Layer": 0
                }
                grid_state[0].append(portrayal)
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                for obj in cell_objects:
                    portrayal = self.portrayal_method(obj)
                    if portrayal:
                        portrayal["x"] = x
                        portrayal["y"] = y
                        grid_state[portrayal["Layer"]].append(portrayal)
        
        return grid_state


def launch(width, height, port=None):
    model_params = {
        'n': UserSettableParameter(
            'slider',
            'starting_households',
            value=7,
            min_value=1,
            max_value=10,
            description='Initial Number of Households'),
        'starting_household_size': UserSettableParameter(
            'slider',
            'starting_household_size',
            value=5,
            min_value=1,
            max_value=10,
            description='Initial Number of Workers in each Household'),
        'starting_grain': UserSettableParameter(
            'slider',
            'starting_grain',
            value=3000,
            min_value=100,
            max_value=8000,
            description='Initial Grain Supply of Households'),
        'min_ambition': UserSettableParameter(
            'slider',
            'min_ambition',
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            description='Minimum Household Ambition'),
        'min_competency': UserSettableParameter(
            'slider',
            'min_competency',
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            description='Minimum Household Competency'),
        'generational_variation': UserSettableParameter(
            'slider',
            'generational_variation',
            value=0.9,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            description='Generational Variation in Ambition and Competency'),
        'knowledge_radius': UserSettableParameter(
            'slider',
            'knowledge_radius',
            value=20,
            min_value=5,
            max_value=40,
            description='Household Knowledge Radius'),
        'population_growth_rate_percentage': UserSettableParameter(
            'slider',
            'pop_growth_rate_percentage',
            value=0.1,
            min_value=0.0,
            max_value=0.5,
            step=0.01,
            description='Population Growth Rate'),
        'w': width,
        'h': height
    }
    
    visualisation_elements = []

    # grid visualisation
    visualisation_elements.append(EgyptGrid(__agent_portrayal__, width, height, 500, 500))
    
    # Gini coefficient graph
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Gini',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))

    # Total population graph
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'total_population',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))
    
    server = ModularServer(
        EgyptModel,
        visualisation_elements,
        'Egypt Model',
        model_params
    )
    
    server.launch(port)
