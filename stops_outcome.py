import streamlit as st
import nivo
import data
import streamlit_elements

def stops_outcome_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                    index=1,
                                    help='Time scale to use on time axis of graphs',
                                    key='scale-outcome')

    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
                                   selected_residency, selected_scale, selected_time_stats)

    with streamlit_elements.elements('stops_outcome'):
        # TODO: Add time range to title
        nivo.bar(plot_data['outcome_table'], title="Result of Stop",
                percent=True, stacked=True, columns=selected_races, layout='horizontal', _debug=_debug)
        nivo.plot(plot_data['Arrest Rate'], ylabel="Arrest Rate", time_scale=selected_scale, title="Arrest Rate",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
        nivo.plot(plot_data['Warning Rate'], ylabel="Warning Rate", time_scale=selected_scale, title="Warning Rate",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])