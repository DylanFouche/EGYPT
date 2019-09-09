import numpy as np
import pandas as pd
import statsmodels.api as sm
import math
from matplotlib import pyplot as plt

metric_pairs = [
    ('python-total-population', 'netlogo-total-population'),
    ('python-total-wealth', 'netlogo-total-wealth'),
    ('python-gini', 'netlogo-gini-index-reserve')
]


def compare(O, E):
    """Returns a similarity score for corresponding elements in O and E"""
    return (O - E) / E


# read csv file
data = pd.read_csv('src/validation/output.csv', delimiter=',', skipinitialspace=True)

feature_column_names = data.keys()[1:11]

# when there are numerous repeats of each set of parameters/features take the mean of the results from each set
groups = data.groupby(list(feature_column_names), as_index=False)
data = groups.mean()

# numpy array of X values for regression
X = data[feature_column_names].values

# remove features that were never changed (e.g. if only one value for starting-households was tested)
feature_column_names = feature_column_names[X.std(axis=0) != 0]
X = X[:, X.std(axis=0) != 0]

# normalise X values
X = (X - X.mean(axis=0)) / X.std(axis=0)

# set up plot
fig, ax = plt.subplots(2, len(metric_pairs), sharex='col', sharey='row', figsize=plt.figaspect(0.55))
ax[1][0].set_ylabel('-log(p-value)')
ax[0][0].set_ylabel('coefficient')

for i, metric_pair in enumerate(metric_pairs):
    # numpy array of Y values for regression
    Y = compare(data[metric_pair[0]].values, data[metric_pair[1]].values)
    
    # Normalise Y values
    Y = (Y - Y.mean(axis=0)) / Y.std(axis=0)
    
    # run regression
    est = sm.OLS(Y, sm.add_constant(X)).fit()
    
    # remove p-values and coefficients for the regression constant
    p_values = est.pvalues[np.array(est.model.data.param_names) != 'const']
    parameters = est.params[np.array(est.model.data.param_names) != 'const']
    
    # -log(p-value)
    lp = [-math.log10(pv) for pv in p_values]
    
    # plot results
    ax[0][i].set_title(metric_pair[0] + '/\n' + metric_pair[1])
    ax[0][i].scatter(range(len(lp)), parameters)
    ax[0][i].axhline(y=0, color='r', linestyle='--')
    ax[1][i].scatter(range(len(lp)), lp)
    ax[1][i].set_xticks(range(len(lp)))
    ax[1][i].set_xticklabels(feature_column_names, rotation=270)

plt.tight_layout()
plt.subplots_adjust(wspace=0.4)
plt.savefig('src/validation/regression.pdf', format='pdf')
plt.show()
