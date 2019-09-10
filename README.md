# EGYPT
An Agent-Based Simulation of Predynastic Egypt.

## Quick start
Run the following command from the project root directory to install and launch the simulation:

```bash
python3 run_simulation.py [grid_width] [grid_height]
```

Note that the default width and height values are 31 and 30 respectively.

## General Usage

### 1. Install requirements
```bash
pip3 install -r requirements.txt
```

### 2. Append src directory to PYTHONPATH
```bash
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/src
```

### 3. Run simulation
```bash
python3 src/simulations/gui_simulation.py [grid_width] [grid_height]
```

## Validation

### 1. Run NetLogo BehaviourSpace simulations

Open the NetLogo file in the validation_output directory.

Click tools->BehaviourSpace.

Scroll down to and run the "capstone" experiment.

Make sure only the "table output" checkbox is checked.

Save the table csv file to ```validation_output/revised Egypt model 2019 no GIS Capstone-table.csv```

### 2. Run Python simulations

```bash
python3 src/validation/run_simulations.py
```

Note that this may take around 3 hours.

### 3. Run regression analysis

```bash
python3 src/validation/regression.py
```

This will generate, display and save the visualisation of the analysis.