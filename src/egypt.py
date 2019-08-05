import sys
from model import *
import matplotlib.pyplot as plt

def main():
	#get command line params
	if(len(sys.argv)!=3):
		print("Usage:\t$python3 ./src/egypt.py [num_agents] [num_steps]")
		quit()
	else:
		num_agents = int(sys.argv[1])
		num_steps = int(sys.argv[2])
	#create and run model
	model = egyptModel(num_agents)
	for i in range(num_steps):
		model.step()
	#visualise agent wealth
	agent_wealth = [agent.wealth for agent in model.schedule.agents]
	plt.hist(agent_wealth)
	plt.title("Agent wealth distribution")
	plt.xlabel("Wealth")
	plt.ylabel("Agents")
	plt.show()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting...")
		quit()
	except e:
		print("Some other error occurred")
		print(e.message)
		quit()