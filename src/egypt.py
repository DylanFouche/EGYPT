import sys
from mesa.batchrunner import BatchRunner
from model import *
import matplotlib.pyplot as plt
import traceback
import numpy as np


def main():
	#get command line params
	if(len(sys.argv)!=5):
		print("Usage:\t$python3 ./src/egypt.py [num_agents] [num_steps] [grid_width] [grid_height]")
		quit()
	else:
		num_agents = int(sys.argv[1])
		num_steps = int(sys.argv[2])
		grid_width = int(sys.argv[3])
		grid_height = int(sys.argv[4])
	#create and run model
	model = EgyptModel(num_agents, grid_width, grid_height)
	for i in range(num_steps):
		model.step()
	#visualise agent wealth
	plt.subplot(1,2,1)
	agent_wealth = [agent.wealth for agent in model.schedule.agents]
	colours = ["alive" if agent.wealth > 0 else "dead" for agent in model.schedule.agents]
	N, bins, patches = plt.hist(agent_wealth)
	plt.title("Agent wealth distribution")
	plt.xlabel("Wealth")
	plt.ylabel("Agents")
	for i,rect in enumerate(patches):
		patches[i].set_color('r') if rect.get_x()<0 else patches[i].set_color('g')
	#visualise agent position
	plt.subplot(1,2,2)
	agent_counts = np.zeros((model.grid.width, model.grid.height))
	for cell in model.grid.coord_iter():
		cell_content, x, y = cell
		agent_count = len(cell_content)
		agent_counts[x][y] = agent_count
	plt.imshow(agent_counts, interpolation='nearest')
	plt.colorbar()
	plt.title("Agent positions")
	plt.show()
	# to get series of Gini coefficients as DataFrame from datacollector
	gini = model.datacollector.get_model_vars_dataframe()
	gini.plot()
	plt.title("Gini coefficient")
	plt.show()

	#batchrunner - not quite functioning as I would like
	# TODO
	fixed_params = {
		"w": 100,
		"h": 100
	}
	variable_params = {"n": range(10, 100, 10)}
	# The variables parameters will be invoke along with the fixed parameters allowing for either or both to be honored.
	batch_run = BatchRunner(
		EgyptModel,
		variable_params,
		fixed_params,
		iterations=5,
		max_steps=100,
		model_reporters={"Gini": compute_gini}
	)
	batch_run.run_all()
	run_data = batch_run.get_model_vars_dataframe()
	run_data.head()
	plt.scatter(run_data.n, run_data.Gini)
	plt.title("Gini coefficient iterations")
	plt.show()


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting...")
		quit()
	except Exception as e:
		print("Some other error occurred:")
		print(traceback.print_exc())
		quit()

