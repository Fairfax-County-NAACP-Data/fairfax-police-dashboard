import streamlit as st
import nivo
import data
import streamlit_elements

def stops_rate_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time, selected_gender, selected_residency,
                            selected_scale,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)

    with streamlit_elements.elements('stops_timeline'):
        nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops",
                columns=selected_races, _debug=_debug)
        nivo.plot(plot_data['Total Stops by Race'], ylabel=r"% of Stops", time_scale=selected_scale, title="Number of Stops (%)",
                percent=True, columns=selected_races, _debug=_debug)
        nivo.plot(plot_data['Stops per 1000 People^'], ylabel="# of Stops", time_scale=selected_scale, title="Stops per 1000 People^",
                columns=selected_races, _debug=_debug, yformat=".1f")