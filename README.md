# EGYPT
CSC3002S Capstone Project

## Quick start
Run the following commands from the project root directory.

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
python3 src/simulations/single_simulation.py 100 100 31 30
```

## Usage

```bash 
python3 src/simulations/single_simulation.py [num_agents] [num_steps] [grid_width] [grid_height]
```
Note that the default width and height values from the NetLogo source are 31 and 30 respectively.