from streamlit_elements import nivo, mui, elements
import pandas as pd
import hashlib

# Nivo colors: https://nivo.rocks/guides/colors/

def bar(data, xlabel=None, ylabel=None, title=None, key=None, 
         stacked=True, layout='vertical', percent=False, columns=None, height=350, 
         _debug=False):
    
    if percent:
        data = data.divide(data.sum(axis=0),axis=1)
        yformat = " >-.1%"
        yaxisformat = ">-.0%"
    else:
        yformat = ""
        yaxisformat = ""

    if columns is not None:
        data = data[columns]

    axis_bottom = {
                'format':yaxisformat,
                'tickSize': 5,
                'tickPadding': 5,
                'tickRotation': 0,
                'legend': xlabel,
                'legendPosition': 'middle',
                'legendOffset': -45
            }
    axis_left = {
            'tickSize': 5,
            'tickPadding': 5,
            'tickRotation': 0,
            'legend': ylabel,
            'legendPosition': 'middle',
            'legendOffset': 32
        }
    if layout=='vertical':
        axis_left['format'] = yaxisformat
        margin_left = 70
    else:
        axis_bottom['format'] = yaxisformat
        margin_left = 175

    DATA = []
    if key is None:
        m = hashlib.sha256()

    if isinstance(data, pd.Series):
        data = pd.DataFrame(data)
    for k,v in data.items():
        if not isinstance(v, pd.Series):
            raise NotImplementedError("Only pandas Series implementation has been completed")
        
        d = v.to_dict()
        d['id'] = k

        if key is None:
            m.update(str.encode(k))
            m.update(b"True" if percent else b"False")
            m.update(b"True" if stacked else b"False")
        DATA.append(d)

    data_keys = [x for x in DATA[0].keys() if x!='id']
            
    if key is None:
        key = m.hexdigest()

    if _debug: return
        
    # https://github.com/okld/streamlit-gallery/blob/ad224abfd5c2bc43a2937fa17c6f392672330688/streamlit_gallery/components/elements/dashboard/pie.py
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
        with mui.Box(sx={"height": height}):
            nivo.Bar(
                    data=DATA,
                    keys=data_keys,
                    margin={ 'top': 10, 'right': 200, 'bottom': 50, 'left': margin_left },
                    padding=0.3,
                    valueFormat=yformat,
                    layout=layout,
                    indexScale={ 'type': 'band', 'round': True },
                    colors={ 'scheme': 'nivo' },
                    defs=[
                        {
                            'id': 'dots',
                            'type': 'patternDots',
                            'background': 'inherit',
                            'color': '#38bcb2',
                            'size': 4,
                            'padding': 1,
                            'stagger': True
                        },
                        {
                            'id': 'lines',
                            'type': 'patternLines',
                            'background': 'inherit',
                            'color': '#eed312',
                            'rotation': -45,
                            'lineWidth': 6,
                            'spacing': 10
                        }
                    ],
                    borderColor={
                        'from': 'color',
                        'modifiers': [
                            [
                                'darker',
                                1.6
                            ]
                        ]
                    },
                    axisBottom=axis_bottom,
                    axisLeft=axis_left,
                    labelSkipWidth=12,
                    labelSkipHeight=12,
                    labelTextColor={
                        'from': 'color',
                        'modifiers': [
                            [
                                'darker',
                                1.6
                            ]
                        ]
                    },
                    legends=[
                        {
                            'dataFrom': 'keys',
                            'anchor': 'bottom-right',
                            'direction': 'column',
                            'justify': False,
                            'translateX': 120,
                            'translateY': 0,
                            'itemsSpacing': 2,
                            'itemWidth': 100,
                            'itemHeight': 20,
                            'itemDirection': 'left-to-right',
                            'itemOpacity': 0.85,
                            'symbolSize': 20,
                            'effects': [
                                {
                                    'on': 'hover',
                                    'style': {
                                        'itemOpacity': 1
                                    }
                                }
                            ]
                        }
                    ],
                    role="application",
                    ariaLabel="Nivo bar chart demo"
            )
            return


def plot(data, xlabel=None, ylabel=None, title=None, key=None, time_scale='monthly', 
         stacked=False, percent=False, columns=None, colors="dark2", height=350,
         _debug=False, yformat=None):
    
    if percent:
        data = data.divide(data.sum(axis=1),axis=0)
        yFormat = " >-.1%"
        yaxisformat = ">-.0%"
    else:
        yFormat = ""
        yaxisformat = ""

    if yformat is not None:
        if isinstance(yformat,list):
            yFormat = ">-"+yformat[0]
            yaxisformat = ">-"+yformat[1]
        else:
            yFormat = ">-"+yformat
            yaxisformat = yFormat

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

    if _debug: return
        
    # https://github.com/okld/streamlit-gallery/blob/ad224abfd5c2bc43a2937fa17c6f392672330688/streamlit_gallery/components/elements/dashboard/pie.py
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
        with mui.Box(sx={"height": height}):
            nivo.Line(
                data=DATA,
                margin={ 'top': 30, 'right': 60, 'bottom': 50, 'left': 60 },
                xScale=xscale,
                xFormat=f"time:{axisBottom['format']}",
                yFormat=yFormat,
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
                colors={ 'scheme': colors },
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