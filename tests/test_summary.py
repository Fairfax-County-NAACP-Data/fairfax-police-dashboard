import pandas as pd
import pytest
from helpers import filter_df, re_col

import data

exclude = ["MISSING"]

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
def test_total_stops(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency):
    scard, _ = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)    

    assert len(df_all)>0
    assert df_all[re_col].value_counts().to_dict() == scard['Total Stops'].to_dict()

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
def test_stops_per_1000(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency):
    scard, _ = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, num_months = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)    

    assert len(df_all)>0
    vc = df_all[re_col].value_counts()
    vc = (vc / population)[vc.index] * 1000 / num_months * 12
    vc = vc.astype('Float64')
    col = 'Stops per 1000 People^'
    assert set(vc.index)==set(scard[col].index)
    for k in vc.index:
        assert (pd.isnull(vc[k]) and pd.isnull(scard[col][k])) or abs(vc[k] - scard[col][k]) < 1e-7

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
def test_arrest_rate(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency):
    scard, _ = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)    

    assert len(df_all)>0    
    vc = df_all[['action_taken',re_col]].value_counts().unstack(fill_value=0)
    vc = vc.loc['ARREST'].divide(vc.sum(), fill_value=0) * 100
    assert scard['Arrest Rate'].to_dict()==vc.to_dict()

    
@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","MALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize('col',['Search Rate','Search Rate (Non-Arrests Only)*'])
def test_search_rate(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency, col):
    scard, _ = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)
    
    if "Non-Arrests" in col:
        df_all = df_all[df_all['action_taken']!='ARREST']

    assert len(df_all)>0    
    vc = df_all[re_col].value_counts()
    was_searched = (df_all['person_searched']=='YES') | (df_all['vehicle_searched']=='YES')
    vc_search = df_all[was_searched][re_col].value_counts()
    vc = vc_search.divide(vc, fill_value=0) * 100

    index = set(vc.index)
    index.update(scard[col].index)
    for k in index:
        assert ((k not in vc or pd.isnull(vc[k])) and (k not in scard[col] or pd.isnull(scard[col][k]))) or \
            vc[k] == scard[col][k]
