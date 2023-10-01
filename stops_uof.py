import streamlit as st
import nivo
import data
import streamlit_elements

def stops_uof_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            selected_scale,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    _, summary_data = data.get_summary_stats(police_data, population, selected_reason, selected_time_stats, selected_gender, selected_residency)
    time_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
                                   selected_residency, selected_scale)

    with streamlit_elements.elements('stops_uof'):
        # TODO: Add time range to title
        # TODO: Throws error when Unknown selected!
        nivo.bar(summary_data['Officer UoF Counts'],
                 title="Use of Force By Officer", stacked=True, ylabel="Subject Race",
                 columns=selected_races, layout='horizontal',_debug=_debug,
                 yoffset=-150)
        nivo.bar(summary_data['Subject UoF Counts'],
                 title="Use of Force By Subject", stacked=True, ylabel="Subject Race",
                 columns=selected_races, layout='horizontal',_debug=_debug,
                 yoffset=-150)
        nivo.bar(summary_data['UoF Rates'],
                 title="Use of Force Rates", stacked=False,
                 columns=selected_races, layout='vertical',_debug=_debug, label_format=[".1%",".0%"])
        nivo.plot(time_data['UoF Rate']["Officer"], ylabel="Use of Force Rate", time_scale=selected_scale, 
                  title=r"Officer Use of Force Rate: % of stops that end in an officer using force",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
        nivo.plot(time_data['UoF Rate']["Subject"], ylabel="Use of Force Rate", time_scale=selected_scale, 
                  title=r"Subject Use of Force Rate: % of stops that end in a subject using force",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])