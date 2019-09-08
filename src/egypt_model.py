from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import numpy as np
from math import sqrt, pi, e

# constants in NetLogo source
PATCH_MAX_POTENTIAL_YIELD = 2475
ANNUAL_PER_PERSON_GRAIN_CONSUMPTION = 160  # 160 kilograms of grain per person annually, after Hassan 1984, 63.
SEEDING_COST = 300  # cost of seeding a field, assuming 1/8 of maximum potential yield.


# data collector methods
def compute_gini(model):
    if compute_total_wealth(model) == 0:
        return 0
    
    total_wealth = compute_total_wealth(model)
    households = sorted(model.households, key=lambda household: household.grain, reverse=False)
    cumulative_wealth = 0
    gini_index_reserve = 0
    
    for i, household in enumerate(households):
        cumulative_wealth += household.grain
        gini_index_reserve += i / len(households) - cumulative_wealth / total_wealth
    
    return gini_index_reserve / len(households) / 0.5


def compute_total_population(model):
    return sum([settlement.workers() for settlement in model.settlements])


def compute_mean_population(model):
    if len(model.settlements) == 0:
        return 0
    return compute_total_population(model) / len(model.settlements)


def compute_total_wealth(model):
    return sum([settlement.grain() for settlement in model.settlements])


def compute_mean_wealth(model):
    if len(model.settlements) == 0:
        return 0
    return compute_total_wealth(model) / len(model.settlements)


class FieldAgent(Agent):
    """A field is a piece of land claimed by a household"""
    
    def __init__(self, unique_field_id, model, household):
        super().__init__(unique_field_id, model)
        self.model = model
        self.household = household
        self.years_fallowed = 0
        self.harvested = False
    
    def changeover(self):
        if self.harvested:
            self.years_fallowed = 0
        else:
            self.years_fallowed += 1
        
        if self.years_fallowed >= self.model.fallow_limit:
            self.household.fields.remove(self)
            self.model.fields.remove(self)
            self.model.grid.remove_agent(self)
        
        self.harvested = False


class SettlementAgent(Agent):
    """A settlement that aggregates n households and fields."""
    
    def __init__(self, unique_id, num_households, starting_household_size, starting_grain, min_competency, min_ambition, model):
        super().__init__(unique_id, model)
        self.households = []
        for i in range(num_households):
            agent = Household(
                starting_size=starting_household_size,
                competency=self.random.uniform(min_competency, 1.0),
                ambition=self.random.uniform(min_ambition, 1.0),
                starting_grain=starting_grain,
                settlement=self
            )
            self.households.append(agent)
            self.model.households.append(agent)
    
    def workers(self):
        return sum([household.workers for household in self.households])
    
    def grain(self):
        return sum([household.grain for household in self.households])


class Household():
    """A household that aggregates n workers"""
    
    def __init__(self, starting_size, competency, ambition, starting_grain, settlement):
        self.workers = starting_size
        self.workers_worked = 0
        self.competency = competency
        self.ambition = ambition
        self.grain = starting_grain
        self.settlement = settlement
        self.generation_changeover_countdown = self.settlement.random.randint(10, 15)
        self.fields = []
    
    def farm(self):
        """ Increase grain in proportion to field fertility and worker competency """
        household_x, household_y = self.settlement.pos
        total_harvest = 0
        self.workers_worked = 0
        for i in range(self.workers // 2):
            best_field = None
            best_harvest = 0
            
            for field in self.fields:
                field_x, field_y = field.pos
                
                this_harvest = ((self.settlement.model.grid.fertility[household_y][household_x] * PATCH_MAX_POTENTIAL_YIELD * self.competency) \
                                - (sqrt((household_x - field_x) ** 2 + (household_y - field_y) ** 2) * self.settlement.model.distance_cost))
                if not field.harvested and this_harvest > best_harvest:
                    best_field = field
                    best_harvest = this_harvest
            
            farm_chance = self.settlement.random.uniform(0, 1)
            if best_field is not None and (self.grain < (
                    self.workers * ANNUAL_PER_PERSON_GRAIN_CONSUMPTION) or farm_chance < self.ambition * self.competency):
                best_field.harvested = True
                total_harvest += best_harvest - SEEDING_COST
                self.workers_worked += 2  # each field = 9.52 feddan. Heqanakht papyri suggest 1 worker per 13 feddan. but Islamic period records 1 worker for every 5 or 6 feddan (Lehner 2000, 310), which is what we are following. Since 'worker' here really means household member, and the assumption is that not all household members (e.g. children, people with other duties) are fulltime labourers, so we went for 2 per field.
        
        self.grain += total_harvest
    
    def storage_loss(self):
        """ Accounts for typical annual storage loss of agricultural product """
        self.grain -= self.grain * 0.1
    
    def consume_grain(self):
        """ Each worker consumes grain. """
        self.grain -= self.workers * ANNUAL_PER_PERSON_GRAIN_CONSUMPTION
        
        if self.grain <= 0:
            self.grain = 0
            self.workers -= 1
            if self.workers <= 0:
                # a household will die off if it has no workers left
                self.settlement.households.remove(self)
                self.settlement.model.households.remove(self)
                self.release_field_claim()
    
    def population_shift(self):
        """ Increase population stochastically in proportion to the population growth rate """
        populate_chance = self.settlement.random.uniform(0, 1)
        # criteria for increasing population as per netLogo implementation
        if (compute_total_population(self.settlement.model) <= \
                (self.settlement.model.starting_population * (1 + self.settlement.model.population_growth_rate) ** self.settlement.model.ticks)) \
                and (populate_chance > 0.5):
            
            self.workers += 1
    
    def generation_changeover(self):
        """ Change competency and ambition values every 10-15 years to simulate a new head of household """
        # Note: this routine is as per the netlogo implementation but is wildly inefficient.
        self.generation_changeover_countdown -= 1
        if self.generation_changeover_countdown <= 0:
            # reset generation changeover countdown
            self.generation_changeover_countdown = self.settlement.random.randint(10, 14)
            
            ambition_change = self.settlement.random.uniform(0, self.settlement.model.generational_variation)
            decrease_chance = self.settlement.random.uniform(0, 1)
            if decrease_chance < 0.5:
                ambition_change *= -1
            new_ambition = self.ambition + ambition_change
            while new_ambition > 1 or new_ambition < self.settlement.model.min_ambition:
                ambition_change = self.settlement.random.uniform(0, self.settlement.model.generational_variation)
                decrease_chance = self.settlement.random.uniform(0, 1)
                if decrease_chance < 0.5:
                    ambition_change *= -1
                new_ambition = self.ambition + ambition_change
            self.ambition = new_ambition
            
            competency_change = self.settlement.random.uniform(0, self.settlement.model.generational_variation)
            decrease_chance = self.settlement.random.uniform(0, 1)
            if decrease_chance < 0.5:
                competency_change *= -1
            new_competency = self.competency + competency_change
            while new_competency > 1 or new_competency < self.settlement.model.min_competency:
                competency_change = self.settlement.random.uniform(0, self.settlement.model.generational_variation)
                decrease_chance = self.settlement.random.uniform(0, 1)
                if decrease_chance < 0.5:
                    competency_change *= -1
                new_competency = self.competency + competency_change
            self.competency = new_competency
    
    def claim_fields(self):
        """Allows households to decide (function of the field productivity compared to existing fields and ambition) to claim/ not claim fields that fall within their knowledge radii"""
        claim_chance = self.settlement.random.uniform(0, 1)  # set random value between 0 and 1
        if (claim_chance < self.ambition) and (self.workers > len(self.fields)) or (len(self.fields) <= 1):
            best_X_fertility = 0
            best_Y_fertility = 0
            best_fertility = -1
            
            household_x, household_y = self.settlement.pos
            xmin = household_x - self.settlement.model.knowledge_radius
            ymin = household_y - self.settlement.model.knowledge_radius
            xmax = household_x + self.settlement.model.knowledge_radius
            ymax = household_y + self.settlement.model.knowledge_radius
            
            # make sure x and y don't fall outside of grid
            xmin = max(xmin, 0)  # if xmin less than zero, set to 0, else leave as xmin
            ymin = max(ymin, 0)
            xmax = min(xmax, self.settlement.model.grid.width)
            ymax = min(ymax, self.settlement.model.grid.height)
            
            for field_x in range(xmin, xmax):
                for field_y in range(ymin, ymax):
                    if (field_x - household_x) ** 2 + (field_y - household_y) ** 2 <= self.settlement.model.knowledge_radius ** 2:
                        
                        if self.settlement.model.grid.fertility[field_y][
                            field_x] > best_fertility and self.settlement.model.grid.is_cell_empty((field_x, field_y,)):
                            best_X_fertility = field_x
                            best_Y_fertility = field_y
                            best_fertility = self.settlement.model.grid.fertility[field_y][field_x]
            
            # best_X and best_Y = the best field to take in knowledge radius
            if best_fertility > 0:
                self.complete_claim(best_X_fertility, best_Y_fertility)
    
    def complete_claim(self, x, y):
        """Once household determines whether or not to claim ownership, this methods sets new ownership"""
        field = FieldAgent(str(self.settlement.random.uniform(0, 1)), self.settlement.model, self)
        self.settlement.model.grid.position_agent(field, x, y)
        self.fields.append(field)
        self.settlement.model.fields.append(field)
    
    def release_field_claim(self):
        """Once a household dies field claims are released """
        for field in self.fields:
            self.settlement.model.grid.remove_agent(field)
            self.settlement.model.fields.remove(field)
    
    def rent_land(self):
        """if global variable 'rent land' is on, ambitious households ae allowed to farm additional plots they don't own, after everyone has finished main farming/harvesting """
        total_harvest = 0
        
        for i in range((self.workers - self.workers_worked) // 2):
            best_harvest = 0
            best_field = None
            
            household_x, household_y = self.settlement.pos
            xmin = household_x - self.settlement.model.knowledge_radius
            ymin = household_y - self.settlement.model.knowledge_radius
            xmax = household_x + self.settlement.model.knowledge_radius
            ymax = household_y + self.settlement.model.knowledge_radius
            
            # make sure x and y don't fall outside of grid
            xmin = max(xmin, 0)  # if xmin less than zero, set to 0, else leave as xmin
            ymin = max(ymin, 0)
            xmax = min(xmax, self.settlement.model.grid.width)
            ymax = min(ymax, self.settlement.model.grid.height)
            
            for field_x in range(xmin, xmax):
                for field_y in range(ymin, ymax):
                    if (field_x - household_x) ** 2 + (field_y - household_y) ** 2 <= self.settlement.model.knowledge_radius ** 2:
                        field_cell = self.settlement.model.grid.get_cell_list_contents((field_x, field_y))
                        if field_cell and isinstance(field_cell[0], FieldAgent):
                            
                            this_harvest = ((self.settlement.model.grid.fertility[field_y][field_x] * PATCH_MAX_POTENTIAL_YIELD * self.competency) - \
                                            sqrt((field_x - household_x) ** 2 + (field_y - household_y) ** 2) * self.settlement.model.distance_cost)
                            
                            if not field_cell[0].harvested and this_harvest >= best_harvest:
                                best_harvest = this_harvest
                                best_field = field_cell[0]
            
            harvest_chance = self.settlement.random.uniform(0, 1)
            if best_field is not None and best_field not in self.fields and harvest_chance < (self.competency * self.ambition):
                best_field.harvested = True
                total_harvest += ((best_harvest * (1 - self.settlement.model.land_rental_rate)) - SEEDING_COST)  # renter bears seeding cost
                
                best_field.household.grain += best_harvest * self.settlement.model.land_rental_rate  # seller makes a profit
        
        self.grain += total_harvest


class EgyptGrid(SingleGrid):
    """A MESA grid containing the fertility values for patches of land."""
    
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
        # see https://en.wikipedia.org/wiki/Normal_distribution
        # the mean and standard deviation value ranges are according to NetLogo source code
        mu = self.random.randint(5, 14)
        sigma = self.random.randint(5, 9)
        alpha = 2 * sigma ** 2
        beta = 1 / (sigma * sqrt(2 * pi))
        # as per NetLogo code
        for x in range(self.width):
            # assign fertility value to column x
            self.fertility[:, x] = 17 * (beta * (e ** (-(x - mu) ** 2 / alpha)))


class EgyptModel(Model):
    """An agent-based model of Pre-Dynastic Egypt"""
    
    def __init__(self, w, h,
                 starting_settlements=14,
                 starting_households=7,
                 starting_household_size=5,
                 starting_grain=2000,
                 min_competency=0.5,
                 min_ambition=0.1,
                 population_growth_rate=0.1,
                 generational_variation=0.9,
                 knowledge_radius=20,
                 fallow_limit=4,
                 distance_cost=10,
                 land_rental_rate=0.5,
                 allow_rental=True):
        self.land_rental_rate = land_rental_rate
        self.allow_rental = allow_rental
        self.starting_settlements = starting_settlements
        self.starting_households = starting_households
        self.starting_household_size = starting_household_size
        self.starting_grain = starting_grain
        self.min_competency = min_competency
        self.min_ambition = min_ambition
        self.population_growth_rate = population_growth_rate
        self.starting_population = starting_settlements * starting_households * starting_household_size
        self.generational_variation = generational_variation
        self.knowledge_radius = knowledge_radius
        self.fallow_limit = fallow_limit
        self.distance_cost = distance_cost
        self.ticks = 0
        
        # Create scheduler
        self.schedule = RandomActivation(self)
        # Create grid
        self.grid = EgyptGrid(w, h, self)
        self.running = True  # BatchRunner set true
        
        self.settlements = []
        self.households = []
        self.fields = []
        
        # Create agents
        for i in range(self.starting_settlements):
            agent = SettlementAgent(
                unique_id=i,
                num_households=starting_households,
                starting_household_size=starting_household_size,
                starting_grain=starting_grain,
                min_competency=min_competency,
                min_ambition=min_ambition,
                model=self
            )
            self.settlements.append(agent)
            self.grid.position_agent(agent)  # place agent in a random empty patch
            # data collection
            self.datacollector = DataCollector(
                model_reporters={'Gini': compute_gini,
                                 'Total Population': compute_total_population,
                                 'Mean Settlement Population': compute_mean_population,
                                 "Total Wealth": compute_total_wealth,
                                 "Mean Settlement Wealth": compute_mean_wealth})
    
    def step(self):
        """Advance the model by one tick."""
        self.grid.flood()
        
        for household in sorted(self.households, key=lambda household: household.grain, reverse=True):
            household.claim_fields()
        
        for household in self.households:
            household.farm()
        
        if self.allow_rental:
            for household in sorted(self.households, key=lambda household: household.ambition, reverse=True):
                household.rent_land()
        
        for household in self.households:
            household.consume_grain()
        
        for household in self.households:
            household.storage_loss()
        
        for field in self.fields:
            field.changeover()
        
        for household in self.households:
            household.storage_loss()
        
        for household in self.households:
            household.generation_changeover()
        
        for household in self.households:
            household.population_shift()
        
        self.ticks += 1
        self.datacollector.collect(self)
