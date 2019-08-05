from mesa import Agent, Model
from mesa.time import RandomActivation

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
        # TODO
        self.wealth += self.random.randint(0, 2475) #2475 is maximum yield from netlogo

    def eat(self):
        # TODO
        self.wealth -= self.random.randint(0,10)*160 #160 is annual grain consumption per person from netlogo

class egyptModel(Model):
    '''A model that aggregates n agents'''

    def __init__(self, n):
        self.num_agents = n
        # Add scheduler
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            agent = egyptAgent(i, self)
            self.schedule.add(agent)

    def step(self):
        '''Advance the model by one tick.'''
        self.schedule.step()