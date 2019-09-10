import csv
from egypt_model import EgyptModel
import multiprocessing
import egypt_model

data = []

with open('validation_output/revised Egypt model 2019 no GIS Capstone-table.csv', 'r') as file:
    reader = csv.reader(file, skipinitialspace=True)
    for line in reader:
        data.append(line)

# read grid size from NetLogo generated file
width = int(data[5][1]) - int(data[5][0])  # max-pxcor - min-pxcor
height = int(data[5][3]) - int(data[5][2])  # max-pycar - min-pycor

headings = data[6]
data = data[7:]  # "real" data is from row 7 onwards

run_index = headings.index('[run number]')
step_index = headings.index('[step]')

# NetLogo generates csv rows for every step in every simulation
# We only want the final step of each simulation
# Therefore, for each unique set of parameters keep only the run with the highest step number

temp = {}

for row in data:
    row[run_index] = int(row[run_index])
    row[step_index] = int(row[step_index])
    run = row[run_index]
    if run in temp:
        if temp[run][step_index] < row[step_index]:
            temp[run] = row
    else:
        temp[run] = row

runs = []
for key in sorted(temp):
    runs.append(temp[key])

# output file to save results to

f = open('validation_output/output.csv', 'w')

f.write(', '.join(headings[:step_index + 1] + ['python-gini', 'netlogo-gini-index-reserve', 'python-total-population',
                                               'netlogo-total-population', 'python-total-wealth',
                                               'netlogo-total-wealth']) + '\n')


def simulate(run):
    """
    Runs a simulation with the parameters specified in the 'run' row from NetLogo generated csv file
    :return Returns an array containing the parameters and results of the Python and NetLogo simulations
    """
    # read simulation parameters from "run" row taken from csv
    model = EgyptModel(
        w=width,
        h=height,
        starting_settlements=int(run[headings.index('starting-settlements')]),
        starting_households=int(run[headings.index('starting-households')]),
        starting_household_size=int(run[headings.index('starting-household-size')]),
        starting_grain=int(run[headings.index('starting-grain')]),
        min_competency=float(run[headings.index('min-competency')]),
        min_ambition=float(run[headings.index('min-ambition')]),
        population_growth_rate=float(run[headings.index('pop-growth-rate')]),
        generational_variation=float(run[headings.index('generational-variation')]),
        knowledge_radius=int(run[headings.index('knowledge-radius')]),
        fallow_limit=int(run[headings.index('fallow-limit')]),
        distance_cost=int(run[headings.index('distance-cost')]),
        land_rental_rate=int(run[headings.index('land-rental-rate')])/100,
        allow_rental=run[headings.index('allow-land-rental?')] == 'true'
    )
    
    num_steps = int(run[step_index])
    
    for i in range(num_steps):
        model.step()
    
    python_gini = egypt_model.compute_gini(model)
    python_population = egypt_model.compute_total_population(model)
    python_wealth = egypt_model.compute_total_wealth(model)
    
    netlogo_gini = float(run[headings.index('gini-index-reserve / total-households / 0.5')])
    netlogo_population = int(run[headings.index('total-population')])
    netlogo_wealth = float(run[headings.index('total-grain')])
    
    # append results to the row containing the parameters
    return run[:step_index + 1] + [python_gini, netlogo_gini, python_population, netlogo_population, python_wealth,
                                   netlogo_wealth]

# use multiprocessing to speed up the process by running simulations in parallel.
p = multiprocessing.Pool(multiprocessing.cpu_count())
results = p.map(simulate, runs)

# write the results to a file
for result in results:
    f.write(', '.join([str(x) for x in result]) + '\n')

f.close()
