from mesa import Agent, Model
from mesa.time import RandomActivation

class egyptAgent(Agent):
	"""A settlement with random starting position and initial wealth of 1"""
	def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = 1

     def step(self):
        # TODO
        pass

class egyptModel(Model):
	"""A model that aggregates n agents"""
	def __init__(self, n):
        self.num_agents = n
        # Add scheduler
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = MoneyAgent(i, self)
            self.schedule.add(a)

        def step(self):
	        '''Advance the model by one tick.'''
	        self.schedule.step()