from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import numpy as np
from math import sqrt, pi, e

# values hardcoded into NetLogo source
PATCH_MAX_POTENTIAL_YIELD = 2475
ANNUAL_PER_PERSON_GRAIN_CONSUMPTION = 160

# values adjustable by sliders in NetLogo source
STARTING_HOUSEHOLD_SIZE = 5
STARTING_GRAIN = 2000
MIN_COMPETENCY = 0.5

# data collector methods
def compute_gini(model):
    agent_wealths = [agent.grain for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)


def compute_meanPopulation(model):
    # TODO
    agent_population = [agent.num for agent in model.schedule.agents]
    N = model.num_agents


class HouseholdAgent(Agent):
    """A household with random initial wealth"""

    def __init__(self, unique_id, starting_size, competency, starting_grain, model):
        super().__init__(unique_id, model)
        self.workers = starting_size
        self.competency = competency
        self.grain = starting_grain

    def step(self):
        # TODO
        self.farm()
        self.eat()

    def farm(self):
        x, y = self.pos
        self.grain += PATCH_MAX_POTENTIAL_YIELD * self.model.grid.fertility[y, x] * self.competency

    def eat(self):
        self.grain -= self.workers * ANNUAL_PER_PERSON_GRAIN_CONSUMPTION
        if self.grain <= 0:
            self.workers -= 1
            if self.workers <= 0:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)


class EgyptGrid(SingleGrid):
    """A MESA grid containing the fertility values for patches of land"""
    
    def __init__(self, width, height, model):
        super().__init__(width, height, torus=False)
        
        self.width = width
        self.height = height
        self.random = model.random
        
        self.fertility = np.zeros((height, width))
        self.flood()  # initialise fertility values
    
    def flood(self):
        """Simulates nile flood. Assigns new patch fertility values."""

        # Set fertility values according to normal distribution probability density function
        # https://en.wikipedia.org/wiki/Normal_distribution

        # All patches in a column have the same fertility

        # the mean and standard deviation value ranges are according to NetLogo source code
        mu = self.random.randint(5, 14)  # random integer from 5 to 14 (inclusive of both 5 and 14)
        sigma = self.random.randint(5, 9)

        alpha = 2 * sigma ** 2
        beta = 1 / (sigma * sqrt(2 * pi))

        # as per NetLogo code
        for x in range(self.width):
            self.fertility[:, x] = 17 * (beta * (e ** (-(x - mu) ** 2 / alpha)))  # assign fertility value to column x


class EgyptModel(Model):
    """A model that aggregates n agents"""

    def __init__(self, n, w, h):
        self.num_agents = n
        # Create scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = EgyptGrid(w, h, self)
        self.running = True  # BatchRunner set true

        # Create agents
        for i in range(self.num_agents):
            agent = HouseholdAgent(
                unique_id=i,
                starting_size=STARTING_HOUSEHOLD_SIZE,
                competency=self.random.uniform(MIN_COMPETENCY, 1.0),
                starting_grain=STARTING_GRAIN,
                model=self
            )
            self.schedule.add(agent)  # add agent to scheduler
            self.grid.position_agent(agent)  # place agent in a random empty patch

            # data collection
            self.datacollector = DataCollector(
                # compute gini coefficient - done in datacollector class
                model_reporters = {"Gini": compute_gini })
                # agent_reporters = {"Wealth": "wealth"} )

    def step(self):
        """Advance the model by one tick."""
        # collect this step's data
        self.datacollector.collect(self)
        self.schedule.step()

