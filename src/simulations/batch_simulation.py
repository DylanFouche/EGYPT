from mesa.batchrunner import BatchRunner
import egypt_utils
from egypt_model import EgyptModel, compute_gini

# batchrunner - not quite functioning as I would like
# TODO
fixed_params = {
    "w": 100,
    "h": 100
}
variable_params = {"n": range(10, 100, 10)}
# The variables parameters will be invoke along with the fixed parameters allowing for either or both to be honored.
batch_run = BatchRunner(
    EgyptModel,
    variable_params,
    fixed_params,
    iterations=5,
    max_steps=100,
    model_reporters={"Gini": compute_gini}
)
batch_run.run_all()

egypt_utils.plot_batch_run_variable_graphs(batch_run)
