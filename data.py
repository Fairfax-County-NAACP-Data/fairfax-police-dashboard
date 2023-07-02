from datetime import datetime
import logging
import math
import pandas as pd
import openpolicedata as opd
import streamlit as st

# Default logger that will only print out critical messages
default_logger = logging.getLogger("critical")
default_logger.setLevel(logging.CRITICAL)

def get_data():
    logger = logging.getLogger("opd-app")

def download_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):

    cur_year = datetime.now().year
    stop_date = f"{cur_year+1}-01-01"

    # TODO: Update start_date based on saved data

    src = opd.Source(source_name)
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

    data = {} 
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

        data["result"] = df.value_counts(["Month","Race/Ethnicity","action_taken","reason_for_stop"]).unstack(fill_value=0)

        was_searched = (df["person_searched"]=="YES") | (df["vehicle_searched"]=="YES")
        data["search"] = df[was_searched].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)

        no_arrest = df["action_taken"]!="ARREST"
        data["search_na"] = df[was_searched & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)
        data["person_search_na"] = df[(df["person_searched"]=="YES") & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)
        data["vehicle_search_na"] = df[(df["vehicle_searched"]=="YES") & no_arrest].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)

    return data


def update_saved_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):
    data = download_data(source_name, table_type, agency, start_date, logger)
    for k,v in data.items():
        v.to_csv(rf"./data/{source_name}_{agency}_{table_type}_{k}.csv")


if __name__ == "__main__":
    import streamlit_debug as stdb
    stdb.add_debug(st)
    update_saved_data("Virginia", "STOPS", "Fairfax County Police Department")