import mysql.connector
import pandas as pd
from DB_config import DB_CONFIG

def get_connection(): #Establishes and returns a connection to the MySQL database.
    
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def logs():#To Display Logs in the Dashboard
    connection = get_connection()
    query = """
        SELECT * FROM checkpost_data
        """
    df = pd.read_sql(query, connection)
    return df

def add_logs():
    connection = get_connection
    query = """
        INSERT INTO logs(
            stop_date, stop_time, country_name, driver_gender, driver_age_raw, driver_age, driver_race,
            violation_raw, violation, search_conducted, search_type, stop_outcome, is_arrested,
            stop_duration, drugs_related_stop, vehicle_number
        ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,)
    """
    cursor = connection.cursor
    cursor.executemany(query, connection)
    connection.commit()


def top10_drug_vehicle(): #What are the top 10 vehicles involved in drug-related stops?
    connection = get_connection()
    query = """
        select vehicle_number, count(*) as stop_count
        FROM checkpost_data
        WHERE drugs_related_stop = True
        GROUP BY vehicle_number
        ORDER BY stop_count DESC
        LIMIT 10
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def most_search_vehicle(): #Why vehicles were most frequently searched(Top 3 Reason)
    connection = get_connection()
    query ="""
        SELECT violation_raw as Violation, count(*) as Total_Stops
        FROM checkpost_data
        WHERE search_conducted = True
        GROUP BY violation_raw
        ORDER BY Total_stops DESC
        LIMIT 3 
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def high_arrest_age_group(): #Which driver age group had the highest arrest rate?
    connection = get_connection()
    query = """
        SELECT 
            CASE
                WHEN driver_age BETWEEN 18 AND 29 THEN 'Young(18-29)'
                WHEN driver_age BETWEEN 30 AND 59 THEN 'Middle-Aged(30-59)'
                ELSE 'Senior(60+)'
            END AS age_group,
            COUNT(*) AS count
        FROM checkpost_data
        WHERE is_arrested IS TRUE
        GROUP BY age_group
        order by count DESC;
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def gender_ratio(): #What is the gender distribution of drivers stopped in each country?
    connection = get_connection()
    query = """
        SELECT 
            country_name, driver_gender, 
            COUNT(*) AS count
        FROM checkpost_data
        WHERE search_conducted IS TRUE
        GROUP BY country_name, driver_gender
        ORDER BY country_name
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def high_search_rate(): #Which race and gender combination has the highest search rate?
    connection = get_connection()
    query = """
        SELECT 
            country_name, driver_gender, 
            COUNT(*) AS count
        FROM checkpost_data
        WHERE search_conducted IS TRUE
        GROUP BY country_name, driver_gender
        ORDER BY count DESC
        LIMIT 1
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def most_stop_time(): #What time of day sees the most traffic stops?
    connection = get_connection()
    query = """
        SELECT 
            CASE
                WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 0 AND 5 THEN 'Midnight - Early Morning(12AM - 5AM)'
                WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 6 AND 11 THEN 'Morning(6AM - 11AM)'
                WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 12 AND 16 THEN 'Afternoon(12PM - 4PM)'
                WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 17 AND 20 THEN 'Evening(5PM - 8PM)'
                WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 21 AND 23 THEN 'Night(9PM - 11PM)'
            END as time_period,
            COUNT(*) AS count
        FROM checkpost_data
        WHERE search_conducted IS TRUE
        GROUP BY time_period
        ORDER BY count DESC;
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def AVG_stop_time():#What is the average stop duration for different violations?
    connection = get_connection()
    query = """
        SELECT 
            violation, 
            ROUND(AVG(stop_duration)) AS 'Avg_duration(in Mins)'
        FROM checkpost_data
        WHERE search_conducted IS TRUE
        GROUP BY violation;
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def night_arrest_possibilities():#Are stops during the night more likely to lead to arrests?
    connection = get_connection()
    query = """
        SELECT 
            CASE
                WHEN HOUR(stop_time) BETWEEN 20 AND 23 OR HOUR(stop_time) BETWEEN 0 AND 4 THEN 'Night Hours'
                ELSE 'Day Hours'
            END AS Time_of_the_day,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS Arrests,
            ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Arrest_rate
        FROM checkpost_data
        GROUP BY Time_of_the_day
        ORDER BY Arrest_rate DESC;
        """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#Which violations are most associated with searches or arrests?

'''
________________________________________________________________________________
def violation_search_arrest():
    connection = get_connection()
    query = """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS total_searches
        FROM checkpost_data
        GROUP BY violation
        ORDER BY total_searches DESC
        LIMIT 1;
        """
    df = pd.read_sql(query, connection)
    print("Below is the stat for Violation that leads to most searches")
    print(df)
    query = """
        SELECT 
            violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests
        FROM checkpost_data
        GROUP BY violation
        ORDER BY total_arrests DESC
        LIMIT 1;
        """
    df2 = pd.read_sql(query, connection)
    print("Below is the stat for Violation that leads to most arrests")
    print(df2)    
    connection.close()
_______________________________________________________________________________
    
'''
def violation_search_arrest(): #Which violations are most associated with searches or arrests?
    connection = get_connection()
    query = """
        SELECT 'Most Searches' AS category, violation, total_stops, total_searches_or_arrests
        FROM (
            SELECT 
                violation,
                COUNT(*) AS total_stops,
                SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS total_searches_or_arrests
            FROM checkpost_data
            GROUP BY violation
            ORDER BY total_searches_or_arrests DESC
            LIMIT 1
        ) AS most_searches

        UNION

        SELECT 'Most Arrests' AS category, violation, total_stops, total_searches_or_arrests
        FROM (
            SELECT 
                violation,
                COUNT(*) AS total_stops,
                SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_searches_or_arrests
            FROM checkpost_data
            GROUP BY violation
            ORDER BY total_searches_or_arrests DESC
            LIMIT 1
        ) AS most_arrests;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def common_youth_violations():#Which violations are most common among younger drivers (<25)?
    connection = get_connection()
    query = """
        SELECT 
            violation,
            COUNT(*) AS total
        FROM checkpost_data
        WHERE driver_age < 25
        GROUP BY violation
        ORDER BY total DESC
        LIMIT 3;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def least_search_and_arrest_violation():#Is there a violation that rarely results in search or arrest?
    connection = get_connection()
    query = """
        SELECT 'Least Searches' AS Category, violation AS Violation, Total_Searches 
        FROM (
            SELECT violation, 
                   SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS Total_Searches
            FROM checkpost_data
            GROUP BY violation
            ORDER BY Total_Searches ASC
            LIMIT 1
        ) AS least_searches

        UNION

        SELECT 'Least Arrests' AS Category, violation AS Violation, total_arrests AS Total_Arrests
        FROM (
            SELECT violation, 
                   SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests
            FROM checkpost_data
            GROUP BY violation
            ORDER BY total_arrests ASC
            LIMIT 1
        ) AS least_arrests;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def drug_stops_by_country(): #Which countries report the highest rate of drug-related stops?
    connection = get_connection()
    query = """
        SELECT 
            country_name as Country,
            COUNT(*) AS Total_stops,
            SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END) AS Drug_stops,
            ROUND(SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END)/COUNT(*)*100, 2) AS Drug_stop_rate
        FROM checkpost_data
        GROUP BY country_name
        ORDER BY drug_stop_rate DESC;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def arrest_rate_country_violation(): #What is the arrest rate by country and violation?
    connection = get_connection()
    query = """
        SELECT 
            country_name AS Country,
            violation AS Violation,
            COUNT(*) AS total_stops,
            SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests,
            ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Arrest_rate
        FROM checkpost_data
        GROUP BY country_name, violation
        ORDER BY Arrest_rate DESC;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

def country_most_searches(): #Which country has the most stops with search conducted?
    connection = get_connection()
    query = """
        SELECT 
            country_name AS Country,
            COUNT(*) AS Total_stops,
            SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS Searches
        FROM checkpost_data
        GROUP BY country_name
        ORDER BY Searches DESC
        LIMIT 1;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)
def yearly_stops_arrests_country():
    connection = get_connection()
    query = """
        SELECT
            Year,
            Country,
            SUM(Arrests) OVER (PARTITION BY Country ORDER BY Year) AS Total_Arrests,
            SUM(Searches) OVER (PARTITION BY Country ORDER BY Year) AS Total_Searches
        FROM (
            SELECT 
                YEAR(stop_date) AS Year,
                country_name AS Country,
                COUNT(*) AS Total_Stops,
                SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS Arrests,
                SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS Searches
            FROM checkpost_data
            GROUP BY country_name, YEAR(stop_date)
            ) AS Yearly_stats
        ORDER BY Country, Year;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#2.Driver Violation Trends Based on Age and Race (Join with Subquery)
def get_violation_trends_by_age_race():
    connection = get_connection()
    query = """
        SELECT 
            age_group,
            driver_race,
            violation,
            COUNT(*) AS violation_count
        FROM (
            SELECT *,
                CASE
                    WHEN driver_age <= 25 THEN 'Youth (<=25)'
                    WHEN driver_age BETWEEN 26 AND 50 THEN 'Adult (26-50)'
                    WHEN driver_age > 50 THEN 'Senior (51+)'
                    ELSE 'Unknown'
                END AS age_group
            FROM checkpost_data
            WHERE driver_age IS NOT NULL AND driver_race IS NOT NULL AND violation IS NOT NULL
        ) AS age_grouped_data
        GROUP BY age_group, driver_race, violation
        ORDER BY age_group, driver_race, violation_count DESC;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#3.Time Period Analysis of Stops (Joining with Date Functions), Number of Stops by Year, Month, Hour of the Day
def time_period_analysis():
    connection = get_connection()
    query = """
        SELECT 
            YEAR(stop_date) AS year,
            MONTH(stop_date) AS month,
            HOUR(stop_time) AS hour,
            COUNT(*) AS total_stops
        FROM checkpost_data
        GROUP BY year, month, hour
        ORDER BY year, month, hour;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#4.Violations with High Search and Arrest Rates (Window Function)
def high_arrest_search_rates():
    connection = get_connection()
    query = """
        SELECT * FROM (
            SELECT 
                'Highest Search Rate' AS Category,
                violation,
                ROUND(100 * SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) / COUNT(*), 2) AS Percentage_rate
            FROM checkpost_data
            GROUP BY violation
            ORDER BY Percentage_rate DESC
            LIMIT 1
        ) AS highest_search

        UNION

        SELECT * FROM (
            SELECT 
                'Highest Arrest Rate' AS Category,
                violation,
                ROUND(100 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*), 2) AS Percentage_rate
            FROM checkpost_data
            GROUP BY violation
            ORDER BY Percentage_rate DESC
            LIMIT 1
        ) AS highest_arrest;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

#5.Driver Demographics by Country (Age, Gender, and Race)
def driver_demographics_by_country():
    connection = get_connection()
    query = """
        SELECT 
            country_name AS Country,
            CASE 
                WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
                WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
                WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
                ELSE '60+' 
            END AS Age_group,
            driver_gender AS Sex,
            driver_race AS Ethinicity,
            COUNT(*) AS Stops
        FROM checkpost_data
        WHERE driver_age IS NOT NULL
        GROUP BY country_name, age_group, driver_gender, driver_race
        ORDER BY country_name, age_group, Stops DESC;
    """
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# 6.Top 5 Violations with Highest Arrest Rates
def top_violations():
    connection = get_connection()
    query = """
            SELECT
                violation AS Violation, 
                ROUND(100 * SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_rate
            FROM checkpost_data
            GROUP BY violation
            ORDER BY Arrest_rate DESC
            LIMIT 5;
            """
    df = pd.read_sql(query, connection)
    connection.close()
    return df