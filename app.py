import streamlit as st
import pandas as pd
import DB_utils as db
st.set_page_config(page_title="Security Check Dashboard🚓", layout="wide")

st.title("Security Check Dashboard🚓")
st.markdown("A centralized system for logging, tracking, and analyzing vehicle movements")

tab1, tab2, tab3 = st.tabs(["Insights", "Logs Table", "Add a new log"])

with tab1:
    container = st.container(border=True)
    with container:
        container.subheader("Key Insight🔎")
        left, middle, right = st.columns(3, border=True)

        with left:
            left.markdown("Most Searched Violation")
            df = db.most_search_vehicle()
            left.table(df)
        with middle:
            middle.markdown("Violation with High Search & Arrest Rate")
            df = db.high_arrest_search_rates()
            middle.table(df)
            
        with right:
            right.markdown("Violation with Less Search & Arrest")
            df = db.least_search_and_arrest_violation()
            right.table(df)

    zone = st.container(border=True)
    with zone:
        zone.subheader("🚨Drug stops screening report🚨")
        zone.markdown("Insights on Drug Stops")

        df = db.drug_stops_by_country()
        df = df.reset_index(drop=True)
        col1, col2, col3 = st.columns(3)
        col1.metric(label=df.loc[0, "Country"], value=f"Total Stops: {df.loc[0, 'Total_stops']}", delta=f"Drug Stop Rate: {df.loc[0, 'Drug_stop_rate']}%")
        col2.metric(label=df.loc[1, "Country"], value=f"Total Stops: {df.loc[1, 'Total_stops']}", delta=f"Drug Stop Rate: {df.loc[1, 'Drug_stop_rate']}%")
        col3.metric(label=df.loc[2, "Country"], value=f"Total Stops: {df.loc[2, 'Total_stops']}", delta=f"Drug Stop Rate: {df.loc[2, 'Drug_stop_rate']}%")

        with st.expander("🔍 Top 10 Vehicles in Drug-Related Stops"):
            df = db.top10_drug_vehicle()
            st.dataframe(df)

    country = st.container(border=True)
    with country:
        country.subheader("🗺️World Security Stops")
        df = db.country_most_searches()
        country.markdown(f'''**Country With Highest Search Conducted:** ***{df.loc[0,'Country']}***  
                        **Total Search conducted:** ***{df.loc[0,'Searches']}***
                        ''')
        country.subheader("Stops Conducted in Different Countries")
        df = db.driver_demographics_by_country()
        country.bar_chart(df, x="Ethinicity", y="Stops", color="Country", stack=False)


        with country:
            chart = st.container(border=True)
            chart.subheader("Arrest rate by country and violation")
            data = db.arrest_rate_country_violation()
            chart.bar_chart(data, x="Violation", y="Arrest_rate", color="Country", stack=False)
    
    st.subheader("Advanced Queries")
    query_options = [
        "Yearly Breakdown of Stops and Arrests by Country",
        "Driver Violation Trends Based on Age and Race",
        "Time Period Analysis of Stops",
        "Violations with High Search and Arrest Rates",
        "Driver Demographics by Country (Age, Gender, Race)",
        "Top 5 Violations with Highest Arrest Rates",
        "What Time of Day Sees the Most Traffic Stops",
        "Which Driver Age Group Had the Highest Arrest Rate",
        "What is the Gender Distribution of Drivers Stopped",
        "Which Violations Are Most Common Among Younger Drivers (<25)",
        "Which Race and Gender Combination Has the Highest Search Rate",
        "Are Stops During the Night More Likely to Lead to Arrests"
    ]
    
    selected_query = st.selectbox("Select a query to display", query_options)

    # Display the results of the selected query
    if selected_query == "Yearly Breakdown of Stops and Arrests by Country":
        df = db.yearly_stops_arrests_country()
        st.write("### Yearly Breakdown of Stops and Arrests by Country")
        st.line_chart(df.set_index("Year")[["Total_Searches", "Total_Arrests"]])

    elif selected_query == "Driver Violation Trends Based on Age and Race":
        df = db.get_violation_trends_by_age_race()
        st.write("### Driver Violation Trends Based on Age and Race")
        st.dataframe(df)

    elif selected_query == "Time Period Analysis of Stops":
        df = db.time_period_analysis()
        st.write("### Time Period Analysis of Stops")
        st.dataframe(df)

    elif selected_query == "Violations with High Search and Arrest Rates":
        df = db.high_arrest_search_rates()
        st.write("### Violations with High Search and Arrest Rates")
        st.dataframe(df)

    elif selected_query == "Driver Demographics by Country (Age, Gender, Race)":
        df = db.driver_demographics_by_country()
        st.write("### Driver Demographics by Country (Age, Gender, Race)")
        st.dataframe(df)

    elif selected_query == "Top 5 Violations with Highest Arrest Rates":
        df = db.top_violations()
        st.write("### Top 5 Violations with Highest Arrest Rates")
        st.bar_chart(df.set_index("Violation")["Arrest_rate"])

    elif selected_query == "What Time of Day Sees the Most Traffic Stops":
        df = db.most_stop_time()
        st.write("### Time of Day with Most Traffic Stops")
        st.bar_chart(df.set_index("time_period"))

    elif selected_query == "Which Driver Age Group Had the Highest Arrest Rate":
        df = db.high_arrest_age_group()
        st.write("### Arrest Rate by Driver Age Group")
        st.bar_chart(df.set_index("age_group"))

    elif selected_query == "What is the Gender Distribution of Drivers Stopped":
        data = db.gender_ratio()
        st.write("### Gender Distribution of Drivers Stopped")
        st.bar_chart(data, x="driver_gender", y="count", stack=False)

    elif selected_query == "Which Violations Are Most Common Among Younger Drivers (<25)":
        df = db.common_youth_violations()
        st.write("### Common Violations Among Younger Drivers (<25)")
        st.bar_chart(df.set_index("violation"))

    elif selected_query == "Which Race and Gender Combination Has the Highest Search Rate":
        df = db.high_search_rate()
        st.write("### Highest Search Rate by Race and Gender")
        st.dataframe(df)

    elif selected_query == "Are Stops During the Night More Likely to Lead to Arrests":
        df = db.night_arrest_possibilities()
        st.write("### Arrest Rate During Night Stops")
        st.bar_chart(df.set_index("Time_of_the_day"))
    
with tab2:
    st.markdown("Log Entries")
    df = db.logs()
    st.dataframe(df)

with tab3:
    st.markdown("Fill in the form below to enter a new log:")
    
    with st.form(key="log_form"):
        stop_date = st.date_input("Stop Date")
        stop_time = st.time_input("Stop Time")
        country_name = st.text_input("Country where the stop took place")
        driver_gender = st.selectbox("Driver Gender", ["M", "F", "Other"])
        driver_age_raw = st.number_input("Driver Age (Raw)", min_value=18)
        driver_age = st.number_input("Driver Age (After Confirmation)", min_value=18)
        driver_race = st.text_input("The Race/Ethnicity of the driver")
        violation_raw = st.selectbox("The original reason for the stop", ["Drunk Driving", "Other", "Signal Violation", "Speeding", "Seatbelt"])
        violation = st.selectbox("The type of violation", ["Speeding", "Other", "DUI", "Seatbelt", "Signal"])
        search_conducted = st.selectbox("Was the driver or vehicle searched?", ["Yes", "No"])
        search_type = st.selectbox("Search Type", ["Frisk", "Vehicle Search", "Other", "None", "No Search, Vehicle all green", "Search Type Not Specified"])
        stop_outcome = st.selectbox("Stop Outcome", ["Warning", "Citation", "Arrest", "Ticket"])
        is_arrested = st.selectbox("Was the driver arrested?", ["Yes", "No"])
        stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
        drugs_related_stop = st.selectbox("Was the stop related to drugs?(1 - Yes, 0 - No)", ["1", "0"])
        vehicle_number = st.text_input("Vehicle Number/ID")
        submit_button = st.form_submit_button("Submit Log")

        if submit_button:
            if stop_date and stop_time and country_name and driver_gender and driver_age and violation:
                log_data = {
                    "stop_date": stop_date,
                    "stop_time": stop_time,
                    "country_name": country_name,
                    "driver_gender": driver_gender,
                    "driver_age_raw": driver_age_raw,
                    "driver_age": driver_age,
                    "driver_race": driver_race,
                    "violation_raw": violation_raw,
                    "violation": violation,
                    "search_conducted": search_conducted,
                    "search_type": search_type,
                    "stop_outcome": stop_outcome,
                    "is_arrested": is_arrested,  
                    "stop_duration": stop_duration,
                    "drugs_related_stop": drugs_related_stop,
                    "vehicle_number": vehicle_number
                }

                result = db.add_log(log_data)
                if result:
                    st.success("New log added successfully!")
                else:
                    st.error("There was an error adding the log.")
            else:
                st.warning("Please fill in all required fields.")