from datetime import datetime
import logging
import math
import pandas as pd
import openpolicedata as opd
import streamlit as st

# Default logger that will only print out critical messages
default_logger = logging.getLogger("critical")
default_logger.setLevel(logging.CRITICAL)

_SUBTRACT_ARRESTS = True

re_replacements = {
            "BLACK OR AFRICAN AMERICAN":"BLACK",
            'ASIAN OR NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER':"ASIAN/PACIFIC ISLANDER",
            'AMERICAN INDIAN OR ALASKA NATIVE':"Indigenous".upper()
        }

def get_population():
    # TODO: Create population table that can be broken down by age and gender
    df = load_csv('FairfaxCountyPopulation.csv',index_col="Race/Ethnicity")
    return df["Population"]

def get_data(source_name="Virginia", table_type="STOPS", agency="Fairfax County Police Department"):
    logger = logging.getLogger("opd-app")

    tables = ["result", "both_searched", 'person_searched_only','vehicle_searched_only', 
              "both_searched_na", 'person_searched_only_na','vehicle_searched_only_na', 
              'uof_officer_only','uof_subject_only','uof_both']
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

    for k in data.keys():
        data[k]['gender'] = data[k]['gender'].fillna("MISSING")
        
    return data

@st.cache_data(show_spinner=False)
def getdates(data, selected_residency, date_key='result'):
    min_date = data[date_key]["Month"].min()
    max_date = data[date_key]["Month"].max()
    min_residency_date = data[date_key][data[date_key]['residency'].notnull()]["Month"].min()
    if selected_residency!='ALL':
        min_date = min_residency_date

    return min_date, max_date

@st.cache_data(show_spinner=False)
def _filterdata_time(data, period, gender, residency):
    return _filterdata(data, period, gender, residency)

@st.cache_data(show_spinner=False)
def _filterdata_summary(data, period, gender, residency):
    return _filterdata(data, period, gender, residency)

def get_date_range(period, min_date=None, max_date=None, data=None, residency=None):
    if min_date is None or max_date is None:
        min_date, max_date = getdates(data, residency)

    if period == "ALL":
        pass
    elif period == "MOST RECENT YEAR":
        min_date = max(min_date, max_date-12+1)
    else:
        min_date = max(min_date, pd.Period(period, "M"))
        max_date = min(max_date, pd.Period(period, "M")+12-1)

    return min_date, max_date

def _filterdata(data, period, gender, residency):
    min_date, max_date = getdates(data, residency)
    result = {}
    for key in data.keys():
        min_date, max_date = get_date_range(period, min_date, max_date)
        if period == "ALL":
            df = data[key]
        elif period == "MOST RECENT YEAR":
            df = data[key][data[key]["Month"]>=min_date]
        else:
            df = data[key][data[key]["Month"].dt.year==period]

        if key=='result':
            nmonths = (max_date - min_date).n+1

        if gender != "ALL":
            df = df[df["gender"]==gender]       

        if residency != "ALL":
            df = df[df["residency"]==residency]

        result[key] = df

    return result, nmonths


def _set_time(df, selected_scale):
    for key in df.keys():
        if "annual" in selected_scale.lower():
            df[key]["TimeScale"] = df[key]["Month"].dt.to_timestamp().dt.to_period("Y")
        elif "quarter" in selected_scale.lower():
            df[key]["TimeScale"] = df[key]["Month"].dt.to_timestamp().dt.to_period("Q")
        else:
            df[key]["TimeScale"] = df[key]["Month"]


@st.cache_data(show_spinner=False)
def get_timelines(data, population, reason_for_stop, period, gender, residency, selected_scale):
    df_filt, _ = _filterdata_time(data, period, gender, residency)

    num_cols = df_filt['person_searched_only'].select_dtypes(include='number').columns
    index = [x for x in df_filt['person_searched_only'].columns if x not in num_cols]
    df_filt['All Searches'] = df_filt['person_searched_only'].set_index(index)\
                                .add(df_filt['vehicle_searched_only'].set_index(index),fill_value=0)\
                                .add(df_filt['both_searched'].set_index(index),fill_value=0)\
                                .reset_index()
    df_filt['All Searches NA'] = df_filt['person_searched_only_na'].set_index(index)\
                                      .add(df_filt['vehicle_searched_only_na'].set_index(index),fill_value=0)\
                                      .add(df_filt['both_searched_na'].set_index(index),fill_value=0)\
                                      .reset_index()
    df_filt['All UoF Officer'] = df_filt['uof_officer_only'].set_index(index)\
                                .add(df_filt['uof_both'].set_index(index),fill_value=0)\
                                .reset_index()
    df_filt['All UoF Subject'] = df_filt['uof_subject_only'].set_index(index)\
                                .add(df_filt['uof_both'].set_index(index),fill_value=0)\
                                .reset_index()

    _set_time(df_filt, selected_scale)

    is_arrest = df_filt['result']["action_taken"]=="ARREST"
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
            if reason_for_stop not in df:
                df = df.copy()
                df[reason_for_stop] = 0
            return df.groupby([scale_col,'Race/Ethnicity'])[reason_for_stop].sum().unstack(fill_value=0)
        
    result['Total Stops by Race'] = sum_by_race(df_filt['result'])
    total_arrests = sum_by_race(df_filt['result'][is_arrest])
    total_warnings = sum_by_race(df_filt['result'][df_filt['result']["action_taken"]=="WARNING ISSUED"])

    result['Stops per 1000 People'] = (result['Total Stops by Race'] / population * 1000)[result['Total Stops by Race'].columns] * 12 / months
    result['Arrest Rate'] = total_arrests.divide(result['Total Stops by Race'], fill_value=0)
    result['Warning Rate'] = total_warnings.divide(result['Total Stops by Race'], fill_value=0)
    result['Search Rate'] = {"All":sum_by_race(df_filt['All Searches']).divide(result['Total Stops by Race'], fill_value=0),
                             "Person Only":sum_by_race(df_filt['person_searched_only']).divide(result['Total Stops by Race'], fill_value=0),
                             "Vehicle Only":sum_by_race(df_filt['vehicle_searched_only']).divide(result['Total Stops by Race'], fill_value=0),
                             "Both Only":sum_by_race(df_filt['both_searched']).divide(result['Total Stops by Race'], fill_value=0),
                             }
    total_stop_na = sum_by_race(df_filt['result'][~is_arrest]) if _SUBTRACT_ARRESTS else result['Total Stops by Race']
    result['Search Rate NA'] = {"All":sum_by_race(df_filt['All Searches NA']).divide(total_stop_na, fill_value=0),
                             "Person Only":sum_by_race(df_filt['person_searched_only_na']).divide(total_stop_na, fill_value=0),
                             "Vehicle Only":sum_by_race(df_filt['vehicle_searched_only_na']).divide(total_stop_na, fill_value=0),
                             "Both Only":sum_by_race(df_filt['both_searched_na']).divide(total_stop_na, fill_value=0),
                             }
    total_stops_cpa_update = result['Total Stops by Race'][result['Total Stops by Race'].index>="2021-07"]
    result['UoF Rate'] = {
                        "Officer":sum_by_race(df_filt['All UoF Officer']).divide(total_stops_cpa_update, fill_value=0),
                        "Subject":sum_by_race(df_filt['All UoF Subject']).divide(total_stops_cpa_update, fill_value=0)
                        }

    return result

@st.cache_data(show_spinner=False)
def get_summary_stats(data, population, reason_for_stop, period, gender, residency):
    df_filt, months = _filterdata_summary(data, period, gender, residency)

    num_cols = df_filt['person_searched_only'].select_dtypes(include='number').columns
    index = [x for x in df_filt['person_searched_only'].columns if x not in num_cols]
    df_filt['All Searches'] = df_filt['person_searched_only'].set_index(index)\
                                .add(df_filt['vehicle_searched_only'].set_index(index),fill_value=0)\
                                .add(df_filt['both_searched'].set_index(index),fill_value=0)\
                                .reset_index()
    df_filt['All Searches NA'] = df_filt['person_searched_only_na'].set_index(index)\
                                      .add(df_filt['vehicle_searched_only_na'].set_index(index),fill_value=0)\
                                      .add(df_filt['both_searched_na'].set_index(index),fill_value=0)\
                                      .reset_index()
    df_filt['All UoF Officer'] = df_filt['uof_officer_only'].set_index(index)\
                                .add(df_filt['uof_both'].set_index(index),fill_value=0)\
                                .reset_index()
    df_filt['All UoF Subject'] = df_filt['uof_subject_only'].set_index(index)\
                                .add(df_filt['uof_both'].set_index(index),fill_value=0)\
                                .reset_index()

    is_arrest = df_filt['result']["action_taken"]=="ARREST"
    result = {}
    if reason_for_stop == "ALL":
        result["reasons"] = df_filt['result'].groupby("Race/Ethnicity").sum(numeric_only=True).transpose()
        def sum_by_race(df):
            return df.groupby("Race/Ethnicity").sum(numeric_only=True).sum(axis=1).convert_dtypes()
        def sum_actions(df):
            return df.groupby(['action_taken','Race/Ethnicity']).sum(numeric_only=True).sum(axis=1).convert_dtypes().unstack(fill_value=0)
    else:
        result["reasons"] = df_filt['result'].groupby("Race/Ethnicity")[[reason_for_stop]].sum().transpose()
        def sum_by_race(df):
            if reason_for_stop in df:
                return df.groupby("Race/Ethnicity")[reason_for_stop].sum()
            else:
                return pd.Series({k:0 for k in df["Race/Ethnicity"].unique()}, name=reason_for_stop)
        def sum_actions(df):
            if reason_for_stop not in df:
                df = df.copy()
                df[reason_for_stop] = 0
            return df.groupby(['action_taken','Race/Ethnicity'])[reason_for_stop].sum().unstack(fill_value=0)

        
    result['Outcomes'] = sum_actions(df_filt['result'])
    result['Total Stops'] = sum_by_race(df_filt['result'])
    total_stops_cpa_update = sum_by_race(df_filt['result'][df_filt['result']["Month"]>="2021-07"])
    result['Search Counts'] = pd.DataFrame({"Person Only":sum_by_race(df_filt['person_searched_only']),
                                            "Vehicle Only":sum_by_race(df_filt['vehicle_searched_only']),
                                            "Both":sum_by_race(df_filt['both_searched'])}).transpose()
    search_rate_total = sum_by_race(df_filt['All Searches']).divide(result['Total Stops'], fill_value=0)
    result['Search Rates'] = pd.DataFrame({"Person Only":result['Search Counts'].loc["Person Only"].divide(result['Total Stops'], fill_value=0),
                                            "Vehicle Only":result['Search Counts'].loc["Vehicle Only"].divide(result['Total Stops'], fill_value=0),
                                            "Both":result['Search Counts'].loc["Both"].divide(result['Total Stops'], fill_value=0),
                                            "Total":search_rate_total}).transpose()
    result['Search Counts NA'] = pd.DataFrame({"Person Only":sum_by_race(df_filt['person_searched_only_na']),
                                            "Vehicle Only":sum_by_race(df_filt['vehicle_searched_only_na']),
                                            "Both":sum_by_race(df_filt['both_searched_na'])}).transpose()
    total_stop_na = sum_by_race(df_filt['result'][df_filt['result']['action_taken']!="ARREST"]) if _SUBTRACT_ARRESTS else result['Total Stops']
    search_rate_total_na = sum_by_race(df_filt['All Searches NA']).divide(total_stop_na, fill_value=0)
    result['Search Rates NA'] = pd.DataFrame({"Person Only":result['Search Counts NA'].loc["Person Only"].divide(total_stop_na, fill_value=0),
                                            "Vehicle Only":result['Search Counts NA'].loc["Vehicle Only"].divide(total_stop_na, fill_value=0),
                                            "Both":result['Search Counts NA'].loc["Both"].divide(total_stop_na, fill_value=0),
                                            "Total":search_rate_total_na}).transpose()
    result['Subject UoF Counts'] = pd.DataFrame({"By Subject Only":sum_by_race(df_filt['uof_subject_only']),
                                            "By Subject and Officer":sum_by_race(df_filt['uof_both']),
                                            }).transpose().astype('float64')
    result['Officer UoF Counts'] = pd.DataFrame({"By Officer Only":sum_by_race(df_filt['uof_officer_only']),
                                            "By Subject and Officer":sum_by_race(df_filt['uof_both']),
                                            }).transpose().astype('float64')
    subject_uof_rate_total = sum_by_race(df_filt['All UoF Subject']).divide(total_stops_cpa_update, fill_value=0)
    officer_uof_rate_total = sum_by_race(df_filt['All UoF Officer']).divide(total_stops_cpa_update, fill_value=0)
    result['UoF Rates'] = pd.DataFrame({"By Officer Only":result['Officer UoF Counts'].loc["By Officer Only"].divide(total_stops_cpa_update, fill_value=0),
                                        "By Officer Total":officer_uof_rate_total,
                                        "By Subject and Officer":result['Subject UoF Counts'].loc["By Subject and Officer"].divide(total_stops_cpa_update, fill_value=0),
                                        "By Subject Only":result['Subject UoF Counts'].loc["By Subject Only"].divide(total_stops_cpa_update, fill_value=0),
                                        "By Subject Total":subject_uof_rate_total,
                                        }).transpose()

    result['Stops per 1000 People'] = (result['Total Stops'] / population * 1000)[result['Total Stops'].index] * 12 / months
    result['Arrest Rate'] = sum_by_race(df_filt['result'][is_arrest]).divide(result['Total Stops'], fill_value=0) * 100
    result['Search Rate'] = search_rate_total * 100
    result['Search Rate (Non-Arrests Only)'] = search_rate_total_na * 100
    result['Officer Use of Force Rate'] = officer_uof_rate_total * 100

    result['Uof Outcomes'] = {
        "By Officer Only":sum_actions(df_filt['uof_officer_only']),
        "By Officer Total":sum_actions(df_filt['All UoF Officer']),
        "By Subject and Officer":sum_actions(df_filt['uof_both']),
        "By Subject Only":sum_actions(df_filt['uof_subject_only']),
        "By Subject Total":sum_actions(df_filt['All UoF Subject'])
    }

    df_result = pd.DataFrame({k:v for k,v in result.items() if isinstance(v,pd.Series)})
    result = {k:v for k,v in result.items() if not isinstance(v,pd.Series)}

    return df_result, result


def download_population(agency, logger=default_logger):
    # 2023 CPA report:
    # https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/report-analysis-traffic-stop-data-fiscal-year-2023.pdf

    # Populations used based on this link per appendix I
    all_pop = pd.read_csv(r"https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/counties/asrh/cc-est2021-alldata-51.csv")

    locale = agency.replace("Police Department","").replace("Sheriff's Department","").replace("Sheriff's Office","").strip()

    pop = all_pop[all_pop["CTYNAME"]==locale]

    if not len(pop):
        raise ValueError(f"Population data for location {locale} and agency {agency} not found")

    # Per Appendix I: "The four youngest age groups—together spanning ages 0-14—were dropped 
    # from the benchmark estimates, leaving a driving-age sample of individuals ages 15 and older."
    # Remove age groups 0-3
    pop = pop[pop['AGEGRP']>3]

    # Appendix I: Estimates for 2021 were used
    # Per https://www2.census.gov/programs-surveys/popest/technical-documentation/file-layouts/2020-2022/cc-est2022-alldata.pdf
    # The key for the YEAR variable is as follows: 
    # 1 = 4/1/2020 population estimates base 
    # 2 = 7/1/2020 population estimate 
    # 3 = 7/1/2021 population estimate
    # 4 = 7/1/2022 population estimate 
    pop = pop[pop["YEAR"]==3]

    # Add up across age groups
    pop = pop.sum()

    # Calculations based on Table I-1 in Appendix I
    cpa_labels = ["WHITE", "BLACK", 'INDIGENOUS', 
            'ASIAN/PACIFIC ISLANDER', 
            'LATINO' ]
    census_labels = [['NHWA'], ['NHBA'], ['NHIA'], ['NHAA', 'NHNA'], ['H']]

    # Convert to upper case 
    cpa_labels = [x.upper() for x in cpa_labels]

    for k in range(len(cpa_labels)):
        pop[cpa_labels[k]] = pop[census_labels[k][0]+"_MALE"] + pop[census_labels[k][0]+"_FEMALE"]
        for j in range(len(census_labels[k])-1):
            pop[cpa_labels[k]] += pop[census_labels[k][j+1]+"_MALE"] + pop[census_labels[k][j+1]+"_FEMALE"]

    total = pop["TOT_POP"]

    # Only keep CPA labels that were added
    pop = pop[cpa_labels]
    pop['OTHER'] = total - pop.sum()

    pop.index.name = "Race/Ethnicity"
    pop.name = 'Population'

    return pop


def download_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):
    # TODO: Add age group

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
        df = pd.concat(df, ignore_index=True)
        df = df.drop_duplicates()
        df["Month"] = df["incident_date"].dt.to_period("M")
        df["Quarter"] = df["incident_date"].dt.to_period("Q")
        df["Race/Ethnicity"] = df["race"].replace(re_replacements).str.upper()

        eth = [x for x in df["ethnicity"].unique() if "HISPANIC" in x and not x.upper().startswith("NOT")]
        if len(eth)!=1:
            raise ValueError(f"Ethnicity not found in {df['ethnicity'].unique() }")
        df.loc[df["ethnicity"] == eth[0], "Race/Ethnicity"] = "LATINO"
        df.loc[df["ethnicity"] == "UNKNOWN", "Race/Ethnicity"] = "UNKNOWN"

        cols = ["Month","Race/Ethnicity",'gender','residency',"action_taken","reason_for_stop"]

        data["result"] = df.value_counts(cols, dropna=False).unstack(fill_value=0)

        person_searched = df["person_searched"]=="YES"
        vehicle_searched = df["vehicle_searched"]=="YES"
        data["person_searched_only"] = df[person_searched&~vehicle_searched].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["vehicle_searched_only"] = df[vehicle_searched&~person_searched].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["both_searched"] = df[vehicle_searched&person_searched].value_counts(cols, dropna=False).unstack(fill_value=0)

        no_arrest = df["action_taken"]!="ARREST"
        data["person_searched_only_na"] = df[no_arrest&person_searched&~vehicle_searched].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["vehicle_searched_only_na"] = df[no_arrest&vehicle_searched&~person_searched].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["both_searched_na"] = df[no_arrest&vehicle_searched&person_searched].value_counts(cols, dropna=False).unstack(fill_value=0)

        officer = df["physical_force_by_officer"]=="YES"
        subject = df["physical_force_by_subject"]=="YES"
        data["uof_officer_only"] = df[officer&~subject].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["uof_subject_only"] = df[~officer&subject].value_counts(cols, dropna=False).unstack(fill_value=0)
        data["uof_both"] = df[officer&subject].value_counts(cols, dropna=False).unstack(fill_value=0)

        for k,v in data.items():
            data[k] = v.reset_index()

    return data


def load_csv(csv_filename, *args, **kwargs):
    return pd.read_csv("https://raw.githubusercontent.com/Fairfax-County-NAACP-Data/fcpd-data/main/data/"+
                            csv_filename.replace(" ","%20"), *args, **kwargs)


def update_saved_data(source_name, table_type, agency, start_date="2020-01-01", logger=default_logger):
    population = download_population(agency)
    population.to_csv(rf"../fcpd-data/data/FairfaxCountyPopulation.csv", index=True)

    data = download_data(source_name, table_type, agency, start_date, logger)
    for k,v in data.items():
        v.to_csv(rf"../fcpd-data/data/{source_name}_{agency}_{table_type}_{k}.csv", index=False)


if __name__ == "__main__":
    import streamlit_debug as stdb
    stdb.add_debug(st)
    update_saved_data("Virginia", "STOPS", "Fairfax County Police Department")