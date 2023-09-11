import streamlit as st
import pandas as pd

def add_filters(police_data):
    exclude = ["MISSING"]

    reasons_for_stop = police_data['result'].columns.drop(["Month","Race/Ethnicity",'gender','residency',"action_taken"]).tolist()
    reasons_for_stop.insert(0, "ALL")
    # Reorder
    top = [x for x in ["ALL", "TRAFFIC VIOLATION", "EQUIPMENT VIOLATION", "TERRY STOP"] if x in reasons_for_stop]
    top.extend([x for x in reasons_for_stop if x not in top and x not in exclude])
    reasons_for_stop = top

    time_periods = ["ALL","MOST RECENT YEAR"]
    time_periods.extend([x for x in range(police_data['result']["Month"].dt.year.max(), 2019, -1)])

    genders = [x for x in police_data['result']["gender"].unique() if x not in exclude]
    genders.insert(0, "ALL")

    res = [x for x in police_data['result']["residency"].unique() if pd.notnull(x) and x not in exclude]
    top = [x for x in res if "COUNTY" in x.upper() and "OUT" not in x.upper() and "OTHER" not in x.upper()]
    top.extend([x for x in res if x not in top])
    res = top
    res.insert(0, "ALL")

    selection = {}
    with st.expander('Data Filters', expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            selection['time stats'] = st.selectbox("Time Period (Stats)", time_periods, index=1,
                                            help="Filter to show only statistics for selected time period")
        with col2:
            selection['time series'] = st.selectbox("Time Period (Time Series)", time_periods, 
                                            help="Filter to show only statistics for selected time period")
        with col3:
            selection['reason'] = st.selectbox("Reason For Stop", reasons_for_stop,
                                            # default=reasons_for_stop,
                                            help="Filter to show only statistics for selected reason(s) for stop")        
            
        col1, col2, col3 = st.columns(3)
        with col1:
            selection['gender'] = st.selectbox("Gender", genders,
                                            help="Filter to show only statistics for a gender")
        with col2:
            selection['residency'] = st.selectbox("Residency", res,
                                            help="Filter to show only statistics for residency")
        with col3:
            selection['race'] = st.multiselect("Race/Ethnicity", police_data['result']["Race/Ethnicity"].unique(),
                                            default=["ASIAN/PACIFIC ISLANDER", "BLACK", "LATINO", "WHITE"],
                                            help="Select races/ethnicities to show in data below")
            
    return selection