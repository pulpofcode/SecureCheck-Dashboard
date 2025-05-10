import pandas as pd
import mysql.connector

#To know the data we are dealing with
df = pd.read_excel("traffic_stops.xlsx")
print("Top 5 Rows")
print(df.head())
print("\n Columns Info:")
print(df.info())

#Creating the DB and Table
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "SQL@123sql",
)
cursor = connection.cursor()

query = "CREATE DATABASE securecheck"
cursor.execute(query)

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "SQL@123sql",
    database="securecheck"
)
cursor = connection.cursor()

query = "CREATE TABLE checkpost_data (stop_date DATE, stop_time TIME, country_name VARCHAR(100), driver_gender VARCHAR(10), driver_age_raw INT, driver_age INT, driver_race VARCHAR(50), violation_raw VARCHAR(100), violation VARCHAR(100), search_conducted BOOLEAN, search_type VARCHAR(100), stop_outcome VARCHAR(100), is_arrested BOOLEAN, stop_duration VARCHAR(50), drugs_related_stop BOOLEAN,vehicle_number VARCHAR(50))"
cursor.execute(query)

#Initializing the Cleaning and Preparation of the Data
df = pd.read_excel("traffic_stops.xlsx")
print("\nMissing values per column:")
print(df.isnull().sum())

inconsistent_rows = df[(df['search_type'].isnull()) & (df['search_conducted'] == True)]
print(f"Number of inconsistent rows where is search is conducted: {len(inconsistent_rows)}")

inconsistent_rows2 = df[(df['search_type'].isnull()) & (df['search_conducted'] == False)]
print(f"Number of inconsistent rows where is search is not conducted: {len(inconsistent_rows2)}")

Labels_used = df[df['search_conducted'] == False]['search_type'].unique()
print(f"The Labels used are : {Labels_used}")

df.loc[(df['search_type'] == "Vehicle Search") | (df['search_type'] == "Frisk"), 'search_conducted'] = True

df.loc[(df['search_type'].isnull()) & (df['search_conducted'] == True), 'search_type'] = "Search Type Not Specified"
df.loc[(df['search_type'].isnull()) & (df['search_conducted'] == False), 'search_type'] = "No Search, Vehicle all green"

print("\nMissing values per column:")
print(df.isnull().sum())

#Pushing the Cleaned DF in the Database
columns = ",".join(df.columns)
placeholders = ",".join(["%s"] * len(df.columns))

insert_query = f"INSERT INTO checkpost_data ({columns}) VALUES ({placeholders})"
data = [tuple(row) for row in df.itertuples(index=False, name=None)]
cursor.executemany(insert_query, data)
connection.commit()

