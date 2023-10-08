import pytest
import pandas as pd

import sys
sys.path.append("./")

import data
from helpers import filter_df, re_col, df_equal
from nivo import to_percent

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize("outcome",["ALL", "NON-ARRESTS"])
def test_counts(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, outcome):
    _, summary_data = data.get_summary_stats(df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    if outcome=="NON-ARRESTS":
        df_all = df_all[df_all['action_taken']!="ARREST"]
        col = 'Search Counts NA'
    else:
        col = 'Search Counts'

    match_both = (df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    match_person_only = (df_all['person_searched']=="YES") & ~(df_all['vehicle_searched']=="YES")
    match_vehicle_only = ~(df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    vc = pd.DataFrame({
        "Person Only":df_all[match_person_only].value_counts(re_col),
        "Vehicle Only":df_all[match_vehicle_only].value_counts(re_col),
        "Both":df_all[match_both].value_counts(re_col)
    }).transpose().fillna(0)

    summary_data[col] = summary_data[col].fillna(0)

    # Transposing because df_equal handles missing rows and INDIGENOUS column is often missing
    df_equal(vc.transpose(), summary_data[col].transpose())

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize("outcome",["ALL", "NON-ARRESTS"])
def test_rates(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, outcome):
    _, summary_data = data.get_summary_stats(df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    if outcome=="NON-ARRESTS":
        if not data._SUBTRACT_ARRESTS:
            raise NotImplementedError()
        df_all = df_all[df_all['action_taken']!="ARREST"]
        col = 'Search Rates NA'
    else:
        col = 'Search Rates'

    match_either = (df_all['person_searched']=="YES") | (df_all['vehicle_searched']=="YES")
    match_both = (df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    match_person_only = (df_all['person_searched']=="YES") & ~(df_all['vehicle_searched']=="YES")
    match_vehicle_only = ~(df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    vc = pd.DataFrame({
        "Person Only":df_all[match_person_only].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "Vehicle Only":df_all[match_vehicle_only].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "Both":df_all[match_both].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "Total":df_all[match_either].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0)
    }).transpose().fillna(0)

    summary_data[col] = summary_data[col].fillna(0)

    # Transposing because df_equal handles missing rows and INDIGENOUS column is often missing
    df_equal(vc.transpose(), summary_data[col].transpose())

 
@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL"])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize("outcome",["ALL", "NON-ARRESTS"])
@pytest.mark.parametrize('selected_scale', ["Monthly","Quarterly","Annually"])
@pytest.mark.parametrize("selected_type",['All', 'Person Only', 'Vehicle Only', 'Both Only'])
def test_rates_by_time(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, outcome, selected_scale, selected_type):
    time_data = data.get_timelines(df_dash, db_population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    if outcome=="NON-ARRESTS":
        if not data._SUBTRACT_ARRESTS:
            raise NotImplementedError()
        df_all = df_all[df_all['action_taken']!="ARREST"]
        col = 'Search Rate NA'
    else:
        col = 'Search Rate'

    db = time_data[col][selected_type]

    if selected_scale in ["Monthly","Quarterly"]:
        gtcols = [selected_scale[:-2], re_col]
    else:
        gtcols = [df_all['incident_date'].dt.to_period("Y"), re_col]

    if selected_type=="All":
        match = (df_all['person_searched']=="YES") | (df_all['vehicle_searched']=="YES")
    elif selected_type=='Person Only':
        match = (df_all['person_searched']=="YES") & ~(df_all['vehicle_searched']=="YES")
    elif selected_type=='Vehicle Only':
        match = ~(df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    else:
        match = (df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")

    vc_all = df_all.groupby(gtcols).size().unstack(fill_value=0)
    vc_result = df_all[match].groupby(gtcols).size().unstack(fill_value=0)
    vc = vc_result.divide(vc_all,fill_value=0)

    df_equal(db, vc)