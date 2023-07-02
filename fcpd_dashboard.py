import streamlit as st

from datetime import datetime
import math
import pandas as pd

from streamlit_logger import create_logger
import openpolicedata as opd

debug_mode = True
if debug_mode:
    # Overwrite some streamlit function with non-functioning versions to enable Python debug
    import streamlit_debug as stdb
    stdb.add_debug(st)

# TODO: Update page_config
st.set_page_config(
    page_title="FCPD Dashboard",
    page_icon="🌃",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a Bug': "https://github.com/openpolicedata/OPD_Explorer/issues"
    }
)

if 'logger' not in st.session_state:
    st.session_state['logger'] = create_logger(name = 'opd-app', level = 'DEBUG')
logger = st.session_state['logger']

table_type = "STOPS"
agency = "Fairfax County Police Department"

drop = ["Indigenous"]

@st.cache_data(show_spinner=False)
def get_data():
    start_date = "2020-01-01"
    cur_year = datetime.now().year
    stop_date = f"{cur_year+1}-01-01"

    # TODO: Update start_date based on saved data

    src = opd.Source("Virginia")
    record_count = src.get_count([start_date, stop_date], table_type, agency=agency)
    
    df = []
    batch_size = 5000
    nbatches = math.ceil(record_count / batch_size)
    iter = 0
    wait_text = "Loading most recent data ({} of " + f"{nbatches})"
    pbar = st.progress(0, text=wait_text.format(0))
    for tbl in src.load_from_url_gen(year=[start_date, stop_date], table_type=table_type, nbatch=batch_size, agency=agency):
        iter+=1
        df.append(tbl.table)
        pbar.progress(iter / nbatches, text=wait_text.format(iter))
        
    if len(df)>0:
        df = pd.concat(df)
        logger.debug(f"Table size is {len(df)}")

        df["Month"] = df["incident_date"].dt.to_period("M")
        df["Quarter"] = df["incident_date"].dt.to_period("Q")
        df["Race/Ethnicity"] = df["race"].replace({
            "BLACK OR AFRICAN AMERICAN":"Black",
            'ASIAN OR NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER':"AAPI",
            'AMERICAN INDIAN OR ALASKA NATIVE':"Indigenous"
        }).str.upper()

        eth = [x for x in df["ethnicity"].unique() if "HISPANIC" in x and not x.upper().startswith("NOT")]
        if len(eth)!=1:
            raise ValueError(f"Ethnicity not found in {df['ethnicity'].unique() }")
        df.loc[df["ethnicity"] == eth[0], "Race/Ethnicity"] = "LATINO"
        df.loc[df["ethnicity"] == "UNKNOWN", "Race/Ethnicity"] = "UNKNOWN"

        df = df[~df["Race/Ethnicity"].isin(drop)]

        action_taken_counts = df.value_counts(["Month","Race/Ethnicity","action_taken","reason_for_stop"]).unstack(fill_value=0)

        was_searched = (df["person_searched"]=="YES") | (df["vehicle_searched"]=="YES")
        search_counts = df[was_searched].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)

        no_arrest = df["action_taken"]!="ARREST"
        search_counts_no_arrest = df[was_searched & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)
        person_search_counts_no_arrest = df[(df["person_searched"]=="YES") & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)
        vehicle_search_counts_no_arrest = df[(df["vehicle_searched"]=="YES") & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)

        action_taken_counts.to_csv(rf"./data/{agency}_{table_type}_actions_taken.csv")
        search_counts.to_csv(rf"./data/{agency}_{table_type}_searches.csv")
    else:
        logger.debug("No new data found")

get_data()

logger.debug(f'Done with rendering dataframe using OPD Version {opd.__version__}')