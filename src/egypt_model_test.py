import egypt_model
import unittest


class TestAggregateMethods(unittest.TestCase):

    def test_aggregates(self):
        model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.assertEqual(egypt_model.compute_total_population(model), 9 * 5 * 5)
        self.assertEqual(egypt_model.compute_total_wealth(model), 9 * 5 * 1000)
        self.assertEqual(egypt_model.compute_mean_population(model), 5 * 5)
        self.assertEqual(egypt_model.compute_mean_wealth(model), 5 * 1000)

        model = egypt_model.EgyptModel(31, 30, starting_settlements=0, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.assertEqual(egypt_model.compute_total_population(model), 0)
        self.assertEqual(egypt_model.compute_total_wealth(model), 0)
        self.assertEqual(egypt_model.compute_mean_population(model), 0)
        self.assertEqual(egypt_model.compute_mean_wealth(model), 0)

        model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=0, starting_household_size=5, starting_grain=1000)
        self.assertEqual(egypt_model.compute_total_population(model), 0)
        self.assertEqual(egypt_model.compute_total_wealth(model), 0)
        self.assertEqual(egypt_model.compute_mean_population(model), 0)
        self.assertEqual(egypt_model.compute_mean_wealth(model), 0)

        model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=0, starting_grain=1000)
        self.assertEqual(egypt_model.compute_total_population(model), 0)
        self.assertEqual(egypt_model.compute_total_wealth(model), 9 * 5 * 1000)
        self.assertEqual(egypt_model.compute_mean_population(model), 0)
        self.assertEqual(egypt_model.compute_mean_wealth(model), 5 * 1000)

class TestSettlementMethods(unittest.TestCase):

    def setUp(self):
        self.model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.settlement = self.model.settlements[0]

    def test_settlement_workers(self):
        self.assertEqual(self.settlement.workers(), 5*5)

        for household in self.settlement.households:
            household.workers += 1
        self.assertEqual(self.settlement.workers(), 5*6)

        self.settlement.households.remove(self.settlement.households[0])
        self.assertEqual(self.settlement.workers(), 4*6)

    def test_settlement_grain(self):
        self.assertEqual(self.settlement.grain(), 5*1000)

        for household in self.settlement.households:
            household.grain += 1
        self.assertEqual(self.settlement.grain(), 5*1001)

        self.settlement.households.remove(self.settlement.households[0])
        self.assertEqual(self.settlement.grain(), 4*1001)

class TestHouseholdMethods(unittest.TestCase):

    def setUp(self):
        self.model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.household = self.model.households[0]
        self.assertEqual(self.household.grain, 1000)

    def test_workers(self):
        self.assertEqual(self.household.workers, 5)
        self.assertEqual(self.household.workers_worked, 0)

    def test_storage_loss(self):
        grain = 1000
        self.household.grain = grain

        self.household.storage_loss()
        grain -= grain * 0.1
        self.assertEqual(self.household.grain, grain)

        self.household.storage_loss()
        grain -= grain * 0.1
        self.assertEqual(self.household.grain, grain)

        self.household.storage_loss()
        grain -= grain * 0.1
        self.assertEqual(self.household.grain, grain)

    def test_consume_grain(self):
        workers = 5
        grain = workers * egypt_model.ANNUAL_PER_PERSON_GRAIN_CONSUMPTION + 1
        self.household.grain = grain
        self.household.workers = workers
        self.household.consume_grain()
        self.assertEqual(self.household.grain, grain - workers * egypt_model.ANNUAL_PER_PERSON_GRAIN_CONSUMPTION)
        self.assertEqual(self.household.workers, workers)

        grain = workers * egypt_model.ANNUAL_PER_PERSON_GRAIN_CONSUMPTION
        self.household.grain = grain
        self.household.workers = workers
        self.household.consume_grain()
        self.assertEqual(self.household.grain, 0)
        self.assertEqual(self.household.workers, workers - 1)

        workers = 5
        grain = workers * egypt_model.ANNUAL_PER_PERSON_GRAIN_CONSUMPTION - 1
        self.household.grain = grain
        self.household.workers = workers
        self.household.consume_grain()
        self.assertEqual(self.household.grain, 0)
        self.assertEqual(self.household.workers, workers - 1)

    def test_competency_increase(self):
        self.household.competency = 0.5
        self.model.annual_competency_increase = 5
        self.assertEqual(self.household.competency, 0.5)

        self.household.competency_increase()
        self.assertEqual(self.household.competency, 0.525)

        self.household.competency_increase()
        self.assertEqual(self.household.competency, 0.55125)

        self.model.annual_competency_increase = 0
        self.household.competency_increase()
        self.assertEqual(self.household.competency, 0.55125)

    def test_generation_changeover(self):
        self.model.min_ambition = 0.2
        self.model.min_competency = 0.5
        self.household.generation_changeover_countdown = 3
        self.household.competency = 0.8
        self.household.ambition = 0.4

        self.household.generation_changeover()
        self.assertEqual(self.household.competency, 0.8)
        self.assertEqual(self.household.ambition, 0.4)

        self.household.generation_changeover()
        self.assertEqual(self.household.competency, 0.8)
        self.assertEqual(self.household.ambition, 0.4)

        self.household.generation_changeover()
        self.assertNotEqual(self.household.competency, 0.8)
        self.assertNotEqual(self.household.competency, 0.4)
        self.assertTrue(self.household.competency >= 0.5 and self.household.competency <= 1)
        self.assertTrue(self.household.ambition >= 0.2and self.household.ambition <= 1)

class TestFieldMethods(unittest.TestCase):

    def setUp(self):
        self.model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.model.fallow_limit = 10
        self.household = self.model.households[0]
        self.field = egypt_model.FieldAgent(1, self.model, self.household)
        self.household.fields.append(self.field)
        self.model.fields.append(self.field)
        self.model.grid.position_agent(self.field, 0,0)

        self.assertEqual(self.field.unique_id, 1)
        self.assertEqual(self.field.years_fallowed,0)
        self.assertFalse(self.field.harvested)

    def test_changeover(self):
        for i in range(10):
            self.field.harvested = True
            self.field.changeover()
        self.assertEqual(self.field.years_fallowed, 0)
        self.assertEqual(self.household, self.field.household)

        for i in range(9):
            self.field.changeover()
        self.assertEqual(self.field.years_fallowed, 9)
        self.assertEqual(self.household, self.field.household)

        self.field.changeover()
        self.assertEqual(self.field.years_fallowed, self.model.fallow_limit)
        self.assertTrue(self.field not in self.household.fields)
        self.assertTrue(self.field not in self.model.fields)

if __name__ == '__main__':
    unittest.main()
