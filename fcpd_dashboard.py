import streamlit as st

from argparse import ArgumentParser
from datetime import datetime

from stops_summary import stops_summary_dashboard
from stops_timeline import stops_rate_dashboard
from stops_outcome import stops_outcome_dashboard
from filters import add_filters
from streamlit_logger import create_logger
import data

import openpolicedata as opd

parser = ArgumentParser()
parser.add_argument("-d", "--debug", action='store_true')
args = parser.parse_args()

if args.debug:
    print('RUNNING IN DEBUG MODE')
    import streamlit_debug as stdb
    # Overwrite streamlit functions with non-functioning versions to enable Python debug
    stdb.add_debug(st)

# TODO: Update page_config
st.set_page_config(
    page_title="FCPD Dashboard",
    page_icon="🌃",
    initial_sidebar_state="expanded",
    layout = 'wide',
    menu_items={
        'Report a Bug': "https://github.com/Fairfax-County-NAACP-Data/fairfax-police-dashboard/issues"
    }
)

if 'logger' not in st.session_state:
    st.session_state['logger'] = create_logger(name = 'opd-app', level = 'DEBUG')
logger = st.session_state['logger']

table_type = "STOPS"
agency = "Fairfax County Police Department"

@st.cache_data(show_spinner=False)
def get_data(time):
    return data.get_data()

@st.cache_data(show_spinner=False)
def get_population(time):
    return data.get_population()

# Add input so that new data will be loaded once a day
today = datetime.now().replace(hour=0, minute=0, second=0,microsecond=0)
with st.empty():
    police_data = get_data(today)
    # TODO: Add age range filters
    st.warning("### FOR DEMONSTRATION PURPOSES ONLY: CALCULATION/NUMBERS STILL NEED TO BE VALIDATED.")

filters = add_filters(police_data)

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Summary', "Initial Stop", "Outcomes", "Searches", "Use of Force"])

population = get_population(today)

with tab1:
    stops_summary_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['gender'], filters['residency'])

with tab2:
    stops_rate_dashboard(police_data, population,filters['race'],
                            filters['reason'], filters['time series'], filters['gender'], filters['residency'],
                            _debug=args.debug)
    
with tab3:
    stops_outcome_dashboard(police_data, population, filters['race'],
                            filters['reason'], filters['time stats'], filters['gender'], filters['residency'], 
                            _debug=args.debug)

with tab4:
    st.markdown('# IN PROGRESS')

with tab5:
    st.markdown('### IN PROGRESS')

logger.debug(f'Done with rendering dataframe using OPD Version {opd.__version__}')