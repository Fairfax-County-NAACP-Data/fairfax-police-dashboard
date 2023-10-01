import pytest

import sys
sys.path.append("./")

import data
from nivo import to_percent
from helpers import filter_df, re_col

@pytest.mark.parametrize("selected_reason", ["ALL", "TRAFFIC VIOLATION"])
@pytest.mark.parametrize("selected_time", ["ALL"])
@pytest.mark.parametrize("selected_gender", ["ALL","FEMALE"])
@pytest.mark.parametrize("selected_residency", ["ALL","RESIDENT OF CITY/COUNTY OF STOP"])
@pytest.mark.parametrize('selected_scale', ["Monthly","Quarterly","Annually"])
def test_total_stops(df_gt, df_dash, population, selected_reason, selected_time, selected_gender, selected_residency, selected_scale):
    plot_data = data.get_timelines(df_dash, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)
    df_all, _ = filter_df(df_gt, selected_reason, selected_time, selected_gender, selected_residency)

    assert len(df_all)>0

    if selected_scale in ["Monthly","Quarterly"]:
        cols = [selected_scale[:-2], re_col]
        scale = 12 if selected_scale == "Monthly" else 4
    else:
        cols = [df_all['incident_date'].dt.to_period("Y"), re_col]
        scale = 1

    vc = df_all.groupby(cols).size().unstack(fill_value=0)
    
    assert vc.to_dict() == plot_data['Total Stops by Race'].to_dict()

    vc_perc = vc.divide(vc.sum(axis=1), axis=0) * 100
    assert (vc_perc.sum(axis=1).round(4)==100).all()

    pcent = to_percent(plot_data['Total Stops by Race'], 1)*100
    assert pcent.to_dict() == vc_perc.to_dict()

    stop_rate = (vc / population)[vc.columns] * 1000 * scale
    assert (stop_rate.columns==plot_data['Stops per 1000 People^'].columns).all()
    assert (stop_rate.index==plot_data['Stops per 1000 People^'].index).all()
    for col in stop_rate.columns:
        assert (stop_rate[col].round(4)==plot_data['Stops per 1000 People^'][col].round(4)).all() or \
            (plot_data['Stops per 1000 People^'][col].isnull().all() and \
             stop_rate[col].isnull().all())