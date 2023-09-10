import streamlit as st
import nivo
import data
import streamlit_elements

def stops_outcome_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time, selected_gender, selected_residency, 
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                    index=1,
                                    help='Time scale to use on time axis of graphs',
                                    key='scale-outcome')

    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)

    with streamlit_elements.elements('stops_outcome'):
        nivo.bar(plot_data['outcome'], xlabel="# of Stops", ylabel="Result of Stop", title="Result of Stop",
                percent=True, stacked=True, columns=selected_races, layout='horizontal', axis=0, _debug=_debug)