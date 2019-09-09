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
