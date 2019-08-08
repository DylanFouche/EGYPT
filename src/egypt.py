import sys
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
	model = egyptModel(num_agents, grid_width, grid_height)
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
