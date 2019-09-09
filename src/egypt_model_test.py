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


class TestHouseholdMethods(unittest.TestCase):
    def setUp(self):
        model = egypt_model.EgyptModel(31, 30, starting_settlements=9, starting_households=5, starting_household_size=5, starting_grain=1000)
        self.household = model.households[0]
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


if __name__ == '__main__':
    unittest.main()
