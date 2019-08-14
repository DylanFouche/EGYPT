from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import numpy as np
from math import sqrt, pi, e

# values hardcoded into NetLogo source
PATCH_MAX_POTENTIAL_YIELD = 2475
ANNUAL_PER_PERSON_GRAIN_CONSUMPTION = 160


# data collector methods
def compute_gini(model):
    agent_wealths = [agent.grain for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_agents

    if N * sum(x) == 0:
        return 0

    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)


def compute_population(model):
    return sum([household.workers for household in model.schedule.agents])


class HouseholdAgent(Agent):
    """A household with random initial wealth"""

    def __init__(self, unique_id, starting_size, competency, ambition, starting_grain, model):
        super().__init__(unique_id, model)
        self.workers = starting_size
        self.competency = competency
        self.ambition = ambition
        self.grain = starting_grain

    def step(self):
        self.farm()
        self.eat()
        self.population_shift()

    def farm(self):
        x, y = self.pos
        self.grain += PATCH_MAX_POTENTIAL_YIELD * self.model.grid.fertility[y, x] * self.competency

    def eat(self):
        self.grain -= self.workers * ANNUAL_PER_PERSON_GRAIN_CONSUMPTION
        if self.grain <= 0:
            self.workers -= 1
            self.grain = 0
            if self.workers <= 0:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                self.model.num_agents -= 1

    def population_shift(self):
        # TODO
        populate_chance = self.random.uniform(0,1)
        #criteria for increasing population as per netLogo implementation
        if (compute_population(self.model) <= (self.model.initial_population * (1 + (self.model.population_growth_rate / 100)) ** self.model.ticks)) and (populate_chance > 0.5):
            self.workers += 1

class EgyptGrid(SingleGrid):
    """A MESA grid containing the fertility values for patches of land"""

    def __init__(self, width, height, model):
        super().__init__(width, height, torus=False)

        self.width = width
        self.height = height
        self.random = model.random

        self.fertility = np.zeros((height, width))
        self.flood()  # initialise fertility values

        #show fertility map
        """
        from matplotlib import pyplot as plt
        plt.imshow(self.fertility)
        plt.show()
        """

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

    def __init__(self, n, w, h, starting_household_size=5, starting_grain=2000, min_competency=0.5, min_ambition=0.5, population_growth_rate=0.25):
        self.num_agents = n
        self.starting_household_size = starting_household_size
        self.starting_grain = starting_grain
        self.min_competency = min_competency
        self.min_ambition = min_ambition
        self.population_growth_rate = population_growth_rate
        self.initial_population = n * starting_household_size
        self.ticks = 0

        # Create scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = EgyptGrid(w, h, self)
        self.running = True  # BatchRunner set true

        # Create agents
        for i in range(self.num_agents):
            agent = HouseholdAgent(
                unique_id=i,
                starting_size=starting_household_size,
                competency=self.random.uniform(min_competency, 1.0),
                ambition=self.random.uniform(min_ambition, 1.0),
                starting_grain=starting_grain,
                model=self
            )
            self.schedule.add(agent)  # add agent to scheduler
            self.grid.position_agent(agent)  # place agent in a random empty patch

            # data collection
            self.datacollector = DataCollector(
                # compute gini coefficient - done in datacollector class
                model_reporters = {'Gini': compute_gini, 'total_population': compute_population})
                # agent_reporters = {"Wealth": "wealth"} )

    def step(self):
        """Advance the model by one tick."""
        self.schedule.step()
        self.ticks += 1
        # collect this step's data
        self.datacollector.collect(self)
