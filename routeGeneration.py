# Generating a subset of feasible routes

# Libraries
import numpy as np
from numpy.core.einsumfunc import _einsum_path_dispatcher  #?????
from numpy.lib.nanfunctions import _nanprod_dispatcher
import pandas as pd
import itertools
from Regions import set_boundaries


# Read in grouped data
distributionCentre = pd.read_csv("Distribution_Centre_Data.csv")
data = pd.read_csv("Store_Data_Some_zero_GROUPED.csv")
durations = pd.read_csv("WoolworthsTravelDurations.csv").to_numpy()
# Distribution centre index
DC = 55

# Seperate the data into regions and convert to numpy arrays
North = data.loc[data["Region"]=='North'].to_numpy()
South = data.loc[data["Region"]=='South'].to_numpy()
East = data.loc[data["Region"]=='East'].to_numpy()
West = data.loc[data["Region"]=='West'].to_numpy()
Central= data.loc[data["Region"]=='Central'].to_numpy()



# Generalise for loop for each region
region = North

# Loop to apply to each region to get each combination of 3 stores
# ID
ID_set = region[:,4]
#list every unordered combo of 3 stores
sets = list(itertools.combinations(ID_set, 3))

# Initialising lists
############################################################
# Creating ordered route array to store outcome
route = [] # Distribution centre ID is the first element of all routes
currentRoute = []


temp_route = []
# Initialising final time and route storage lists
routeMatrix = np.zeros((84,5))
timeArray = []
palletsArray = []
############################################################

# Cheapest Insertion ( Assume symetric durations) function for each 

for k in range(len(sets)):
    pallets = 0
    time = 0.0
    #print(k) # To check progress whilst running 
    # 1 possible combination of stores
    cluster = list(sets[k])
    #print(cluster)
    # Find closest store from distribution centre
    node =[]
    for n in range(len(cluster)): 

        # Indexing ID to find distance of each store in cluster from distribution 
        node.append(durations[DC, cluster[n]+1]) # accounts for data frame shift (CHECK)
    
        # Select the minimum time and add to the route ( Symetric assumption here) 
    st = node.index(min(node))
    route.append(cluster[st]) #####
    time += min(node) + 450 # Here only accounting for one way
    # Acounting for distribution centre being extracted from data
    pallets += data.iloc[st, 5]
 
        # Remove added node from cluster ( last added node)
    cluster.pop(st)

    #2d array row = current node number in partial solution, cols = number of nodes left to visit in cluster 
    #min_duration = np.zeros((len(route), len(cluster)))
        
    # Check for next shortest route addition at insertion positions
    # Need to check point in route that every store in cluster could be added
    route.append(DC) # Distribution centre store to end
    route.insert(0,DC)

    if(len(sets[0])==3):
        '''
        for i in range(1,len(route)-1): # Checks distances from each next node in route to each node in the remaining cluster
            for j in cluster: 
            min_time_temp = durations[route[i], j+1] + durations[route[i+1], j+1]
            if(i==0):
                min_time = time + min_time_temp + 450
                min_store = j
                pallets_temp = pallets + data.iloc[min_store, 5]
            elif(min_time_temp<min_time):
                min_time = time + min_time_temp + 450
                min_store = j
                pallets_temp = pallets + data.iloc[min_store, 5]
        
                cluster.pop(min_store) # Remove the cluster that has just been added
    # Check where the next store should be inserted into route list
        '''
    temp_time = 0
    min_duration_best= 2000000000
    for v in cluster:  # looks at every non visited store in cluster
                 
        # Find min duration to node still in cluster
                
        for u in range(1,len(route)-1): # Every index position that unvisited store could go in
            #Checking each i
            min_duration_temp = durations[route[u], v+1] + durations[v, route[u+1]+1] # Both directions
            # Recording if best time
            if(min_duration_temp < min_duration_best):
                min_duration_best = min_duration_temp
                store_ID = v
                position = u          
            
        # Insert best new node into array  
        route.insert(position+1,store_ID)
        # Calculating total route time with this insertion point
        time += min_duration_best + 450
        pallets += data.iloc[v, 5]
        '''            
        # Output arrays
        if(routeMatrix==[]): # If empty then the first 
            routeMatrix[k] = temp_route
            timeArray.append(temp_time)
            pallets = pallets_temp + region[store_ID,5]
        elif(temp_time<timeArray[k]):
            routeMatrix[k] = temp_route
            timeArray[k] = temp_time
            pallets = pallets_temp + region[store_ID,5]
        ''' 
    routeMatrix[k,0] = route[0]
    routeMatrix[k,1] = route[1]
    routeMatrix[k,2] = route[2]
    routeMatrix[k,3] = route[3]
    routeMatrix[k,4] = route[4]
    routeMatrix[k,5] = route[5]
    timeArray.append(time)
    palletsArray.append(pallets)

       
                
print(routeMatrix[0])


#  lists of 2 and 1 store

# Approach
# Step 1 : Seperating data into regions based on the attribute
# Loop through different regions 
# In each region every combination of 3 stores will be formed ( order doesn't matter) and recorded in lists corresponding to route and the ID's of stores in each route (pallets <30)

# For loop that does Cheapest insertion on each combination. ( to figure out best order for the nodes in the combination)
# Best order will be turned into a 1D array of which stores and in which order () 
# Output of Cheapest insertion for loop
#   route
#   1 [3, 0, 2, 1...(number of stores)]
#   2 rest of the routes (appended to row above)
#   3
#   Corresponding time and cost of each route are also input into a 1D array

# Make a copy of this 2D array and turn all values >= 1 into 1

# These 3 arrays (2D binary route matrix, time and cost, 1D arrays) convert to csv to feed straight into solver. 



