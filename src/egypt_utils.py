import numpy as np
import matplotlib.pyplot as plt
from egypt_model import EgyptModel
from mesa.batchrunner import BatchRunner


def visualise_model_state(model: EgyptModel):
    """Visualise the current state of the model"""
    
    # visualise agent wealth
    plt.subplot(1, 2, 1)
    agent_wealth = [agent.wealth for agent in model.schedule.agents]
    colours = ["alive" if agent.wealth > 0 else "dead" for agent in model.schedule.agents]
    N, bins, patches = plt.hist(agent_wealth)
    plt.title("Agent wealth distribution")
    plt.xlabel("Wealth")
    plt.ylabel("Agents")
    for i, rect in enumerate(patches):
        patches[i].set_color('r') if rect.get_x() < 0 else patches[i].set_color('g')
    
    # visualise agent position
    plt.subplot(1, 2, 2)
    agent_counts = np.zeros((model.grid.width, model.grid.height))
    for cell in model.grid.coord_iter():
        cell_content, x, y = cell
        agent_count = len(cell_content)
        agent_counts[x][y] = agent_count
    plt.imshow(agent_counts, interpolation='nearest')
    plt.colorbar()
    plt.title("Agent positions")
    
    plt.show()


def plot_model_variable_graphs(model: EgyptModel):
    """Plot graphs showing how model variables (e.g. Gini coefficient) change over each step of the simulation run"""
    
    # to get series of model variables as DataFrame from model datacollector
    model_variables = model.datacollector.get_model_vars_dataframe()
    model_variables.plot()
    plt.show()


def plot_batch_run_variable_graphs(batch_run: BatchRunner):
    run_data = batch_run.get_model_vars_dataframe()
    run_data.head()
    plt.scatter(run_data.n, run_data.Gini)
    plt.title("Gini coefficient iterations")
    plt.show()
