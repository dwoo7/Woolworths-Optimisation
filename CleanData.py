# This file generates all the code used in Part I of the project
# The sections are as follows:
# - Clean/process data
# - Estimate demands
# - Cartesian locations
# - Polar locations
# - Export file

# Import libraries
import numpy as np
import pandas as pd
import utm as utm
from matplotlib import pyplot as plt

# Read in data files for store demands, distance separations, latitude/longitude and time separations
Demand_file = pd.read_csv("WoolworthsDemands.csv")
Distances_file = pd.read_csv("WoolworthsDistances.csv")
Locations_file = pd.read_csv("WoolworthsLocations.csv")
Times_file = pd.read_csv("WoolworthsTravelDurations.csv")



###########################################################################################################
###############                              CLEAN/PROCESS DATA                             ###############
###########################################################################################################

pd.options.mode.chained_assignment = None  # Remove false positive warning

# Extract the distribution centre location and remove from locations dataframe
distribution_data = Locations_file[Locations_file['Type'].str.contains("Distribution")]
# distribution_data.reset_index(inplace=True, drop=True)
# distribution_data.drop(distribution_data.columns[[0,1]], 1)
n_dist, _ = distribution_data.shape
# Set as origins
distribution_data["x"] = 0
distribution_data["y"] = 0
distribution_data["r"] = 0
distribution_data["theta"] = 0
# Export to file
distribution_data.to_csv("Distribution_Centre_Data.csv", index=False)

# Initialise tables of cleaned tabular data
# Locations_cleaned = Locations_file[~Locations_file['Type'].str.contains("Distribution")]
# Data_table1 = Locations_cleaned[['Store', 'Lat','Long']].copy()

Data_table1 = Locations_file[['Store', 'Lat','Long']].copy()
Data_table2 = Data_table1.copy()

# Add IDs
Data_table1["ID"]=Data_table1.index
Data_table2["ID"]=Data_table2.index



###########################################################################################################
###############                             ESTIMATE DEMANDS                                ###############
###########################################################################################################

# Data_table1 will be used to solve the LP on days when all stores have nonzero demand
# Data_table1 will be used to solve the LP when only Countdown stores have nonzero demand; this occurs weekly
# Note the LP doesn't need to be solved when no stores have demand (which occurs weekly)
[n_stores, n_days] = Demand_file.shape
n_days -= 1
demands1 = np.zeros(n_stores + 1)
demands2 = np.zeros(n_stores + 1)

# Process the demands and obtain a conservative estimate for each. These will be used to generate routes
# Use the Xth percentile value as the demand for each store
X = 75

Data_table1['Demand Estimate'] = np.zeros(n_stores + 1)
Data_table2['Demand Estimate'] = np.zeros(n_stores + 1)


# Loop through each stores
for i in range(n_stores):

    # Get demands on all days
    storename = Demand_file['Store'].iloc[i]
    store_data = Demand_file.loc[Demand_file['Store'] == storename]
    store_demands = store_data.iloc[0, 1:].values.tolist()

    # Calculate and store the Xth percentile, excluding the days with no demand
    nonzero_demands = [value for value in store_demands if value != 0]
    estimate = np.percentile(nonzero_demands, X)
    storeindex = Data_table1.index[Data_table1.Store == storename]
    Data_table1.at[storeindex, 'Demand Estimate'] = estimate

    if ("Countdown" in storename) and "Metro" not in storename:
        Data_table2.at[storeindex, 'Demand Estimate'] = estimate


###########################################################################################################
###############                            CARTESIAN LOCATIONS                              ###############
###########################################################################################################

# We will use one (the first) distribution centre as the reference (Auckland)
centre_data = distribution_data.iloc[0,:]
x_cent,y_cent,_,_ = utm.from_latlon(centre_data.Lat, centre_data.Long)

# Initialise arrays
x_coords = np.zeros(n_stores+1)
y_coords = np.zeros(n_stores+1)

# Loop through stores
for i in range(n_stores+1):
    # Calculate and store the coordinates
    if i !=55:
        store = Data_table1.iloc[i,:]
        x,y,_,_ = utm.from_latlon(store.Lat, store.Long)
        x_coords[i] = (x - x_cent)
        y_coords[i] = (y - y_cent)

# Append data to tables
Data_table1["x"] = x_coords
Data_table1["y"] = y_coords
Data_table2["x"] = x_coords
Data_table2["y"] = y_coords



###########################################################################################################
###############                              POLAR LOCATIONS                                ###############
###########################################################################################################

# We will proceed to find the location of each store relative to the distribution centre
# Each store will have a radius (magnitude) and angle (anticlockwise from the horizontal)

# Magnitude/distance of each store from each distribution centre
r_all = Distances_file[[name for name in distribution_data["Store"]]]
rows, cols = r_all.shape

# Loop through each distribution centre
for i in range(cols):

    # Calculate the distance of each store from the centre and store
    r = [d for d in r_all.iloc[:,i]]
    str_name = "r_" + r_all.columns[i]
    Data_table1[str_name] = r
    Data_table2[str_name] = r

# Generate angles
theta = np.zeros(rows)
theta = np.arctan2(y_coords, x_coords) * 180/np.pi
# Store angles
Data_table1["theta"] = theta
Data_table2["theta"] = theta



###########################################################################################################
###############                                EXPORT FILE                                  ###############
###########################################################################################################

Data_table1.to_csv("Store_Data_Nonzero.csv", index=False)
Data_table2.to_csv("Store_Data_Some_zero.csv", index=False)



###########################################################################################################

# Check code is valid by plotting the stores
# f,ax = plt.subplots()
# ax.set_title("Visualisation of Stores in Cartesian Coordinates")
# for i in range(n_stores):
#     store = Data_table1.iloc[i,:]
#     ax.plot(store["x"],store["y"], 'kx')
# for j in range(n_dist):
#     ax.plot(distribution_data.iloc[j]["x"],distribution_data.iloc[j]["y"], 'rx', markersize=12)
# plt.show()

# Print total average
# average = Data_table1["Demand Estimate"].mean()
# print(average)
