import math
import numpy as np
from bayes_opt import BayesianOptimization

# Define your data
# volumetric_water_content = [0.875, 0.854907539, 0.80227596, 0.770981508, 0.773826458, 0.681365576, 0.549075391]
volumetric_water_content = [0.891, 0.849, 0.801, 0.798, 0.768, 0.678, 0.549, 0.496]
# psi_array = [41.06846236, 61.64085697, 92.51856606, 131.8484555, 215.7539345, 270.0969623, 1085.543621]
psi_array = [43.57066006,
62.35507341,
93.08173481,
136.0503407,
201.567,
278.6473679,
1144.479607,
1938.857038]
tetta_max = 0.907147006546546

# Define the model function
def third_form(psi, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
    psi_wd = psi_ws1 ** 0.3 * psi_ws2 ** 0.7

    def safe_exp(x):
        # Safe exponent to prevent overflow issues
        max_exp_arg = 700
        return math.exp(max(-max_exp_arg, min(x, max_exp_arg)))

    if psi < psi_ws1:
        first_exp = safe_exp(0)
    else:
        first_exp_arg = -4.75 * ((psi - psi_ws1) / (psi_wd - psi_ws1))
        first_exp = round(safe_exp(first_exp_arg), 2)

    if psi < psi_ws2:
        second_exp = safe_exp(0)
    else:
        second_exp_arg = -4.75 * ((psi - psi_ws2) / (psi_max - psi_ws2))
        second_exp = round(safe_exp(second_exp_arg), 2)

    CF = round((1 - (math.log(1 + psi / psi_we2)) / math.log(1 + (10 ** 6) / psi_we2)), 4)
    tetta = round(((tetta_max - tetta_mid) * first_exp + (tetta_mid - tetta_min) * second_exp + tetta_min) * CF, 3)
    return tetta

# Define the objective function for optimization
def objective(tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
    mse = sum(abs((volumetric_water_content[i] - third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max))) ** 2 for i in range(len(psi_array))) / len(psi_array)
    return -mse  # Minimize MSE by maximizing its negative

# Bounds for variables
pbounds = {
    'tetta_mid': (tetta_max/2, tetta_max),
    'tetta_min': (0.01, tetta_max/2),
    'psi_ws1': (0.01, 100),
    'psi_ws2': (100, 10000),
    'psi_we2': (100, 10000),
    'psi_max': (1000, 100000)
}

# Initialize Bayesian Optimization
optimizer = BayesianOptimization(
    f=objective,
    pbounds=pbounds,
    random_state=1,
)

# Perform optimization
optimizer.maximize(
    init_points=10,  # Increased from 5 to 10 for more thorough initial exploration
    n_iter=100,       # Increased from 25 to 50 for more iterations to fine-tune the parameters
)

# Print the best parameters found
print("Best parameters found: ", optimizer.max['params'])
