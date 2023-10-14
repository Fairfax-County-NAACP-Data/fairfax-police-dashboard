import streamlit as st

from argparse import ArgumentParser
from datetime import datetime

__version__ = "0.1-beta"

parser = ArgumentParser()
parser.add_argument("-d", "--debug", action='store_true')
parser.add_argument("-t", "--time", action='store', default=None)
parser.add_argument("-r", "--reason", action='store', default=None)
parser.add_argument("-res", "--res", action='store', default=None)
args = parser.parse_args()

if args.debug:
    print('RUNNING IN DEBUG MODE')
    import streamlit_debug as stdb
    # Overwrite streamlit functions with non-functioning versions to enable Python debug
    stdb.add_debug(st)

from stops_summary import stops_summary_dashboard
from stops_timeline import stops_rate_dashboard
from stops_outcome import stops_outcome_dashboard
from stops_search import stops_search_dashboard
from stops_uof import stops_uof_dashboard
from filters import add_filters
from streamlit_logger import create_logger, get_remote_ip
import data

import openpolicedata as opd

def markdown_file(file):
    with open(file) as f:
        text = f.read()

    st.markdown(text)

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

if 'logger' not in st.session_state:
    st.session_state['logger'] = create_logger(name = 'opd-app', level = 'DEBUG')
logger = st.session_state['logger']

logger.info(datetime.now())
logger.info("VERSIONS:")
logger.info(f"\tOpenPoliceData: {opd.__version__}")
logger.info(f"\tDashboard: {__version__}")
logger.info(f"IP: {get_remote_ip()}")

table_type = "STOPS"
agency = "Fairfax County Police Department"

@st.cache_data(show_spinner=False)
def get_data(time):
    return data.get_data()

@st.cache_data(show_spinner=False)
def get_population(time):
    return data.get_population()

st.title("Fairfax County Police Department Stops Data")

# Add input so that new data will be loaded once a day
today = datetime.now().replace(hour=0, minute=0, second=0,microsecond=0)
with st.empty():
    police_data = get_data(today)
    st.markdown("Welcome to Fairfax County XXXXX's dashboard on traffic and pedestrian stops by the Fairfax County Police Department. "+
            "See the `About` section for more information about police stops and the data. See the `Help` section for the basics on navigating "+
            "this dashboard.")

filters = add_filters(police_data, sidebar=sidebar)

if args.time:
    filters['time stats'] = int(args.time) if args.time.isdigit() else args.time
if args.reason:
    filters['reason'] = args.reason
if args.res:
    filters['residency'] = args.res

for k,v in filters.items():
    if k in st.session_state and st.session_state[k]!=v:
        logger.info(f"Value of filter {k} changed to {v}")
    
    st.session_state[k] = v

population = get_population(today)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Summary', "Initial Stop", "Outcomes", "Searches", "Use of Force", "About", "Help"])
with tab1:
    stops_summary_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['gender'], filters['residency'])

with tab2:
    stops_rate_dashboard(police_data, population,filters['race'],
                            filters['reason'], filters['time series'], filters['gender'], filters['residency'],
                            filters['time scale'],
                            _debug=args.debug)
    
with tab3:
    stops_outcome_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time scale'],
                            _debug=args.debug)

with tab4:
    stops_search_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time scale'],
                            _debug=args.debug)

with tab5:
    stops_uof_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['time series'], filters['gender'], filters['residency'], 
                            filters['time scale'],
                            _debug=args.debug)
    
with tab6:
    markdown_file(r"./markdown/about.md")

with tab7:
    markdown_file(r"./markdown/help.md")

st.divider()
st.markdown("The dashboard is generated using Community Policing Act data aggregated by the Virginia State Police. The raw data can be accessed from the "+
            "[Virginia Open Data Portal](https://data.virginia.gov/Public-Safety/Community-Policing-Data-July-1-2020-to-June-30-202/2c96-texw). "
            "[OpenPoliceData](https://openpolicedata.readthedocs.io/) was used to load data into this dashboard " +
            "and is freely available for others to easily download the raw data.")