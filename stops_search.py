import streamlit as st
import nivo
import data
import streamlit_elements

def stops_search_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                    index=1,
                                    help='Time scale to use on time axis of graphs',
                                    key='scale-outcome')

    # plot_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
    #                                selected_residency, selected_scale)
    _, summary_data = data.get_summary_stats(police_data, population, selected_reason, selected_time_stats, selected_gender, selected_residency)

    with streamlit_elements.elements('stops_search'):
        # TODO: Add time range to title
        nivo.bar(summary_data['Search Outcomes'], title="Searches by Result of Stop",
                percent=True, stacked=True, columns=selected_races, layout='horizontal', _debug=_debug)