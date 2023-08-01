import numpy as np
import pandas as pd
import random

#######################################################################################
###             This script simulates the store demands via bootstrapping           ###
#######################################################################################

def BootstrapDemands():

    # Read in data files
    Demand_file = pd.read_csv("WoolworthsDemands.csv")
    Stores_data = pd.read_csv("Store_Data_Nonzero_GROUPED.csv")
    Stores_data_zero = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")

    # Get number of stores and days
    n_stores, n_days = np.shape(Demand_file)

    # Loop through stores and bootstrap demand for each
    for i in range(n_stores):

        # Get store data
        storename = Demand_file['Store'].iloc[i]
        store_data = Demand_file.loc[Demand_file['Store'] == storename]
        store_demands = store_data.iloc[0, 1:].values.tolist()

        # Sort the list of demands and remove extreme values (min and max)
        nonzero_demands = [value for value in store_demands if value != 0]
        nonzero_demands.sort()
        nonzero_demands = nonzero_demands[2:-3]

        # Sample store demand from empirical distribution
        sampled = random.choice(nonzero_demands)

        # Store in the data frame
        storeindex = Stores_data.index[Stores_data.Store == storename]
        Stores_data.at[storeindex, 'Demand Estimate'] = sampled

        if ("Countdown" in storename) and ("Metro" not in storename):
            Stores_data_zero.at[storeindex, 'Demand Estimate'] = sampled


    # Remove the distribution centre
    Stores_data = Stores_data[Stores_data['Store'] != 'Distribution Centre Auckland']
    Stores_data_zero = Stores_data_zero[Stores_data_zero['Store'] != 'Distribution Centre Auckland']


    # Extract just the list of demands
    Stores_data = Stores_data['Demand Estimate'].values.tolist()
    Stores_data_zero = Stores_data_zero['Demand Estimate'].values.tolist()

    # Export to file
    #Stores_data.to_csv("Simulated_Demands_Nonzero.csv", index = False)
    # Stores_data_zero.to_csv("Simulated_Demands_Some_zero.csv", index = False)

    # Return the arrays
    return Stores_data, Stores_data_zero


def Obtain_Simulated_Route_Demands(weekday_routes_used, saturday_routes_used, weekday_stores_demands, saturday_stores_demands):

    # Read in route matrix
    weekday_route_matrix = np.loadtxt(open("Route_Matrix_Weekday.csv"), delimiter=",", skiprows=0)
    saturday_route_matrix = np.loadtxt(open("Route_Matrix_Weekend.csv"), delimiter=",", skiprows=0)
    n_stores, n_routes = np.shape(weekday_route_matrix)

    # Get number of routes used
    weekday_n_routes = len(weekday_routes_used)
    saturday_n_routes = len(saturday_routes_used)

    # Initalise arrays of route times
    weekday_route_demands = np.zeros(weekday_n_routes)
    saturday_route_demands = np.zeros(saturday_n_routes)

    # Loop through each route, for each demand case, and get the total demand
    ### WEEKDAY ###
    for i in range(weekday_n_routes):
        weekday_route_demands[i] = np.dot(weekday_route_matrix[:, int(weekday_routes_used[i])], weekday_stores_demands)

    ### WEEKEND ###
    for i in range(saturday_n_routes):
        saturday_route_demands[i] = np.dot(saturday_route_matrix[:, int(saturday_routes_used[i])], saturday_stores_demands)

    # Return the route demands
    return weekday_route_demands, saturday_route_demands