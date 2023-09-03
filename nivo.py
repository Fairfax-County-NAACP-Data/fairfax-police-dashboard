from streamlit_elements import nivo, mui, elements
from numbers import Number
import pandas as pd
import hashlib

def _plottime(*args, **kwargs):
    data = [
          {
            'id': "LineOne",
            'data': [
              { 'x': "2019-05-01", 'y': 2 },
              { 'x': "2019-06-01", 'y': 7 },
              { 'x': "2020-03-01", 'y': 1 }
            ]
          },
          {
            'id': "LineTwo",
            'data': [
              { 'x': "2019-05-01", 'y': 1 },
              { 'x': "2019-06-01", 'y': 5 },
              { 'x': "2020-05-01", 'y': 5 }
            ]
          },
          {
            'id': "LineThree",
            'data': [
              { 'x': "2020-02-01", 'y': 4 },
              { 'x': "2020-03-01", 'y': 6 },
              { 'x': "2020-04-01", 'y': 1 }
            ]
          }
        ]
    with elements('time_tmp'):
        with mui.Box(sx={"height": 400}):
            nivo.Line(
                data=data,
                margin={ 'top': 50, 'right': 110, 'bottom': 50, 'left': 60 },
                xScale={
                'type': "time",
                'format': "%Y-%m-%d"
                },
                xFormat={'time':"%Y-%m-%d"},
                yScale={
                'type': "linear",
                'min': "auto",
                'max': "auto",
                'stacked': False,
                'reverse': False
                },
                axisTop=None,
                axisRight=None,
                axisLeft={
                'orient': "left",
                'tickSize': 5,
                'tickPadding': 5,
                'tickRotation': 0,
                'legend': "count",
                'legendOffset': -40,
                'legendPosition': "middle"
                },
                axisBottom={
                'format': "%b %d",
                #   'tickValues': "every 2 days",
                #   'tickRotation': -90,
                'legend': "time scale",
                'legendOffset': -12
                },
                colors={ 'scheme': "nivo" },
                pointSize=10,
                pointColor={ 'theme': "background" },
                pointBorderWidth=2,
                pointBorderColor={ 'from': "serieColor" },
                pointLabel="y",
                pointLabelYOffset=-12,
                useMesh=True,
                legends=[
                {
                    'anchor': "bottom-right",
                    'direction': "column",
                    'justify': False,
                    'translateX': 100,
                    'translateY': 0,
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


def plot(data, xlabel=None, ylabel=None, key=None, time_scale='monthly'):

    DATA = []
    if key is None:
        m = hashlib.sha256()
    
    time_scale = time_scale.lower()
    if "quarter" in time_scale:
        time_format = "Q%q %Y"
        # time_format = '%Y-%m'
    elif 'annual' in time_scale:
        time_format = '%Y'
        # time_format = '%Y-%m'
    else:
        time_format = '%Y-%m'

    for k,v in data.items():
        if not isinstance(v, pd.Series):
            raise NotImplementedError("Only pandas Series implementation has been completed")
        
        d = {
            "id":k,
            'data':[{"x":x.strftime(time_format) if isinstance(x, pd.Period) else x, "y":float(y)} for x,y in v.items()]
        }
        if key is None:
            m.update(str.encode(k))
        DATA.append(d)

    xscale = {'type':'linear', 'precision':'day', 'useUTC':False}
    axisBottom = {}
    if isinstance(v.index.dtype, pd.PeriodDtype):
        if "quarter" in time_scale:
            xscale['type'] = 'point'
            xscale['type'] = 'time'
            xscale['format'] = time_format
            axisBottom['format'] = "Q%q %Y"
        elif "annual" in time_scale:
            xscale['type'] = 'point'
            xscale['type'] = 'time'
            xscale['format'] = time_format
            axisBottom['format'] = "%Y"
            axisBottom['tickValues'] = 'every year'
        else:
            xscale['type'] = 'time'
            xscale['format'] = time_format
            axisBottom['format'] = "%b %Y"
            
    if key is None:
        key = m.hexdigest()
        
    if xscale['type']=='time':
        with elements(key):
            with mui.Box(sx={"height": 400}):
                nivo.Line(
                    data=DATA,
                    margin={ 'top': 50, 'right': 110, 'bottom': 50, 'left': 60 },
                    xScale=xscale,
                    yScale={
                        'type': "linear",
                        'min': 0,
                        'max': "auto",
                        'stacked': False,
                        'reverse': False
                    },
                    axisTop=None,
                    axisRight=None,
                    axisLeft={
                        'orient': "left",
                        'tickSize': 5,
                        'tickPadding': 5,
                        'tickRotation': 0,
                        'legend': "count",
                        'legendOffset': -40,
                        'legendPosition': "middle"
                    },
                    axisBottom=axisBottom,
                    colors={ 'scheme': "nivo" },
                    pointSize=10,
                    pointColor={ 'theme': "background" },
                    pointBorderWidth=2,
                    pointBorderColor={ 'from': "serieColor" },
                    pointLabel="y",
                    pointLabelYOffset=-12,
                    useMesh=True,
                    legends=[
                    {
                        'anchor': "bottom-right",
                        'direction': "column",
                        'justify': False,
                        'translateX': 100,
                        'translateY': 0,
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
    else:
        with elements(key+"2"):
            with mui.Box(sx={"height": 400}):
                nivo.Line(data=DATA,
                    margin={ 'top': 50, 'right': 110, 'bottom': 50, 'left': 60 },
                    xScale=xscale,
                    yScale={
                        'type': 'linear',
                        'min': 0,
                        'max': 'auto'
                    },
                    # yFormat=" >-.2f",
                    axisBottom={
                        'tickSize': 5,
                        'tickPadding': 5,
                        'tickRotation': 0,
                        'legend': xlabel,
                        'legendOffset': 36,
                        'legendPosition': 'middle'
                    },
                    axisLeft={
                        'tickSize': 5,
                        'tickPadding': 5,
                        'tickRotation': 0,
                        'legend': ylabel,
                        'legendOffset': -50,
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
