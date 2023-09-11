import streamlit as st
import nivo
import data
import streamlit_elements

def stops_rate_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time, selected_gender, selected_residency,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                    index=1,
                                    help='Time scale to use on time axis of graphs',
                                    key='scale-time')

    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)

    total_stops = plot_data['Total Stops by Race'][selected_races].sum(axis=1)
    total_stops.name = 'Total Stops'
    with streamlit_elements.elements('stops_timeline'):
        nivo.plot(total_stops, ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops", _debug=_debug)
        nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops (Stacked): Number of StopsALTERNATIVE",
                stacked=True, columns=selected_races, colors='set3', _debug=_debug)
        nivo.plot(plot_data['Total Stops by Race'], ylabel="# of Stops", time_scale=selected_scale, title="Number of Stops (%)",
                percent=True, columns=selected_races, _debug=_debug)
        nivo.plot(plot_data['Stops per 1000 People^'], ylabel="# of Stops", time_scale=selected_scale, title="Stops per 1000 People^ (Likely errors in these values!)",
                columns=selected_races, _debug=_debug)