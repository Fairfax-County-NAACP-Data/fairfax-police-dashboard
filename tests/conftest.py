import pytest
import openpolicedata as opd

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
def population():
    return data.get_population()

@pytest.fixture(scope="session")
def df_dash():
    return data.get_data()