import streamlit as st
import nivo
import data
import pandas as pd

def stops_timeline_dashboard(police_data, population):
    exclude = ["MISSING"]

    reasons_for_stop = police_data['result'].columns.drop(["Month","Race/Ethnicity",'gender','residency',"action_taken"]).tolist()
    reasons_for_stop.insert(0, "ALL")
    # Reorder
    top = [x for x in ["ALL", "TRAFFIC VIOLATION", "EQUIPMENT VIOLATION", "TERRY STOP"] if x in reasons_for_stop]
    top.extend([x for x in reasons_for_stop if x not in top and x not in exclude])
    reasons_for_stop = top

    time_periods = ["ALL", "MOST RECENT YEAR"]
    time_periods.extend([x for x in range(police_data['result']["Month"].dt.year.max(), 2019, -1)])

    genders = [x for x in police_data['result']["gender"].unique() if x not in exclude]
    genders.insert(0, "ALL")

    res = [x for x in police_data['result']["residency"].unique() if pd.notnull(x) and x not in exclude]
    top = [x for x in res if "COUNTY" in x.upper() and "OUT" not in x.upper() and "OTHER" not in x.upper()]
    top.extend([x for x in res if x not in top])
    res = top
    res.insert(0, "ALL")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_time = st.selectbox("Time Period", time_periods,
                                        help="Filter to show only statistics for selected time period",
                                        key='time-time')
    with col2:
        selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                      index=1,
                                      help='Time scale to use on time axis of graphs',
                                      key='scale-time')
    with col3:
        selected_reason = st.selectbox("Reason For Stop", reasons_for_stop,
                                        # default=reasons_for_stop,
                                        help="Filter to show only statistics for selected reason(s) for stop",
                                        key='reason-time')
    with col4:
        selected_gender = st.selectbox("Gender", genders,
                                        help="Filter to show only statistics for a gender",
                                        key='gender-time')
        
    col1, col2 = st.columns(2)
    with col1:
        selected_residency = st.selectbox("Residency", res,
                                        help="Filter to show only statistics for residency",
                                        key='residency-time')
    with col2:
        selected_races = st.multiselect("Race/Ethnicity", police_data['result']["Race/Ethnicity"].unique(),
                                        default=["ASIAN/PACIFIC ISLANDER", "BLACK", "LATINO", "WHITE"],
                                        help="Select races/ethnicities to show in data below",
                                        key='race-time')

    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)

    nivo.plot(plot_data['Total Stops'], ylabel="# of Stops", time_scale=selected_scale, title="Total Number of Stops")
    nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops",
              stacked=True, columns=selected_races)
    nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops (%)",
              stacked=False, percent=True, columns=selected_races)
    nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops (%)",
              stacked=True, percent=True, columns=selected_races)