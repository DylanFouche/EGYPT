from mesa import Agent, Model
from mesa.time import RandomActivation

class egyptAgent(Agent):
    '''A settlement with random starting position and initial wealth of 1'''

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.wealth = self.random.randint(100,8000)

    def step(self):
        # TODO
        self.farm()
        self.eat()

    def farm(self):
        # TODO
        self.wealth += self.random.randint(0, 2475)

    def eat(self):
        # TODO
        self.wealth -= self.random.randint(0,10)*160

class egyptModel(Model):
    '''A model that aggregates n agents'''

    def __init__(self, n):
        self.num_agents = n
        # Add scheduler
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = egyptAgent(i, self)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one tick.'''
        self.schedule.step()