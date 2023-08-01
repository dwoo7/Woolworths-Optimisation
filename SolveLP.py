import numpy as np
from numpy.core.einsumfunc import _einsum_path_dispatcher
from numpy.lib.nanfunctions import _nanprod_dispatcher
import pandas as pd
import itertools
from pulp import *
import csv

# Read in the route matrix, route times and route pallet demands
#route_matrix = np.loadtxt(open("Binary_Route_Matrix.csv"), delimiter=",", skiprows=0)
#route_time_vector = np.loadtxt(open("Route_Times.csv"), delimiter=",", skiprows=0)
#route_pallets_vector = np.loadtxt(open("Route_Pallets.csv"), delimiter=",", skiprows=0)

# Create a dictionary for the problem costs
Cost_Parameters = {'NumTrucks' : 30, 
                   'TruckPallets' : 26,
                   'AverageRouteTime' : 14400,
                   'TruckHourlyCost' : 225,
                   'ExtraTruckTime' : 275,
                   'TruckShift' : 14400,
                   'ExtraTimeCost' : 11/144,
                   'WetLeasedCost' : 2000,
                   'MaxRouteTime' : 18000}

#########################################################################################

def solveLP(Weekday):

    # Read in route data
    if Weekday == True:
        route_name_data = pd.read_csv("Store_Data_Nonzero_GROUPED.csv")
        route_matrix = np.loadtxt(open("Route_Matrix_Weekday.csv"), delimiter=",", skiprows=0)
        route_time_vector = np.loadtxt(open("Route_Times_Weekday.csv"), delimiter=",", skiprows=0)
        route_pallets_vector = np.loadtxt(open("Route_Pallets_Weekday.csv"), delimiter=",", skiprows=0)
    else:
        route_name_data = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")
        route_matrix = np.loadtxt(open("Route_Matrix_Weekend.csv"), delimiter=",", skiprows=0)
        route_time_vector = np.loadtxt(open("Route_Times_Weekend.csv"), delimiter=",", skiprows=0)
        route_pallets_vector = np.loadtxt(open("Route_Pallets_Weekend.csv"), delimiter=",", skiprows=0)

    # Obtain the number of stores and potential routes to use
    n_stores, n_routes = np.shape(route_matrix)

    # List of route labels
    Routes = [str(i) for i in range(n_routes)]
    Extra_Routes = [str(i) for i in range(n_routes)]


    # Obtain cost of each route
    route_costs = np.zeros(n_routes)
    for i in range(n_routes):
        if route_time_vector[i] < Cost_Parameters['TruckShift']:
            route_costs[i] = route_time_vector[i] * Cost_Parameters['TruckHourlyCost']/(60**2)
        else:
            route_costs[i] = (Cost_Parameters['TruckShift'])*(Cost_Parameters['TruckHourlyCost']/(60**2)) + (route_time_vector[i] - Cost_Parameters['TruckShift']) * (Cost_Parameters['ExtraTruckTime']/(60**2))

    # Creating the problem
    prob = LpProblem("PalletProblem", LpMinimize)

    # The problem variables for whether each route is used
    vars = LpVariable.dicts("Route", Routes, cat = "Binary")                # Normal trucks
    extra_vars = LpVariable.dicts("ExRoute", Extra_Routes, cat = "Binary")  # Rental trucks
    # Variables for number of trucks
    n_trucks = LpVariable("NumTrucks", 0, 2*Cost_Parameters['NumTrucks'], LpInteger)
    # Number of 4h rental block periods
    N_lease = LpVariable("NumExtraTrucks", 0, None, LpInteger)
    # Total number of routes used
    num_routes_used = LpVariable("NumR", 0, None, LpInteger)

    # Objective function (total no. of routes used * cost of each route)
    prob += lpSum([vars[str(i)] * route_costs[i] for i in range(n_routes)]) + Cost_Parameters['WetLeasedCost'] * N_lease, "Cost of transporting pallets"

    # Constraint for one route per node
    if Weekday == True:
        for i in range(n_stores):
            prob += lpSum([(vars[str(j)] + extra_vars[str(j)]) * route_matrix[i][j] for j in range(n_routes)]) == 1
    else:
        for i in range(n_stores):
            storename = route_name_data['Store'].iloc[i]
            if "Countdown" in storename and "Metro" not in storename:
                prob += lpSum([(vars[str(j)] + extra_vars[str(j)]) * route_matrix[i][j] for j in range(n_routes)]) == 1
            else:
                prob += lpSum([(vars[str(j)] + extra_vars[str(j)]) * route_matrix[i][j] for j in range(n_routes)]) == 0
        
    # Max 4 hours per route, on average
    prob += lpSum(vars[str(i)] * route_time_vector[i] - Cost_Parameters["AverageRouteTime"] * vars[str(i)] for i in range(n_routes)) <= 0

    # Conostraint on extra time spent by rental trucks
    prob += lpSum([extra_vars[str(i)] * route_time_vector[i] for i in range (n_routes)]) <= 14400 * N_lease

    # No normal truck route can exceed 5h, to allow for reasonable shift times
    for i in range(n_routes):
        prob += vars[str(i)] * route_time_vector[i] <= Cost_Parameters["MaxRouteTime"]

    # Constraint on pallet demand for normal trucks
    for i in range(n_routes):
        if Weekday == True:
            prob += vars[str(i)] * route_pallets_vector[i] <= Cost_Parameters["TruckPallets"] - 6
        else:
            prob += vars[str(i)] * route_pallets_vector[i] <= Cost_Parameters["TruckPallets"] - 3

    # Number of trucks constraints
    prob += lpSum(vars[str(i)] for i in range(n_routes)) == n_trucks
    prob += n_trucks <= 2 * Cost_Parameters["NumTrucks"]
    prob += lpSum([vars[str(i)] + extra_vars[str(i)] for i in range(n_routes)]) == num_routes_used


    ### Solve and print output ###

    #Writing the problem data to an lp file
    prob.writeLP("PalletProblem.lp")

    #Solving the problem
    prob.solve(PULP_CBC_CMD(msg=0))

    # Number of trucks used pinted to the screen
    print("Number of Trucks used: ", n_trucks.varValue)
    print("Number of 4-hour periods leased: ", N_lease.varValue)
    print("Number of routes used: ", num_routes_used.varValue)    

    #Optimised objective function value printed to the screen
    if Weekday == True:
        print("Cost of Transporting Pallets [1 Weekday, all stores open] = $%.2f" % value(prob.objective))
    else:
        print("Cost of Transporting Pallets [1 Weekend day, only Countdown open] = $%.2f" % value(prob.objective))

    # Print all routes used
    count = 0
    counter = 0
    routeNumbers = np.empty((0,1), int)
    routeStores = np.empty((0, n_stores), int)
    print()
    print("\nList of routes used in optimal solution:")
    for v in prob.variables():
        if type(v.varValue) != None and "Route" in v.name:
            if v.varValue > 0:

                # Obtain route number and stores visited, and add to string
                route_number = int(v.name.split('_')[1])
                route_info = route_matrix[:, route_number]
                indices = np.where(route_info == 1)[0]
                names = ""

                for i in indices:
                    if i < 55:
                        names += "  " + route_name_data.iloc[i, 1]
                    else:
                        names += "  " + route_name_data.iloc[i+1, 1]

                    count += 1

                print(v.name + ", DELIVERING TO:   " + names)

                # Recording the routes used in solution so that it can be plotted
                routeNumbers = np.append(routeNumbers, route_number)
                routeStores = np.vstack([routeStores, np.array(route_info)])

                counter += 1
            

    # Saving the route indices for use in visualising
    if Weekday == True:
        np.savetxt("RouteVector_Weekday.csv", routeNumbers, delimiter=',')
        np.savetxt("RouteStore_Weekday.csv", routeNumbers, delimiter=',')
    else:
        np.savetxt("RouteVector_Weekend.csv", routeNumbers, delimiter=',')
        np.savetxt("RouteStore_Weekday.csv", routeNumbers, delimiter=',')


    allvisited = "False"
    if (Weekday == True and count == 65) or (Weekday == False and count == 53):
        allvisited = "True"
    print(count, " stores visited - all visited = ", allvisited)

    #Status of the problem is printed to the screen
    print("Status:", LpStatus[prob.status])
    print("\n")


if __name__ == "__main__":

    solveLP(Weekday=True)
    solveLP(Weekday=False)
