#!/usr/bin/python3

import os
import sys
import inspect

if len(sys.argv) != 3:
    print("Usage:\tpython3 run_simulation.py [grid_width] [grid_height]")
    quit()
else:
    grid_width = sys.argv[1]
    grid_height = sys.argv[2]
    run_cmd = "export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/src && python3 src/simulations/gui_simulation.py " + grid_width + " " + grid_height + " > /dev/null"

    print("Checking dependencies...")
    os.system("pip3 install -r requirements.txt > /dev/null")
    print("Launching simulation...")
    os.system(run_cmd)
