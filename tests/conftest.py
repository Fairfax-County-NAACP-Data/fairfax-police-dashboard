import pytest
import openpolicedata as opd
import pandas as pd

import sys
sys.path.append("./")

import streamlit as st
import streamlit_debug as stdb
stdb.add_debug(st)
import data

@pytest.fixture(scope="session")
def df_gt():
    src = opd.Source("Virginia")
    df = src.load_from_url([2020,2100], "STOPS", agency="Fairfax County Police Department").table

    df["Month"] = df["incident_date"].dt.to_period("M")
    df["Quarter"] = df["incident_date"].dt.to_period("Q")
    df["Race/Ethnicity"] = df["race"].replace({
        "BLACK OR AFRICAN AMERICAN":"BLACK",
        'ASIAN OR NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER':"ASIAN/PACIFIC ISLANDER",
        'AMERICAN INDIAN OR ALASKA NATIVE':"Indigenous".upper()
    }).str.upper()

    eth = ['HISPANIC OR LATINO']
    assert (df["ethnicity"]=='HISPANIC OR LATINO').sum()>0
    assert len(eth)==1
    df.loc[df["ethnicity"] == eth[0], "Race/Ethnicity"] = "LATINO"
    df.loc[df["ethnicity"] == "UNKNOWN", "Race/Ethnicity"] = "UNKNOWN"

    return df

@pytest.fixture(scope="session")
def db_population():
    return data.get_population()

@pytest.fixture(scope="session")
def df_dash():
    return data.get_data()

@pytest.fixture(scope="session")
def gt_population():
    # Populations used based on this link per appendix I
    all_pop = pd.read_csv(r"https://www2.census.gov/programs-surveys/popest/datasets/2020-2021/counties/asrh/cc-est2021-alldata-51.csv")

    pop = all_pop[all_pop["CTYNAME"]=="Fairfax County"]

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
