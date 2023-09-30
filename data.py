from datetime import datetime
import logging
import math
import pandas as pd
import openpolicedata as opd
import streamlit as st

# Default logger that will only print out critical messages
default_logger = logging.getLogger("critical")
default_logger.setLevel(logging.CRITICAL)

def get_population():
    df = load_csv('FairfaxCountyPopulation.csv',index_col="Race/Ethnicity")
    df = df.rename(index={'AAPI':"ASIAN/PACIFIC ISLANDER"})
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

        if len(new_data):
            for t in tables:
                new_months = new_data[t]["Month"].unique()
                # For months in both datasets, replace with new data
                data[t] = data[t][~data[t]['Month'].isin(new_months)]
                data[t] = pd.concat([data[t], new_data[t]], ignore_index=True)
    except:
        pass

    return data

@st.cache_data(show_spinner=False)
def _getdates(data, selected_residency, date_key='result'):
    min_date = data[date_key]["Month"].min()
    max_date = data[date_key]["Month"].max()
    min_residency_date = data[date_key][data[date_key]['residency'].notnull()]["Month"].min()
    if selected_residency!='ALL':
        min_date = min_residency_date

    return min_date, max_date

def _filterdata(data, key, period, gender, residency, return_months=False):
    min_date, max_date = _getdates(data, residency)
    if period == "ALL":
        df = data[key]
    elif period == "MOST RECENT YEAR":
        min_date = max(min_date, max_date-12+1)
        df = data[key][data[key]["Month"]>=min_date]
    else:
        min_date = max(min_date, pd.Period(period, "M"))
        max_date = min(max_date, pd.Period(period, "M")+12-1)
        df = data[key][data[key]["Month"].dt.year==period]

    nmonths = (max_date - min_date).n+1

    if gender != "ALL":
        df = df[df["gender"]==gender]       

    if residency != "ALL":
        df = df[df["residency"]==residency]

    if return_months:
        return df, nmonths
    else:
        return df


def _set_time(df, selected_scale):
    if "annual" in selected_scale.lower():
        df["TimeScale"] = df["Month"].dt.to_timestamp().dt.to_period("Y")
    elif "quarter" in selected_scale.lower():
        df["TimeScale"] = df["Month"].dt.to_timestamp().dt.to_period("Q")
    else:
        df["TimeScale"] = df["Month"]


@st.cache_data(show_spinner=False)
def get_timelines(data, population, reason_for_stop, period, gender, residency, selected_scale):
    df = _filterdata(data, 'result', period, gender, residency)
    df_search = _filterdata(data, 'search', period, gender, residency)
    df_search_na = _filterdata(data, 'search_na', period, gender, residency)

    _set_time(df, selected_scale)
    _set_time(df_search, selected_scale)
    _set_time(df_search_na, selected_scale)

    is_arrest = df["action_taken"]=="ARREST"
    scale_col = "TimeScale"
    if "annual" in selected_scale.lower():
        months = 12
    elif "quarter" in selected_scale.lower():
        months = 3
    else:
        months = 1
    result = {}
    
    if reason_for_stop == "ALL":
        def sum_by_race(df):
            return df.groupby([scale_col,'Race/Ethnicity']).sum(numeric_only=True).sum(axis=1).convert_dtypes().unstack(fill_value=0)
    else:
        def sum_by_race(df):
            return df.groupby([scale_col,'Race/Ethnicity'])[reason_for_stop].sum().unstack(fill_value=0)
        
    result['Total Stops by Race'] = sum_by_race(df)
    total_arrests = sum_by_race(df[is_arrest])
    total_warnings = sum_by_race(df[df["action_taken"]=="WARNING ISSUED"])
    total_searches = sum_by_race(df_search)
    total_searches_na = sum_by_race(df_search_na)

    # TODO: Fix 1st and last months stop rate
    result['Stops per 1000 People^'] = (result['Total Stops by Race'] / population * 1000)[result['Total Stops by Race'].columns] * 12 / months
    result['Arrest Rate'] = total_arrests.divide(result['Total Stops by Race'], fill_value=0)
    result['Warning Rate'] = total_warnings.divide(result['Total Stops by Race'], fill_value=0)
    result['Search Rate'] = total_searches.divide(result['Total Stops by Race'], fill_value=0)
    result['Search Rate (Non-Arrests Only)*'] = total_searches_na.divide(result['Total Stops by Race'], fill_value=0)

    return result

@st.cache_data(show_spinner=False)
def get_summary_stats(data, population, reason_for_stop, period, gender, residency):
    df, months = _filterdata(data, 'result', period, gender, residency, return_months=True)
    df_search = _filterdata(data, 'search', period, gender, residency)
    df_search_na = _filterdata(data, 'search_na', period, gender, residency)

    is_arrest = df["action_taken"]=="ARREST"
    result = {}
    if reason_for_stop == "ALL":
        def sum_by_race(df):
            return df.groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
        def sum_actions(df):
            return df.groupby(['action_taken','Race/Ethnicity']).sum(numeric_only=True).sum(axis=1).convert_dtypes().unstack(fill_value=0)
    else:
        def sum_by_race(df):
            return df.groupby("Race/Ethnicity")[reason_for_stop].sum()
        def sum_actions(df):
            return df.groupby(['action_taken','Race/Ethnicity'])[reason_for_stop].sum().unstack(fill_value=0)
        
    result['Outcomes'] = sum_actions(df)
    result['Total Stops'] = sum_by_race(df)
    total_arrests = sum_by_race(df[is_arrest])
    total_searches = sum_by_race(df_search)
    result['Search Outcomes'] = sum_actions(df_search)
    total_searches_na = sum_by_race(df_search_na)

    result['Stops per 1000 People^'] = (result['Total Stops'] / population * 1000)[result['Total Stops'].index] * 12 / months
    result['Arrest Rate'] = total_arrests.divide(result['Total Stops'], fill_value=0) * 100
    result['Search Rate'] = total_searches.divide(result['Total Stops'], fill_value=0) * 100
    result['Search Rate (Non-Arrests Only)*'] = total_searches_na.divide((result['Total Stops']-total_arrests), fill_value=0) * 100

    df_result = pd.DataFrame({k:v for k,v in result.items() if isinstance(v,pd.Series)})
    result = {k:v for k,v in result.items() if not isinstance(v,pd.Series)}

    return df_result, result


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
        df["Month"] = df["incident_date"].dt.to_period("M")
        df["Quarter"] = df["incident_date"].dt.to_period("Q")
        df["Race/Ethnicity"] = df["race"].replace({
            "BLACK OR AFRICAN AMERICAN":"BLACK",
            'ASIAN OR NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER':"ASIAN/PACIFIC ISLANDER",
            'AMERICAN INDIAN OR ALASKA NATIVE':"Indigenous".upper()
        }).str.upper()

        eth = [x for x in df["ethnicity"].unique() if "HISPANIC" in x and not x.upper().startswith("NOT")]
        if len(eth)!=1:
            raise ValueError(f"Ethnicity not found in {df['ethnicity'].unique() }")
        df.loc[df["ethnicity"] == eth[0], "Race/Ethnicity"] = "LATINO"
        df.loc[df["ethnicity"] == "UNKNOWN", "Race/Ethnicity"] = "UNKNOWN"

        cols = ["Month","Race/Ethnicity",'gender','residency',"action_taken","reason_for_stop"]

        data["result"] = df.value_counts(cols, dropna=False).unstack(fill_value=0)

        was_searched = (df["person_searched"]=="YES") | (df["vehicle_searched"]=="YES")
        data["search"] = df[was_searched].value_counts(cols, dropna=False).unstack(fill_value=0)

        no_arrest = df["action_taken"]!="ARREST"
        data["search_na"] = df[was_searched & no_arrest].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["person_search_na"] = df[(df["person_searched"]=="YES") & no_arrest].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["vehicle_search_na"] = df[(df["vehicle_searched"]=="YES") & no_arrest].value_counts(cols, dropna=False).unstack(fill_value=0)

        data["uof_officer"] = df[df["physical_force_by_officer"]=="YES"].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["uof_subject"] = df[df["physical_force_by_subject"]=="YES"].value_counts(cols, dropna=False).unstack(fill_value=0)

        for k,v in data.items():
            data[k] = v.reset_index()

    return data


def load_csv(csv_filename, *args, **kwargs):
    return pd.read_csv("https://raw.githubusercontent.com/Fairfax-County-NAACP-Data/fcpd-data/main/data/"+
                            csv_filename.replace(" ","%20"), *args, **kwargs)


def update_saved_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):
    data = download_data(source_name, table_type, agency, start_date, logger)
    for k,v in data.items():
        v.to_csv(rf"../fcpd-data/data/{source_name}_{agency}_{table_type}_{k}.csv", index=False)


if __name__ == "__main__":
    import streamlit_debug as stdb
    stdb.add_debug(st)
    # data = get_data()
    # population = get_population()
    # get_scorecard(data, population, "ALL", "ALL")
    update_saved_data("Virginia", "STOPS", "Fairfax County Police Department")