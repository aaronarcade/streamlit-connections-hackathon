import pandas as pd
import time
from geopy.geocoders import Nominatim

# Start the timer
start_time = time.time()

# Read the CSV file into a DataFrame
df = pd.read_csv('zillow_prices_with_lat_lon_updated.csv')

# Function to get latitude and longitude for a given location
def get_lat_lon(location):
    geolocator = Nominatim(user_agent='myGeocoder')
    location_info = geolocator.geocode(location)
    if location_info:
        return location_info.latitude, location_info.longitude
    else:
        return None, None

# Counter for checking every 10 rows
counter = 0

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    location = row['RegionName']
    latitude, longitude = row['Latitude'], row['Longitude']  # Check if Latitude and Longitude already exist

    if pd.isnull(latitude) or pd.isnull(longitude):  # If latitude or longitude is missing, fetch them
        latitude, longitude = get_lat_lon(location)

        df.at[index, 'Latitude'] = latitude
        df.at[index, 'Longitude'] = longitude

        elapsed_time_formatted = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
        print(index, elapsed_time_formatted, row['RegionName'], latitude, longitude)

        counter += 1



    # Save the updated DataFrame to a new CSV file every 10 rows
    if counter % 10 == 0:
        df.to_csv('zillow_prices_with_lat_lon_updated.csv', index=False)

# Save the final updated DataFrame to a new CSV file
df.to_csv('zillow_prices_with_lat_lon_updated.csv', index=False)

# Display the updated DataFrame
print(df.head())
