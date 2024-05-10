# import math
# from scipy.optimize import minimize
# from scipy.optimize import differential_evolution
# #NAJDI 3
# # volumetric_water_content = [0.763, 0.730, 0.683, 0.655, 0.617, 0.596, 0.561,
# #                             0.552, 0.540, 0.539, 0.507, 0.440, 0.400, 0.368, 0.300, 0.262, 0.208]
# # volumetric_water_content = [0.891,
# # 0.849,
# # 0.801,
# # 0.798,
# # 0.768,
# # 0.678,
# # 0.549,
# # 0.496]
# # volumetric_water_content = [24.16,
# # 24.15,
# # 23.97,
# # 23.77,
# # 22.36,
# # 19.06,
# # 18.01,
# # 17.77,
# # 17.01,
# # 15.19,
# # 13.92,
# # 12.05,
# # 10.32,
# # 9.46,
# # 8.95]
# # psi_array = [0.1,
# # 1,
# # 5,
# # 6,
# # 10,
# # 35,
# # 80,
# # 100,
# # 250,
# # 1000,
# # 2000,
# # 5000,
# # 11000,
# # 16000,
# # 20000]
# #NAJDI 1
# volumetric_water_content = [0.875,
# 0.854907539,
# 0.80227596,
# 0.770981508,
# 0.773826458,
# 0.681365576,
# 0.549075391]
# # psi_array = [4.509340013, 6.956939649, 13.03062697, 19.4269383, 37.22736007, 55.50106137, 110.0589516, 164.0833145,
# #              236.3944438, 340.5729169, 1501.109209, 2843.90292, 4752.343561, 6541.224706, 10443.12618, 19784.86098, 32315.82612]
# #NAJDI 2
# # psi_array = [43.57066006,
# # 62.35507341,
# # 93.08173481,
# # 136.0503407,
# # 201.567,
# # 278.6473679,
# # 1144.479607,
# # 1938.857038]
# #NAJDI 3
# psi_array = [41.06846236,
# 61.64085697,
# 92.51856606,
# 131.8484555,
# 215.7539345,
# 270.0969623,
# 1085.543621]
# tetta_max = 0.867826465297161
#
#
# tetta_mid = tetta_max/2
# tetta_min = 0.01
# psi_ws1 = 2
# psi_ws2 = 10
# psi_we2 = 10
# psi_max = 10
# psi_wd = 10
#
#
# # def third_form(psi, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
# #     global psi_wd
# #     psi_wd = 0
# #     psi_wd = psi_ws1**0.3 * psi_ws2**0.7
# #     if psi < psi_ws1:
# #         first_exp = math.exp(0)
# #     else:
# #         first_exp = round(math.exp((-4.75 * ((psi - psi_ws1) / (psi_wd - psi_ws1)))),2)
# #     if psi<psi_ws2:
# #         second_exp = math.exp(0)
# #     else:
# #         second_exp = round(math.exp((-4.75*((psi-psi_ws2)/(psi_max-psi_ws2)))),2)
# #     CF =round((1-(math.log(1+psi/psi_we2))/math.log(1+(10**6)/psi_we2)), 4)
# #
# #     tetta = round(((tetta_max-tetta_mid) * first_exp + (tetta_mid-tetta_min) *second_exp +tetta_min) * CF , 3)
# #     return tetta
#
# def third_form(psi, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
#     global psi_wd
#     psi_wd = psi_ws1 ** 0.3 * psi_ws2 ** 0.7
#
#     # Clip function to prevent overflow
#     def safe_exp(x):
#         max_exp_arg = 700  # Define a max value to prevent overflow
#         return math.exp(max(-max_exp_arg, min(x, max_exp_arg)))
#
#     if psi < psi_ws1:
#         first_exp = safe_exp(0)
#     else:
#         first_exp_arg = (-4.75 * ((psi - psi_ws1) / (psi_wd - psi_ws1)))
#         first_exp = round(safe_exp(first_exp_arg), 2)
#
#     if psi < psi_ws2:
#         second_exp = safe_exp(0)
#     else:
#         second_exp_arg = (-4.75 * ((psi - psi_ws2) / (psi_max - psi_ws2)))
#         second_exp = round(safe_exp(second_exp_arg), 2)
#
#     CF = round((1 - (math.log(1 + psi / psi_we2)) / math.log(1 + (10 ** 6) / psi_we2)), 4)
#
#     tetta = round(((tetta_max - tetta_mid) * first_exp + (tetta_mid - tetta_min) * second_exp + tetta_min) * CF, 3)
#     return tetta
#
# # def objective(variables):
# #     tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max= variables
# #     global error_sum
# #     error_sum = 0
# #     for i in range(len(psi_array)):
# #         predicted_water_content = third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max)
# #         error = abs(volumetric_water_content[i] - predicted_water_content)
# #         if error>=0.0001:
# #             error_sum += error  # - >even worse
# #     for i in range(len(psi_array)):
# #         predicted_water_content = third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max)
# #         error = ((volumetric_water_content[i] - predicted_water_content) / volumetric_water_content[i]) ** 2
# #         # print(error)
# #         if error > 0.001:
# #             continue
# #     error_sum += error
# #
# #     return error_sum
#
# def objective(variables):
#     # Calculate the mean squared error (MSE) for simplicity and consistency
#     tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max = variables
#     mse = sum((volumetric_water_content[i] - third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max))**2 for i in range(len(psi_array))) / len(psi_array)
#     return mse
#
# # def objective(variables):
# #     tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max = variables
# #     error_sum = 0
# #     for i in range(len(psi_array)):
# #         predicted_water_content = third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max)
# #         error = ((volumetric_water_content[i] - predicted_water_content) / volumetric_water_content[i]) ** 2
# #         if error > 0.001:
# #             error_sum += error
# #     return error_sum
#
#
# # Perform optimization
#
# # Set initial values for optimization,
# x0 = [tetta_max/2, 0.01, 0.01, 100, 100, 1000]
# bounds = [(tetta_max/2, tetta_max), (0.01, tetta_mid), (0.01, psi_ws2), (100, 1000000), (100, 1000000), (1000, 1000000)]#try 10000
# # bounds = [(tetta_max * 0.5, tetta_max * 1.5), (tetta_min * 0.5, tetta_min * 1.5), (psi_ws1 * 0.5, psi_ws1 * 1.5),
# #           (psi_ws2 * 0.5, psi_ws2 * 1.5), (psi_we2 * 0.5, psi_we2 * 1.5), (psi_max * 0.5, psi_max * 1.5)]
#
#
# #tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max, psi_wd
# # Perform optimization
# # result = minimize(objective, x0, method='Powell', bounds=bounds)
# result = differential_evolution(objective, bounds=bounds)
# #result = minimize(objective, x0, method='SLSQP', bounds=bounds)
#
# opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max = result.x
# print(opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max, psi_wd)
import math
from scipy.optimize import differential_evolution

tetta_max = 0.787218053403778
tetta_mid = tetta_max/2
tetta_min = 0.01
psi_ws1 = 2
psi_ws2 = 10
psi_we2 = 10
psi_max = 10
psi_wd = 10

# Data for volumetric water content and psi values
volumetric_water_content = [0.763,
0.730,
0.683,
0.655,
0.617,
0.596,
0.561,
0.552,
0.540,
0.539,
0.507,
0.440,
0.400,
0.368,
0.300,
0.262,
0.208]
psi_array = [4.509340013,
6.956939649,
13.03062697,
19.4269383,
37.22736007,
55.50106137,
110.0589516,
164.0833145,
236.3944438,
340.5729169,
1501.109209,
2843.90292,
4752.343561,
6541.224706,
10443.12618,
19784.86098,
32315.82612]


# Function to prevent overflow in exponential calculations
def safe_exp(x):
    max_exp_arg = 700  # Define a max value to prevent overflow
    return math.exp(max(-max_exp_arg, min(x, max_exp_arg)))

# Soil water characteristic function with given parameters
def third_form(psi, tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max):
    psi_wd = psi_ws1 ** 0.3 * psi_ws2 ** 0.7  # weighted average of psi_ws1 and psi_ws2

    if psi < psi_ws1:
        first_exp = safe_exp(0)
    else:
        first_exp_arg = (-4.75 * ((psi - psi_ws1) / (psi_wd - psi_ws1)))
        first_exp = round(safe_exp(first_exp_arg), 2)

    if psi < psi_ws2:
        second_exp = safe_exp(0)
    else:
        second_exp_arg = (-4.75 * ((psi - psi_ws2) / (psi_max - psi_ws2)))
        second_exp = round(safe_exp(second_exp_arg), 2)

    CF = round((1 - (math.log(1 + psi / psi_we2)) / math.log(1 + (10 ** 6) / psi_we2)), 4)

    tetta = round(((tetta_max - tetta_mid) * first_exp + (tetta_mid - tetta_min) * second_exp + tetta_min) * CF, 3)
    return tetta

# Objective function to minimize
def objective(variables):
    tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max = variables
    mse = sum((volumetric_water_content[i] - third_form(psi_array[i], tetta_max, tetta_mid, tetta_min, psi_ws1, psi_ws2, psi_we2, psi_max))**2 for i in range(len(psi_array))) / len(psi_array)
    return mse

# Initial guesses and bounds for parameters
x0 = [tetta_max/2, 0.01, 0.01, 100, 100, 1000]
bounds = [(tetta_max/2, tetta_max), (0.01, tetta_max/2), (0.01, 100), (100, 10000), (100, 10000), (1000, 1000000)]

# Perform optimization using differential evolution
result = differential_evolution(
    objective,
    bounds=bounds,
    strategy='best1bin',
    maxiter=100,       # Increased number of iterations
    popsize=15,          # Larger population size to explore more solutions
    tol=1e-10,            # Smaller tolerance for more precise convergence
    mutation=(0.6, 1.2), # Fine-tune mutation
    recombination=0.7,   # Higher recombination rate
    polish=True,         # Enable polishing to refine the final solution
    seed=42              # Optional: Set seed for reproducible results
)

# Extract the optimized parameters
opt_tetta_mid, opt_tetta_min, opt_psi_ws1, opt_psi_ws2, opt_psi_we2, opt_psi_max = result.x

# Print optimized parameters
print("Optimized Parameters:")
print("Theta_mid:", opt_tetta_mid)
print("Theta_min:", opt_tetta_min)
print("Psi_ws1:", opt_psi_ws1)
print("Psi_ws2:", opt_psi_ws2)
print("Psi_we2:", opt_psi_we2)
print("Psi_max:", opt_psi_max)

