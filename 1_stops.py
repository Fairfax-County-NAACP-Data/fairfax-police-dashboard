import streamlit as st

from stops_summary import stops_summary_dashboard
from stops_timeline import stops_rate_dashboard
from stops_outcome import stops_outcome_dashboard
from stops_search import stops_search_dashboard
from stops_uof import stops_uof_dashboard
from filters import add_filters
from streamlit_logger import get_logger
import data

def markdown_file(file, *args):
    with open(file) as f:
        text = f.read()

    st.markdown(text.format(*args))

sidebar = True

# TODO: Add about menu item. Change icon?
st.set_page_config(
    page_title="FCPD Dashboard",
    page_icon="📊",
    initial_sidebar_state="auto",
    layout = 'wide',
    menu_items={
        'Report a Bug': "mailto:openpolicedata@gmail.com"
    }
)

logger = get_logger(level='DEBUG')

table_type = "STOPS"
agency = "Fairfax County Police Department"

@st.cache_data(show_spinner=False, ttl='7days')
def get_data():
    return data.get_data()

@st.cache_data(show_spinner=False, ttl='7days')
def get_population():
    return data.get_population()

with st.expander('Getting Help', expanded='help_expanded' not in st.session_state) or st.session_state['help_expanded']:
    st.session_state['help_expanded'] = False
    st.caption("See the `Help` tab for basic usage. "+
               "Hover over question marks like the one next to this text for tips and explanations.",
               help="Hover over question mark icons like this one for helpful information!")

st.title("Fairfax County Police Department Stops Data")

with st.empty():
    police_data = get_data()
    st.markdown("Welcome to Fairfax County XXXXX's dashboard on traffic and pedestrian stops by the Fairfax County Police Department. "+
            "See the `About` section for more information about police stops and the data. ")


if 'query' not in st.session_state: # Only occurs during load/reload of page
    st.session_state['query'] = st.query_params.to_dict()

filters = add_filters(police_data, sidebar=sidebar)

if "filters" not in st.session_state:
    st.session_state['filters'] = {}
for k,v in filters.items():
    if k in st.session_state['filters'] and st.session_state['filters'][k]!=v:
        logger.info(f"Value of filter {k} changed to {v}")
    
    st.session_state['filters'][k] = v

population = get_population()

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Introduction', 'Summary', "Initial Stop", "Outcomes", "Searches", "Use of Force", "About", "Help"])

with tab0:
    markdown_file(r"./markdown/intro.md", police_data['result']["Month"].max().strftime('%B %Y'))

with tab1:
    stops_summary_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time_stats'], filters['gender'], filters['residency'])

with tab2:
    stops_rate_dashboard(police_data, population,filters['race'],
                            filters['reason'], filters['time series'], filters['gender'], filters['residency'],
                            filters['time_scale'])
    
with tab3:
    stops_outcome_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time_scale'])

with tab4:
    stops_search_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time_scale'])

with tab5:
    stops_uof_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time_scale'])
    
with tab6:
    markdown_file(r"./markdown/about.md")

with tab7:
    markdown_file(r"./markdown/help.md")

st.divider()
st.markdown("The dashboard is generated using Community Policing Act data aggregated by the Virginia State Police. The raw data can be accessed from the "+
            "[Virginia Open Data Portal](https://data.virginia.gov/Public-Safety/Community-Policing-Data-July-1-2020-to-June-30-202/2c96-texw). "
            "[OpenPoliceData](https://openpolicedata.readthedocs.io/) was used to load data into this dashboard " +
            "and is freely available for others to easily download the raw data.")