# Alt version of routeGeneration.py [V2]

# Libraries
import numpy as np
from numpy.core.einsumfunc import _einsum_path_dispatcher  #?????
from numpy.lib.nanfunctions import _nanprod_dispatcher
import pandas as pd
import itertools
from Regions import set_boundaries

def generate_route_sets(Weekday, name, closing):

    # Read in  data
    distributionCentre = pd.read_csv("Distribution_Centre_Data.csv")
    durations = pd.read_csv("WoolworthsTravelDurations.csv").to_numpy()

    #if Weekday == True:
        #data = pd.read_csv("Store_Data_Nonzero_GROUPED.csv")
    #else:
        #data = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")
    ###################################################################################### CHANGES
    if closing == False and Weekday == True:
        data = pd.read_csv("Store_Data_Nonzero_GROUPED.csv")
    elif closing == False and Weekday == False:
        data = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")
    elif closing == True and Weekday == True:
        data = pd.read_csv("Store_Data_Nonzero_Closing.csv")
    else:
        data = pd.read_csv("Store_Data_Some_zero_Closing.csv")
    
    #  Distribution centre index
    DC = int(data[data['Store'] == 'Distribution Centre Auckland'].index.values)
    ######################################################################################


    # Seperate the data into regions and convert to numpy arrays
    North = data.loc[data["Region"]=='North'].to_numpy()
    South = data.loc[data["Region"]=='South'].to_numpy()
    East = data.loc[data["Region"]=='East'].to_numpy()
    West = data.loc[data["Region"]=='West'].to_numpy()
    Central= data.loc[data["Region"]=='Central'].to_numpy()

    # Calculate number of stores
    n_stores = len(North) + len(South) + len(East) + len(West) + len(Central)

    # Initialising total time, pallets lists + route storage matrix
    routeMatrix = np.empty((n_stores,0), int)
    timeArray = []
    palletsArray = []


    # Loop through each region
    for region in [North, South, East, West, Central]:

        # Obtain ID set to get each unordered combination of 3 stores
        ID_set = region[:,4]
        sets = list(itertools.combinations(ID_set, 4)) + list(itertools.combinations(ID_set, 3)) + list(itertools.combinations(ID_set, 2)) + list(itertools.combinations(ID_set, 1))

        # Cheapest Insertion - loop through each potential route/combination of stores
        for k in range(len(sets)):

            # Initialise lists for this route
            pallets = 0                         # Number of pallets on this route
            time = 0.0                          # Time for this route
            cluster = list(sets[k])             # Stores visited in this route
            first_time = []                     # List for time from the DC to each store in the route
            route = [DC, DC]                    # List for ordered route

            # Add the 'starting' time to each store, from the DC, to the array
            first_time = [durations[DC, index+1] for index in cluster]
            
            # Select the minimum time and add to the route (symmetric assumption here) 
            min_time_location = first_time.index(min(first_time))
            route.insert(1, cluster[min_time_location])                         # List containing places visited, in order
            returntime = durations[route[1], DC + 1]
            singlestorepallets =  data.iloc[cluster[min_time_location], 5]      # Update route's travel time
            pallets += singlestorepallets                                       # Update route's total pallet demand
            time += returntime + min(first_time) + 450 * singlestorepallets
            cluster.pop(min_time_location)                                      # Remove store from cluster


            # While not all the stores have been placed in the route
            while len(cluster) > 0:

                # Initialise minimum additional time
                min_duration_best= float("Inf")

                # Loop through every other (unvisited) store index
                for v in cluster:  
                            
                    # Find min duration to node still in cluster
                            
                    for u in range(1,len(route)-1): # Every index position that unvisited store could go in
                        # hecking each i
                        min_duration_temp = durations[route[u-1], v+1] + durations[v, route[u]+1] - durations[route[u-1], route[u]+1] # Both directions
                        # Record if best time
                        if(min_duration_temp < min_duration_best):
                            min_duration_best = min_duration_temp
                            store_ID = v
                            position = u          
                        
                # Insert best new node into array  
                cluster.pop(cluster.index(store_ID))
                route.insert(position,store_ID)
                # Calculating total route time with this insertion point
                singlestorepallets =  data.iloc[v, 5]
                time += min_duration_best + 450 * singlestorepallets
                pallets += singlestorepallets


            # Append the time and pallets of this route
            timeArray.append(time)
            palletsArray.append(pallets)

            # Only get the indexes of stores visited now
            route = route[1:-1]
            # Store the store indexes in order: 0 if not visited, 1 visited first, and so on. 
            route_info = np.zeros(n_stores)
            for i in range(len(route)):
                if route[i] < 55:
                    route_info[route[i]] = i + 1
                elif route[i] > 55:
                    route_info[route[i]-1] = i + 1

            # Append the route information to the route matrices
            routeMatrix = np.append(routeMatrix, np.array([route_info]).T, axis=1)
        

    # Obtain the binary route matrix, to be used in the linear program constraints
    binary_route_matrix = np.where(routeMatrix>0.01, 1, 0)
    
    ################################################################################ CHANGES
    if closing == False:
        # Export the binary route matrix and route data as files, to be imported in the LP solver script
        np.savetxt("Route_Matrix_" + name + ".csv", binary_route_matrix, delimiter=',')
        np.savetxt("Route_Times_" + name + ".csv", timeArray, delimiter=',')
        np.savetxt("Route_Pallets_" + name + ".csv", palletsArray, delimiter=',')

        # Export the non-binary route matrix as file
        np.savetxt("Ordered_Route_Matrix.csv", routeMatrix, delimiter=',')
    else:
        np.savetxt("Route_Matrix_" + name + "_Closing.csv", binary_route_matrix, delimiter=',')
        np.savetxt("Route_Times_" + name + "_Closing.csv", timeArray, delimiter=',')
        np.savetxt("Route_Pallets_" + name + "_Closing.csv", palletsArray, delimiter=',')

        # Export the non-binary route matrix as file
        np.savetxt("Ordered_Route_Matrix_Closing.csv", routeMatrix, delimiter=',')
    #################################################################################

    # Check some of the output, as a 'reality check'
    # print(np.shape(routeMatrix))
    # print(binary_route_matrix[:,110])
    # print(len(timeArray))
    # print(len(palletsArray))
    # print(timeArray[0]) 

if __name__ == "__main__":

    generate_route_sets(True, "Weekday", closing = False)
    generate_route_sets(False, "Weekend", closing = False)