from collections import defaultdict

import numpy as np
from math import sqrt
from matplotlib.colors import to_hex
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement
from egypt_model import EgyptModel, Household, FieldAgent, SettlementAgent

colours = ['red',
           'yellow',
           'pink',
           'blue',
           '#00ff00',
           'purple',
           'cyan',
           'orange',
           'brown']


def __agent_portrayal__(agent):
    if type(agent) == SettlementAgent:
        portrayal = {
            "Shape": "circle",
            "Color": colours[hash(agent.unique_id) % len(colours)],
            "Filled": "true",
            "Layer": 2,
            "r": sqrt(agent.workers() / 15)
        }
    elif type(agent) == FieldAgent:
        portrayal = {
            "Shape": "rect",
            "Color": colours[hash(agent.household.settlement.unique_id) % len(colours)],
            "Filled": "true",
            "Layer": 1,
            "h": 0.2,
            "w": 0.2
        }
    else:
        portrayal = None
    return portrayal


class EgyptGrid(VisualizationElement):
    package_includes = ["GridDraw.js", "InteractionHandler.js"]
    local_includes = ["src/js/CanvasModule.js"]

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
        colour_map = ScalarMappable(norm=Normalize(vmin=-0.5, vmax=np.max(model.grid.fertility) * 1.2), cmap='Greens')

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
        'starting_settlements': UserSettableParameter(
            'slider',
            'starting_settlements',
            value=14,
            min_value=5,
            max_value=20,
            description='Initial Number of Settlements'),
        'starting_households': UserSettableParameter(
            'slider',
            'starting_households',
            value=7,
            min_value=1,
            max_value=10,
            description='Initial Number of Households per Settlement'),
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
            value=5,
            min_value=5,
            max_value=40,
            description='Household Knowledge Radius'),
        'population_growth_rate': UserSettableParameter(
            'slider',
            'pop_growth_rate',
            value=0.1,
            min_value=0.0,
            max_value=0.5,
            step=0.01,
            description='Population Growth Rate'),
        'distance_cost': UserSettableParameter(
            'slider',
            'distance_cost',
            value=10,
            min_value=1,
            max_value=15,
            step=1,
            description='Distance Cost'),
        'allow_rental': UserSettableParameter(
            'checkbox',
            'allow_rental',
            value=False,
            description= 'Allow Land Rental'),
        'land_rental_rate': UserSettableParameter(
            'slider',
            'land_rental_rate',
            value=0.5,
            min_value=0.3,
            max_value=0.6,
            step=0.05,
            description='Land Rental Rate'),
        'fallow_limit': UserSettableParameter(
            'slider',
            'fallow_limit',
            value=4,
            min_value=0,
            max_value=10,
            step=1,
            description='Fallow Limit'),
        'annual_competency_increase': UserSettableParameter(
            'slider',
            'annual_competency_increase',
            value=0,
            min_value=0,
            max_value=10,
            step=0.25,
            description='Annual Competency Increase Percentage'),
        'w': width,
        'h': height
    }

    visualisation_elements = []

    # grid visualisation
    visualisation_elements.append(EgyptGrid(__agent_portrayal__, width, height, 500, 500))

    # datacollector graphs
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Gini',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Total Wealth',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Mean Settlement Wealth',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Total Population',
            'Color': 'Black'
        }],
        data_collector_name='datacollector'
    ))
    visualisation_elements.append(ChartModule(
        [{
            'Label': 'Mean Settlement Population',
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
