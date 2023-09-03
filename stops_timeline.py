import streamlit as st
import nivo
import data
import pandas as pd

def stops_timeline_dashboard(police_data, population):
    exclude = ["MISSING"]

    reasons_for_stop = police_data['result'].columns.drop(["Month","Race/Ethnicity",'gender','residency',"action_taken"]).tolist()
    reasons_for_stop.insert(0, "ALL")
    # Reorder
    top = [x for x in ["ALL", "TRAFFIC VIOLATION", "EQUIPMENT VIOLATION", "TERRY STOP"] if x in reasons_for_stop]
    top.extend([x for x in reasons_for_stop if x not in top and x not in exclude])
    reasons_for_stop = top

    time_periods = ["ALL", "MOST RECENT YEAR"]
    time_periods.extend([x for x in range(police_data['result']["Month"].dt.year.max(), 2019, -1)])

    genders = [x for x in police_data['result']["gender"].unique() if x not in exclude]
    genders.insert(0, "ALL")

    res = [x for x in police_data['result']["residency"].unique() if pd.notnull(x) and x not in exclude]
    top = [x for x in res if "COUNTY" in x.upper() and "OUT" not in x.upper() and "OTHER" not in x.upper()]
    top.extend([x for x in res if x not in top])
    res = top
    res.insert(0, "ALL")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_time = st.selectbox("Time Period", time_periods,
                                        help="Filter to show only statistics for selected time period",
                                        key='time-time')
    with col2:
        selected_scale = st.selectbox("Time Scale", ["Monthly",'Quarterly','Annually'], 
                                      index=1,
                                      help='Time scale to use on time axis of graphs',
                                      key='scale-time')
    with col3:
        selected_reason = st.selectbox("Reason For Stop", reasons_for_stop,
                                        # default=reasons_for_stop,
                                        help="Filter to show only statistics for selected reason(s) for stop",
                                        key='reason-time')
    with col4:
        selected_gender = st.selectbox("Gender", genders,
                                        help="Filter to show only statistics for a gender",
                                        key='gender-time')
        
    col1, col2 = st.columns(2)
    with col1:
        selected_residency = st.selectbox("Residency", res,
                                        help="Filter to show only statistics for residency",
                                        key='residency-time')
    with col2:
        selected_races = st.multiselect("Race/Ethnicity", police_data['result']["Race/Ethnicity"].unique(),
                                        default=["ASIAN/PACIFIC ISLANDER", "BLACK", "LATINO", "WHITE"],
                                        help="Select races/ethnicities to show in data below",
                                        key='race-time')
    # selected_scale = "Annually"
    plot_data = data.get_timelines(police_data, population, selected_reason, selected_time, selected_gender, 
                                   selected_residency, selected_scale)

    nivo.plot(plot_data, xlabel="Quarter", ylabel="# of Stops", time_scale=selected_scale)

    return

    DATA = [
    {
        "id": "japan",
        "data": [
        {
            "x": "plane",
            "y": 39
        },
        {
            "x": "helicopter",
            "y": 170
        },
        {
            "x": "boat",
            "y": 15
        },
        {
            "x": "train",
            "y": 274
        },
        {
            "x": "subway",
            "y": 97
        },
        {
            "x": "bus",
            "y": 20
        },
        {
            "x": "car",
            "y": 13
        },
        {
            "x": "moto",
            "y": 271
        },
        {
            "x": "bicycle",
            "y": 161
        },
        {
            "x": "horse",
            "y": 122
        },
        {
            "x": "skateboard",
            "y": 42
        },
        {
            "x": "others",
            "y": 184
        }
        ]
    },
    {
        "id": "france",
        "color": "hsl(289, 70%, 50%)",
        "data": [
        {
            "x": "plane",
            "y": 245
        },
        {
            "x": "helicopter",
            "y": 6
        },
        {
            "x": "boat",
            "y": 267
        },
        {
            "x": "train",
            "y": 84
        },
        {
            "x": "subway",
            "y": 142
        },
        {
            "x": "bus",
            "y": 183
        },
        {
            "x": "car",
            "y": 250
        },
        {
            "x": "moto",
            "y": 182
        },
        {
            "x": "bicycle",
            "y": 139
        },
        {
            "x": "horse",
            "y": 187
        },
        {
            "x": "skateboard",
            "y": 135
        },
        {
            "x": "others",
            "y": 189
        }
        ]
    },
    {
        "id": "us",
        "data": [
        {
            "x": "plane",
            "y": 214
        },
        {
            "x": "helicopter",
            "y": 1
        },
        {
            "x": "boat",
            "y": 178
        },
        {
            "x": "train",
            "y": 75
        },
        {
            "x": "subway",
            "y": 154
        },
        {
            "x": "bus",
            "y": 280
        },
        {
            "x": "car",
            "y": 3
        },
        {
            "x": "moto",
            "y": 147
        },
        {
            "x": "bicycle",
            "y": 144
        },
        {
            "x": "horse",
            "y": 268
        },
        {
            "x": "skateboard",
            "y": 111
        },
        {
            "x": "others",
            "y": 264
        }
        ]
    },
    {
        "id": "germany",
        "data": [
        {
            "x": "plane",
            "y": 79
        },
        {
            "x": "helicopter",
            "y": 181
        },
        {
            "x": "boat",
            "y": 183
        },
        {
            "x": "train",
            "y": 103
        },
        {
            "x": "subway",
            "y": 99
        },
        {
            "x": "bus",
            "y": 183
        },
        {
            "x": "car",
            "y": 22
        },
        {
            "x": "moto",
            "y": 187
        },
        {
            "x": "bicycle",
            "y": 191
        },
        {
            "x": "horse",
            "y": 209
        },
        {
            "x": "skateboard",
            "y": 283
        },
        {
            "x": "others",
            "y": 174
        }
        ]
    },
    {
        "id": "norway",
        "color": "hsl(145, 70%, 50%)",
        "data": [
        {
            "x": "plane",
            "y": 1
        },
        {
            "x": "helicopter",
            "y": 93
        },
        {
            "x": "boat",
            "y": 101
        },
        {
            "x": "train",
            "y": 223
        },
        {
            "x": "subway",
            "y": 104
        },
        {
            "x": "bus",
            "y": 114
        },
        {
            "x": "car",
            "y": 226
        },
        {
            "x": "moto",
            "y": 152
        },
        {
            "x": "bicycle",
            "y": 17
        },
        {
            "x": "horse",
            "y": 176
        },
        {
            "x": "skateboard",
            "y": 121
        },
        {
            "x": "others",
            "y": 123
        }
        ]
    }
    ]

    with elements("timeline_element"):
        with mui.Box(sx={"height": 500}):
            nivo.Line(data=DATA,
                      margin={ 'top': 50, 'right': 110, 'bottom': 50, 'left': 60 },
                        xScale={ 'type': 'point' },
                        yScale={
                            'type': 'linear',
                            'min': 'auto',
                            'max': 'auto',
                            'stacked': True,
                            'reverse': False
                        },
                        yFormat=" >-.2f",
                        axisBottom={
                            'tickSize': 5,
                            'tickPadding': 5,
                            'tickRotation': 0,
                            'legend': 'transportation',
                            'legendOffset': 36,
                            'legendPosition': 'middle'
                        },
                        axisLeft={
                            'tickSize': 5,
                            'tickPadding': 5,
                            'tickRotation': 0,
                            'legend': 'count',
                            'legendOffset': -40,
                            'legendPosition': 'middle'
                        },
                        pointSize=10,
                        pointColor={ 'theme': 'background' },
                        pointBorderWidth=2,
                        pointBorderColor={ 'from': 'serieColor' },
                        pointLabelYOffset=-12,
                        useMesh=True,
                        legends=[
                                {
                                    'anchor': 'bottom-right',
                                    'direction': 'column',
                                    'justify': False,
                                    'translateX': 100,
                                    'translateY': 0,
                                    'itemsSpacing': 0,
                                    'itemDirection': 'left-to-right',
                                    'itemWidth': 80,
                                    'itemHeight': 20,
                                    'itemOpacity': 0.75,
                                    'symbolSize': 12,
                                    'symbolShape': 'circle',
                                    'symbolBorderColor': 'rgba(0, 0, 0, .5)',
                                    'effects': [
                                        {
                                            'on': 'hover',
                                            'style': {
                                                'itemBackground': 'rgba(0, 0, 0, .03)',
                                                'itemOpacity': 1
                                            }
                                        }
                                    ]
                                }
                            ]
                        )

    return

    DATA = [
        { "taste": "fruity", "chardonay": 93, "carmenere": 61, "syrah": 114 },
        { "taste": "bitter", "chardonay": 91, "carmenere": 37, "syrah": 72 },
        { "taste": "heavy", "chardonay": 56, "carmenere": 95, "syrah": 99 },
        { "taste": "strong", "chardonay": 64, "carmenere": 90, "syrah": 30 },
        { "taste": "sunny", "chardonay": 119, "carmenere": 94, "syrah": 103 },
    ]

    with elements("timeline_element"):
        with mui.Box(sx={"height": 500}):
            nivo.Radar(
                    data=DATA,
                    keys=[ "chardonay", "carmenere", "syrah" ],
                    indexBy="taste",
                    valueFormat=">-.2f",
                    margin={ "top": 70, "right": 80, "bottom": 40, "left": 80 },
                    borderColor={ "from": "color" },
                    gridLabelOffset=36,
                    dotSize=10,
                    dotColor={ "theme": "background" },
                    dotBorderWidth=2,
                    motionConfig="wobbly",
                    legends=[
                        {
                            "anchor": "top-left",
                            "direction": "column",
                            "translateX": -50,
                            "translateY": -40,
                            "itemWidth": 80,
                            "itemHeight": 20,
                            "itemTextColor": "#999",
                            "symbolSize": 12,
                            "symbolShape": "circle",
                            "effects": [
                                {
                                    "on": "hover",
                                    "style": {
                                        "itemTextColor": "#000"
                                    }
                                }
                            ]
                        }
                    ],
                    theme={
                        "background": "#FFFFFF",
                        "textColor": "#31333F",
                        "tooltip": {
                            "container": {
                                "background": "#FFFFFF",
                                "color": "#31333F",
                            }
                        }
                    }
                )