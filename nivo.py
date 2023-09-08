from streamlit_elements import nivo, mui, elements
from numbers import Number
import pandas as pd
import hashlib


def plot(data, xlabel=None, ylabel=None, title=None, key=None, time_scale='monthly', 
         stacked=False, percent=False, columns=None):
    
    if percent:
        data = data.divide(data.sum(axis=1),axis=0)
        yformat = " >-.1%"
        yaxisformat = ">-.0%"
    else:
        yformat = ""
        yaxisformat = ""

    if columns is not None:
        data = data[columns]

    DATA = []
    if key is None:
        m = hashlib.sha256()
    
    time_scale = time_scale.lower()
    if "quarter" in time_scale:
        time_format = "Q%q %Y"
    elif 'annual' in time_scale:
        time_format = '%Y'
    else:
        time_format = '%Y-%m'

    if isinstance(data, pd.Series):
        data = pd.DataFrame(data)
    for k,v in data.items():
        if not isinstance(v, pd.Series):
            raise NotImplementedError("Only pandas Series implementation has been completed")
        
        d = {
            "id":k,
            'data':[{"x":x.strftime(time_format) if isinstance(x, pd.Period) else x, "y":float(y)} for x,y in v.items()]
        }
        if key is None:
            m.update(str.encode(k))
            m.update(b"True" if percent else b"False")
            m.update(b"True" if stacked else b"False")
        DATA.append(d)

    xscale = {'type':'linear', 'precision':'day', 'useUTC':False}
    axisBottom = {'legend': xlabel,
                'legendOffset': 36,
                'legendPosition': 'middle'}
    if isinstance(v.index.dtype, pd.PeriodDtype):
        xscale['type'] = 'time'
        xscale['format'] = time_format
        if "quarter" in time_scale:
            axisBottom['format'] = "Q%q %Y"
        elif "annual" in time_scale:
            axisBottom['format'] = "%Y"
            axisBottom['tickValues'] = 'every year'
        else:
            axisBottom['format'] = "%b %Y"
            
    if key is None:
        key = m.hexdigest()
        
    # https://github.com/okld/streamlit-gallery/blob/ad224abfd5c2bc43a2937fa17c6f392672330688/streamlit_gallery/components/elements/dashboard/pie.py
    with elements(key):
        if title:
            with mui.Stack(
                    alignItems="center",
                    direction="row",
                    spacing=1,
                    sx={
                        "padding": "5px 15px 5px 15px",
                        "borderBottom": 1,
                        "borderColor": "divider",
                    },
                ):
                    mui.icon.Timeline()
                    mui.Typography(title, sx={"flex": 1})
        with mui.Paper(key=key, sx={"display": "flex", "flexDirection": "column", "borderRadius": 3, "overflow": "hidden"}, elevation=1):
            with mui.Box(sx={"height": 400}):
                nivo.Line(
                    data=DATA,
                    margin={ 'top': 30, 'right': 60, 'bottom': 50, 'left': 60 },
                    xScale=xscale,
                    xFormat=f"time:{axisBottom['format']}",
                    yFormat=yformat,
                    yScale={
                        'type': "linear",
                        'min': 0,
                        'max': "auto",
                        'stacked': stacked,
                        'reverse': False
                    },
                    enableArea=stacked,
                    axisLeft={
                        'orient': "left",
                        'tickSize': 5,
                        'tickPadding': 5,
                        'format':yaxisformat,
                        'tickRotation': 0,
                        'legend': ylabel,
                        'legendOffset': -50,
                        'legendPosition': "middle"
                    },
                    axisBottom=axisBottom,
                    colors={ 'scheme': "set3" },
                    enableSlices='x',
                    pointSize=10,
                    pointColor={ 'theme': "background" },
                    pointBorderWidth=2,
                    pointBorderColor={ 'from': "serieColor" },
                    pointLabel="y",
                    pointLabelYOffset=-12,
                    useMesh=True,
                    legends=[
                    {
                        'anchor': "top-left",
                        'direction': "row",
                        'justify': False,
                        'translateX': 0,
                        'translateY': -20,
                        'itemsSpacing': 0,
                        'itemDirection': "left-to-right",
                        'itemWidth': 80,
                        'itemHeight': 20,
                        'itemOpacity': 0.75,
                        'symbolSize': 12,
                        'symbolShape': "circle",
                        'symbolBorderColor': "rgba(0, 0, 0, .5)",
                        'effects': [
                        {
                            'on': "hover",
                            'style': {
                            'itemBackground': "rgba(0, 0, 0, .03)",
                            'itemOpacity': 1
                            }
                        }
                        ]
                    }
                    ]
                )