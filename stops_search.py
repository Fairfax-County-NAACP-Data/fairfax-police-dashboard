import streamlit as st
import nivo
import data
import streamlit_elements

def stops_search_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time_stats, selected_time_series, selected_gender, selected_residency, 
                            selected_scale,
                            _debug=False):
    
    if _debug:
        import streamlit_debug as stdb
        stdb.debug_elements(streamlit_elements)

    col1, col2 = st.columns(2)
    with col1:
        selected_outcome = st.selectbox("Filter By Result of Stop", ["ALL", "NON-ARRESTS"],
                                            help='The Community Policing Act does not collect data on the reason for a search '+
                                            'so it is not possible to determine which searches are discretionary in the data. '+
                                            'Non-discretionary searches include searches of person "incident to arrest" and ' +
                                            'inventory vehicle searches of an impounded vehicle. ' + 
                                            'Examining searches of person that do not result in an arrest focuses on searches '+
                                            'more likely to be discretionary and that failed to find contraband serious enough '+
                                            'to result in an arrest.')

    _, summary_data = data.get_summary_stats(police_data, population, selected_reason, selected_time_stats, selected_gender, selected_residency)
    time_data = data.get_timelines(police_data, population, selected_reason, selected_time_series, selected_gender, 
                                   selected_residency, selected_scale)
    
    with col2:
        selected_type = st.selectbox("Filter by Search Type", time_data['Search Rate'].keys())
    
    if selected_outcome=="ALL":
        addon = ""
    else:
        addon = " NA"
        
    if selected_type.upper()=="ALL":
        counts = summary_data['Search Counts'+addon]
        rates = summary_data['Search Rates'+addon]
    else:
        counts = summary_data['Search Counts'+addon].loc[[selected_type.replace(" Only","")],:]
        rates = summary_data['Search Rates'+addon].loc[[selected_type.replace(" Only","")],:]

    with streamlit_elements.elements('stops_search'):
        # TODO: Add time range to title
        # TODO: Throws error when Unknown selected!
        nivo.bar(counts,
                 title="Search Counts", stacked=True,
                 columns=selected_races, layout='horizontal',_debug=_debug)
        nivo.bar(rates,
                 title="Search Rates", stacked=False,
                 columns=selected_races, layout='vertical',_debug=_debug, label_format=[".1%",".0%"])
        nivo.plot(time_data['Search Rate'+addon][selected_type], ylabel="Search Rate", time_scale=selected_scale, 
                  title=r"Search Rate: % of stops that end in a search",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])
        # nivo.plot(time_data['Warning Rate'], ylabel="Warning Rate", time_scale=selected_scale, title="Warning Rate",
        #         columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])