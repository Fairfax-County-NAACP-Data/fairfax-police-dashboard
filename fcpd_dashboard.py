import streamlit as st
from streamlit_logger import get_logger
from datetime import datetime
import openpolicedata as opd

logger = get_logger(level='DEBUG')

__version__ = "1.0.0-beta"

logger.info(datetime.now())
logger.info("VERSIONS:")
logger.info(f"\tOpenPoliceData: {opd.__version__}")
logger.info(f"\tDashboard: {__version__}")

pg = st.navigation(["1_stops.py", '2_arrests.py'], position='top')
pg.run()