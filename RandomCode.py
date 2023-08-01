import numpy as np
import pandas as pd
import itertools
from pulp import *

route_matrix = np.loadtxt(open("Route_Matrix_Weekday.csv"), delimiter=",", skiprows=0)
route_time_vector = np.loadtxt(open("Route_Times_Weekday.csv"), delimiter=",", skiprows=0)
route_pallets_vector = np.loadtxt(open("Route_Pallets_Weekday.csv"), delimiter=",", skiprows=0)

# Obtain the number of stores and potential routes to use
n_stores, n_routes = np.shape(route_matrix)

print(n_stores, n_routes)





