import streamlit as st

from argparse import ArgumentParser
from datetime import datetime

from stops_summary import stops_summary_dashboard
from stops_timeline import stops_timeline_dashboard
from streamlit_logger import create_logger
import streamlit_debug as stdb
import data

import openpolicedata as opd

parser = ArgumentParser()
parser.add_argument("-d", "--debug", action='store_true')
args = parser.parse_args()

stdb.debug_mode = args.debug
if stdb.debug_mode:
    print('RUNNING IN DEBUG MODE')
    # Overwrite streamlit functions with non-functioning versions to enable Python debug
    stdb.add_debug(st)

# TODO: Update page_config
st.set_page_config(
    page_title="FCPD Dashboard",
    page_icon="🌃",
    initial_sidebar_state="expanded",
    layout = 'wide',
    menu_items={
        'Report a Bug': "https://github.com/openpolicedata/OPD_Explorer/issues"
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
    tab1, tab2 = st.tabs(['Summary', "Timeline"])

population = get_population(today)

with tab1:
    stops_summary_dashboard(police_data, population)

with tab2:
    stops_timeline_dashboard(police_data, population)

logger.debug(f'Done with rendering dataframe using OPD Version {opd.__version__}')