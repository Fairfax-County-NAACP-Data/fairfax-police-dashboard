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
@pytest.mark.parametrize("actor", ["Subject","Officer"])
def test_counts(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, actor):
    _, summary_data = data.get_summary_stats(df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)
    
    other = "subject" if actor=="Officer" else "officer"

    match_both = (df_all['physical_force_by_officer']=="YES") & (df_all['physical_force_by_subject']=="YES")
    match_one = (df_all['physical_force_by_'+actor.lower()]=="YES") & (df_all['physical_force_by_'+other]!="YES")
    vc = pd.DataFrame({
        "By "+actor+" Only":df_all[match_one].value_counts(re_col),
        "By Subject and Officer":df_all[match_both].value_counts(re_col)
    }).transpose().fillna(0)

    summary_data[actor+" UoF Counts"] = summary_data[actor+" UoF Counts"].fillna(0)

    # Transposing because df_equal handles missing rows and INDIGENOUS column is often missing
    df_equal(vc.transpose(), summary_data[actor+" UoF Counts"].transpose())

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
def test_rates(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency):
    _, summary_data = data.get_summary_stats(df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    df_all = df_all[df_all['Month']>='2021-07']

    match_both = (df_all['physical_force_by_subject']=="YES") & (df_all['physical_force_by_officer']=="YES")
    match_subject_only = (df_all['physical_force_by_subject']=="YES") & ~(df_all['physical_force_by_officer']=="YES")
    match_officer_only = ~(df_all['physical_force_by_subject']=="YES") & (df_all['physical_force_by_officer']=="YES")
    match_officer = match_officer_only | match_both
    match_subject = match_subject_only | match_both
    vc = pd.DataFrame({
        "By Officer Only":df_all[match_officer_only].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "By Officer Total":df_all[match_officer].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "By Subject and Officer":df_all[match_both].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "By Subject Only":df_all[match_subject_only].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0),
        "By Subject Total":df_all[match_subject].value_counts(re_col).divide(df_all.value_counts(re_col),fill_value=0)
    }).transpose().fillna(0)

    col = 'UoF Rates'
    summary_data[col] = summary_data[col].fillna(0)

    # Transposing because df_equal handles missing rows and INDIGENOUS column is often missing
    df_equal(vc.transpose(), summary_data[col].transpose())

 
@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL"])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize("outcome",["ALL", "NON-ARRESTS"])
@pytest.mark.parametrize('selected_scale', ["Monthly","Quarterly","Annually"])
@pytest.mark.parametrize("actor",['Subject','Officer'])
def test_rates_by_time(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, outcome, selected_scale, actor):
    time_data = data.get_timelines(df_dash, db_population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    col = 'UoF Rate'

    db = time_data[col][actor]

    if selected_scale in ["Monthly","Quarterly"]:
        gtcols = [selected_scale[:-2], re_col]
    else:
        gtcols = [df_all['incident_date'].dt.to_period("Y"), re_col]

    match = df_all['physical_force_by_'+actor.lower()]=="YES"

    vc_all = df_all.groupby(gtcols).size().unstack(fill_value=0)
    vc_result = df_all[match].groupby(gtcols).size().unstack(fill_value=0)
    vc = vc_result.divide(vc_all,fill_value=0)

    df_equal(db, vc)

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL","MOST RECENT YEAR", 2021])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize('uof_type',["By Officer Only","By Officer Total","By Subject Only","By Subject Total","By Subject and Officer"])
def test_outcomes_by_uof(df_gt, df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency, uof_type):
    _, summary_data = data.get_summary_stats(df_dash, db_population, selected_reason, selected_time, selected_gender, selected_residency)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency) 

    df_all = df_all[df_all['Month']>='2021-07']

    is_subject = "Subject" in uof_type
    is_officer = "Officer" in uof_type

    match_both = (df_all['physical_force_by_subject']=="YES") & (df_all['physical_force_by_officer']=="YES")
    if is_subject and is_officer:
        match = match_both
    elif is_subject:
        match = (df_all['physical_force_by_subject']=="YES") & ~(df_all['physical_force_by_officer']=="YES")
    else:
        match = ~(df_all['physical_force_by_subject']=="YES") & (df_all['physical_force_by_officer']=="YES")
    if "Only" not in uof_type:
        match = match | match_both

    vc = df_all[match][["action_taken",re_col]].value_counts().unstack(fill_value=0)
    vc /= vc.sum()
    db = to_percent(summary_data['Uof Outcomes'][uof_type], axis=0)

    # Drop rows that are all zeros
    db = db.loc[db.sum(axis=1)>0]
    vc = vc.loc[vc.sum(axis=1)>0]

    # Transposing because df_equal handles missing rows and INDIGENOUS column is often missing
    df_equal(vc.transpose(),db.transpose())