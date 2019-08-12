from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from egypt_model import EgyptModel, HouseholdAgent


def __agent_portrayal__(agent):
    if type(agent) == HouseholdAgent:
        portrayal = {
            "Shape": "circle",
            "Color": "green",
            "Filled": "true",
            "Layer": 2,
            "r": agent.grain / 4000
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
        'min_competency': UserSettableParameter(
            'slider',
            'min_competency',
            value=0.5,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
            description='Minimum Household Competency'),
        'w': width,
        'h': height
    }
    
    visualisation_elements = []

    # grid visualisation
    visualisation_elements.append(CanvasGrid(__agent_portrayal__, width, height, 500, 500))
    
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
