import streamlit as st
import nivo
import data
import streamlit_elements

logger = st.session_state['logger']

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

    for k in ['result of stop', 'search type']:
        v = selected_outcome if k=='result of stop' else selected_type
        if k in st.session_state and st.session_state[k]!=v:
            logger.info(f"Value of filter {k} changed to {v}")
    
        st.session_state[k] = v
    
    if selected_outcome=="ALL":
        addon = ""
    else:
        addon = " NA"
        
    if selected_type.upper()=="ALL":
        counts = summary_data['Search Counts'+addon]
        rates = summary_data['Search Rates'+addon]
    else:
        counts = summary_data['Search Counts'+addon].loc[[selected_type],:]
        rates = summary_data['Search Rates'+addon].loc[[selected_type],:]

    min_date, max_date = data.get_date_range(selected_time_stats, data=police_data, residency=selected_residency)
    date_range = f"{min_date.strftime('%B %Y')} - {max_date.strftime('%B %Y')}"

    with streamlit_elements.elements('stops_search'):
        nivo.bar(counts,
                 title=f"Search Counts: {date_range}", stacked=True,
                 columns=selected_races, layout='horizontal',_debug=_debug)
        nivo.bar(rates,
                 title=f"Search Rates: {date_range}", stacked=False,
                 columns=selected_races, layout='vertical',_debug=_debug, label_format=[".1%",".0%"])
        nivo.plot(time_data['Search Rate'+addon][selected_type], ylabel="Search Rate", time_scale=selected_scale, 
                  title=r"Search Rate: % of stops that end in a search",
                columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])