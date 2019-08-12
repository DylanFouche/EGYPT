import sys
import egypt_utils
from egypt_model import EgyptModel

# get command line params
if len(sys.argv) != 5:
    print("Usage:\t$python3 src/simulations/single_simulation.py [num_agents] [num_steps] [grid_width] [grid_height]")
    quit()
else:
    num_agents = int(sys.argv[1])
    num_steps = int(sys.argv[2])
    grid_width = int(sys.argv[3])
    grid_height = int(sys.argv[4])

# create and run model
model = EgyptModel(num_agents, grid_width, grid_height)
for i in range(num_steps):
    model.step()

egypt_utils.visualise_model_state(model)
egypt_utils.plot_model_variable_graphs(model)
egypt_utils.show_graphs()
