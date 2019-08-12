import sys
import egypt_gui

# get command line params
if len(sys.argv) != 3:
    print("Usage:\tpython3 src/simulations/gui_simulation.py [grid_width] [grid_height]")
    quit()
else:
    grid_width = int(sys.argv[1])
    grid_height = int(sys.argv[2])

egypt_gui.launch(grid_width, grid_height)
