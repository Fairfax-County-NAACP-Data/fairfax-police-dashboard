import streamlit as st
import pandas as pd
from contextlib import nullcontext
from util import text_file, _get_index


def add_filters(police_data, sidebar=True):
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

    sb = st.sidebar if sidebar else st.expander('Data Filters: Expand to change filters', expanded=sidebar)

    selection = {}
    with sb:
        if sidebar:
            st.text("####################################")
            st.subheader("Possible Future location of Chapter Logo")
            st.text("####################################")

            col1=nullcontext()
            col2=nullcontext()
            col3=nullcontext()
        else:
            col1, col2, col3= st.columns(3)

        filter = 'time_stats'
        data = time_periods
        with col1:
            selection[filter] = st.selectbox("Time Range for Statistics", data, index=_get_index(filter, data, 1),
                                            help="Stop totals, arrest rates, and other calculations in tables and bar charts will "
                                                "use data from the selected time period.")
        
        filter = 'time_scale'
        data = ["Monthly",'Quarterly','Annually']
        with col2:
            selection[filter] = st.selectbox("Time Scale", data, index=_get_index(filter, data, 1),
                                help='Time scale to use on time axis of line graphs.')

        selection['time series'] = 'ALL'

        filter = 'reason'
        data = reasons_for_stop
        with col3:
            selection[filter] = st.selectbox("Reason For Stop", data, index=_get_index(filter, data),
                                            help=text_file(r"./markdown/reasons_for_stop.md"))        
            
        if sidebar:
            col1=nullcontext()
            col2=nullcontext()
            col3=nullcontext()
        else:
            col1, col2, col3 = st.columns(3)

        filter = 'gender'
        data = genders
        with col1:
            selection[filter] = st.selectbox("Gender", data, index=_get_index(filter, data),
                                            help="Filter to show only statistics for a gender")
            
        filter = 'residency'
        data = res
        with col2:
            selection[filter] = st.selectbox("Residency", data, index=_get_index(filter, data),
                                            help="Filter to show only statistics for subjects who are residents of Fairfax County, "+
                                            "other residents of Virginia, or out-of-state residents. "+
                                            "Residency field added in July 2021.")
            
        filter = 'race'
        data = police_data['result']["Race/Ethnicity"].unique()
        if filter in st.session_state['query'] and st.session_state['query'][filter][0] in data:
            default = [x for x in data if x in st.session_state['query'][filter]]
        else:
            default = ["ASIAN/PACIFIC ISLANDER", "BLACK", "LATINO", "WHITE"]
        with col3:
            selection['race'] = st.multiselect("Race/Ethnicity", data,
                                            default=default,
                                            help="Only the selected races/ethnicities will be shown in the charts. "+
                                            "Only affects what is shown. No values are re-calculated. "
                                            "\n\nNOTE: Indigenous is not shown by default due to small numbers.")
        
    return selection