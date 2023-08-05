from datetime import datetime
import logging
import os
import math
import pandas as pd
import openpolicedata as opd
import streamlit as st

# Default logger that will only print out critical messages
default_logger = logging.getLogger("critical")
default_logger.setLevel(logging.CRITICAL)

def get_population():
    df = load_csv('FairfaxCountyPopulation.csv',index_col="Race/Ethnicity")
    return df["Population"]

def get_data(source_name="Virginia", table_type="STOPS", agency="Fairfax County Police Department"):
    logger = logging.getLogger("opd-app")

    tables = ["result", "search", "search_na", "person_search_na", "vehicle_search_na",'uof_officer','uof_subject']
    data = {}
    for t in tables:
        csv_filename = f"{source_name}_{agency}_{table_type}_{t}.csv"
        data[t] = load_csv(csv_filename)
        data[t]["Month"] = pd.to_datetime(data[t]["Month"], errors="coerce").dt.to_period("M")
        
    start_date = max([x["Month"].max() for x in data.values()])
    start_date = str(start_date)+"-01"

    # Try to update with most recent data
    try:
        new_data = download_data(source_name, table_type, agency, start_date=start_date, logger=logger)

        for t in tables:
            new_months = new_data[t]["Month"].unique()
            # For months in both datasets, replace with new data
            data[t] = data[t][~data[t]['Month'].isin(new_months)]
            data[t] = pd.concat([data[t], new_data[t]], ignore_index=True)
    except:
        pass

    return data

def get_scorecard(data, population, reason_for_stop, period):
    if period == "ALL":
        months = data['result']["Month"].unique()
        df = data['result']
        # df_search = data['search']
        df_search_na = data['search_na']
    elif period == "MOST RECENT YEAR":
        most_recent_month = data['result']["Month"].max()
        months = data['result']["Month"][data['result']["Month"]>most_recent_month-12].unique()
        df = data['result'][data['result']["Month"]>most_recent_month-12]
        # df_search = data['search'][data['search']["Month"]>most_recent_month-12]
        df_search_na = data['search_na'][data['search_na']["Month"]>most_recent_month-12]
    else:
        months = data['result']["Month"][data['result']["Month"].dt.year==data].unique()
        df = data['result'][data['result']["Month"].dt.year==period]
        # df_search = data['search'][data['search']["Month"].dt.year==period]
        df_search_na = data['search_na'][data['search_na']["Month"].dt.year==period]

    is_arrest = df["action_taken"]=="ARREST"
    result = {}
    if reason_for_stop == "ALL":
        result['Total Stops'] = df.groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
        total_arrests = df[is_arrest].groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
        # total_searches = df_search.groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
        total_searches_na = df_search_na.groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
    else:
        result['Total Stops'] = df.groupby("Race/Ethnicity")[reason_for_stop].sum()
        total_arrests = df[is_arrest].groupby("Race/Ethnicity")[reason_for_stop].sum()
        # total_searches = df_search.groupby("Race/Ethnicity")[reason_for_stop].sum()
        total_searches_na = df_search_na.groupby("Race/Ethnicity")[reason_for_stop].sum()

    result['Stops per 1000 People'] = (result['Total Stops'] / population * 1000)[result['Total Stops'].index]
    result['Arrest Rate'] = total_arrests / result['Total Stops'] * 100
    # result['Search Rate'] = total_searches / result['Total Stops'] * 100
    result['Search Rate (Non-Arrests Only)*'] = total_searches_na / (result['Total Stops']) * 100

    return pd.DataFrame(result)


def download_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):

    cur_year = datetime.now().year
    stop_date = f"{cur_year+1}-01-01"

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
            "BLACK OR AFRICAN AMERICAN":"BLACK",
            'ASIAN OR NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER':"AAPI",
            'AMERICAN INDIAN OR ALASKA NATIVE':"Indigenous".upper()
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

        data["uof_officer"] = df[df["physical_force_by_officer"]=="YES"].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)
        data["uof_subject"] = df[df["physical_force_by_subject"]=="YES"].value_counts(["Month","Race/Ethnicity","reason_for_stop"]).unstack(fill_value=0)

        for k,v in data.items():
            data[k] = v.reset_index()

    return data


def load_csv(csv_filename, *args, **kwargs):
    try:
        return pd.read_csv("https://raw.githubusercontent.com/Fairfax-County-NAACP-Data/fcpd-data/main/data/"+
                            csv_filename.replace(" ","%20"), *args, **kwargs)
    except Exception as e:
        if os.path.exists(os.path.join(r"..\fcpd-data\data", csv_filename)):
            try:
                print(f"LOADING CSV {csv_filename} FROM LOCAL FILE!!!")
                return pd.read_csv(os.path.join(r"..\fcpd-data\data", csv_filename), *args, **kwargs)
            except:
                raise e
        else:
            raise e


def update_saved_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):
    data = download_data(source_name, table_type, agency, start_date, logger)
    for k,v in data.items():
        v.to_csv(rf"../fcpd-data/data/{source_name}_{agency}_{table_type}_{k}.csv")


if __name__ == "__main__":
    import streamlit_debug as stdb
    stdb.add_debug(st)
    data = get_data()
    population = get_population()
    get_scorecard(data, population, "ALL", "ALL")
    a = 1
    # update_saved_data("Virginia", "STOPS", "Fairfax County Police Department")