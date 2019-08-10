from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.batchrunner import BatchRunner

# data collector methods
def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)

def compute_meanPopulation(model):
    # TODO
    agent_population = [agent.num for agent in model.schedule.agents]
    N = model.num_agents

class egyptAgent(Agent):
    '''A household with random initial wealth'''

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = self.random.randint(100,8000) #[100,8000] is initial wealth range from netlogo

    def step(self):
        # TODO
        self.farm()
        self.eat()

    def farm(self):
        # grain yield is inversely proportional to distance from column x=0 (river)
        x, y = self.pos
        width = self.model.grid.width
        self.wealth += (2475/width) * (width-x) #2475 is maximum yield from netlogo
        #for x=0 => yield=max. for x=width => yield=0.

    def eat(self):
        # TODO
        self.wealth -= self.random.randint(1,6)*160 #160 is annual grain consumption per person from netlogo
        #number of agents in household unknown, chosen at random between 1 and 6.

class egyptModel(Model):
    '''A model that aggregates n agents'''

    def __init__(self, n, w, h):
        self.num_agents = n
        # Create scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = MultiGrid(w, h, False) #grid is not toroidal <-- what does this mean?
        self.running = True #BatchRunner set true

        # Create agents
        for i in range(self.num_agents):
            agent = egyptAgent(i, self)
            # add agent to scheduler
            self.schedule.add(agent)
            # add agent to grid
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

            #data collection
            self.datacollector = DataCollector(
                # compute gini coefficient - done in datacollector class
                model_reporters = {"Gini": compute_gini })
                #agent_reporters = {"Wealth": "wealth"} )

    def step(self):
        '''Advance the model by one tick.'''
        #collect this step's data
        self.datacollector.collect(self)
        self.schedule.step()

