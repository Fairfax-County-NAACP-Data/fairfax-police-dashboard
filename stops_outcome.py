import streamlit as st
import nivo
import data
import streamlit_elements

def stops_outcome_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            selected_scale,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    _, summary_data = data.get_summary_stats(police_data, population, selected_reason, selected_time_stats, selected_gender, selected_residency)
    time_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
                                   selected_residency, selected_scale)
    
    min_date, max_date = data.get_date_range(selected_time_stats, data=police_data, residency=selected_residency)
    date_range = f"{min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}"

    with streamlit_elements.elements('stops_outcome'):
        nivo.bar(summary_data['reasons'], title=f"Reasons for Stop: {date_range}", stacked=True,
                 columns=selected_races, layout='horizontal',_debug=_debug)
        nivo.bar(summary_data['Outcomes'], title=f"Result of Stop: {date_range}",
                percent=True, stacked=True, columns=selected_races, layout='horizontal', _debug=_debug)
        nivo.plot(time_data['Arrest Rate'], ylabel=f"Arrest Rate", time_scale=selected_scale, 
                  title="Arrest Rate", help="Percent of stops that end in arrest out of the total number of stops for a group",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
        nivo.plot(time_data['Warning Rate'], ylabel="Warning Rate", time_scale=selected_scale, title="Warning Rate",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"],
                help="Percent of stops that end in a warning out of the total number of stops for a group. A high warning rate could indicate leniency or that people are being stopped for "+
                "low-level offenses, possibly as a pretext to try to find higher-level offenses after the stop is made.")