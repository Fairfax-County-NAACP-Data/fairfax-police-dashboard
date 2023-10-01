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
def test_search_counts(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency):
    _, summary_data = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    match_both = (df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    match_person_only = (df_all['person_searched']=="YES") & ~(df_all['vehicle_searched']=="YES")
    match_vehicle_only = ~(df_all['person_searched']=="YES") & (df_all['vehicle_searched']=="YES")
    vc = pd.DataFrame({
        "Person":df_all[match_person_only].value_counts(re_col),
        "Vehicle":df_all[match_vehicle_only].value_counts(re_col),
        "Both":df_all[match_both].value_counts(re_col)
    }).transpose()

    df_equal(vc, summary_data['Search Counts'])

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
def test_outcome_counts(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency):
    _, summary_data = data.get_summary_stats(df_dash, population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    summary_data['reasons'] = to_percent(summary_data['Outcomes'], axis=0)*100

    vc = df_all[['action_taken', re_col]].value_counts().unstack(fill_value=0)
    vc = vc / vc.sum() * 100

    index = set(vc.index)
    index.update(summary_data['reasons'].index)
    for k in index:
        if k not in vc.index:
            assert (summary_data['reasons'].loc[k]==0).all()
        elif k not in summary_data['reasons'].index:
            assert (vc.loc[k]==0).all()
        else:
            assert (vc.loc[k]==summary_data['reasons'].loc[k]).all()

    
@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL"])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize('selected_scale', ["Monthly","Quarterly","Annually"])
@pytest.mark.parametrize("result", ["ARREST","WARNING ISSUED"])
def test_rates(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency, selected_scale, result):
    time_data = data.get_timelines(df_dash, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    df_time = time_data[result.replace(" ISSUED","").title()+" Rate"]

    if selected_scale in ["Monthly","Quarterly"]:
        cols = [selected_scale[:-2], re_col]
    else:
        cols = [df_all['incident_date'].dt.to_period("Y"), re_col]

    vc_all = df_all.groupby(cols).size().unstack(fill_value=0)
    vc_result = df_all[df_all['action_taken']==result].groupby(cols).size().unstack(fill_value=0)
    vc = vc_result.divide(vc_all,fill_value=0)

    df_equal(df_time, vc)