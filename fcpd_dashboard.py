import streamlit as st
import altair as alt
# # import nivo
# import streamlit_elements

import pandas as pd
import os

__version__ = "0.2.1-beta"

crimes = pd.read_csv(os.path.join('data', 'fcpd_crime_totals.csv'))
arrests = pd.read_csv(os.path.join('data', 'fcpd_arrest_totals.csv'))

charges = arrests[['Year','Month','Charges']]
arrests = arrests[['Year','Month','Arrests']]

charges = charges.rename(columns={'Charges':'Total'})
arrests = arrests.rename(columns={'Arrests':'Total'})

crimes['Type'] = 'Crimes'
charges['Type'] = 'Charges'
arrests['Type'] = 'Arrests'

df = pd.concat([crimes, charges, arrests], ignore_index=True)
df['Date'] = df.apply(lambda x: pd.Timestamp(year=int(x['Year']), month=int(x['Month']), day=1), axis=1)

min_date = max([df['Date'][df['Type']==x].min() for x in df['Type'].unique()])

df = df[df['Date']>=min_date]
df = df.sort_values(by='Date').reset_index()

base_date = (min_date + pd.Timedelta(days=31*2)).replace(day=1)
base_count = {x:df['Total'][(df['Type']==x) & (df['Date']==base_date)].iloc[0] for x in df['Type'].unique()}

perc_label = f'% Change Since {df["Date"].iloc[0].strftime("%B %Y")}'

df[perc_label] = df.apply(lambda x: (x['Total']-base_count[x['Type']])/base_count[x['Type']]*100, axis=1)

# st.line_chart(df, x='Date', y=['% Crimes', '% Charges', '% Arrests'], y_label=f'% Change Since {df["Date"].iloc[0].to_period("M")}')
# st.scatter_chart(df, x='% Crimes', y='% Arrests')

chart = alt.Chart(df).mark_line().encode(
    x='yearmonth(Date):T',
    y=perc_label,
    color='Type'
)
st.altair_chart(chart)

# with streamlit_elements.elements('charges v arrests'):
#     nivo.plot(time_data['Arrest Rate'], ylabel=f"Arrest Rate", time_scale=selected_scale, 
#                   title="Arrest Rate", help="Percent of stops that end in arrest out of the total number of stops for a group",
#                 columns=selected_races, _debug=_debug, yformat=[".1%", ".0%"])

# parser = ArgumentParser()
# parser.add_argument("-d", "--debug", action='store_true')
# parser.add_argument("-t", "--time", action='store', default=None)
# parser.add_argument("-r", "--reason", action='store', default=None)
# parser.add_argument("-g", "--gender", action='store', default=None)
# parser.add_argument("-res", "--res", action='store', default=None)
# args = parser.parse_args()


# from stops_summary import stops_summary_dashboard
# from stops_timeline import stops_rate_dashboard
# from stops_outcome import stops_outcome_dashboard
# from stops_search import stops_search_dashboard
# from stops_uof import stops_uof_dashboard
# from filters import add_filters
# from streamlit_logger import get_logger
# import data

# import openpolicedata as opd

# def markdown_file(file, *args):
#     with open(file) as f:
#         text = f.read()

#     st.markdown(text.format(*args))

# sidebar = True

# # TODO: Add about menu item. Change icon?
# st.set_page_config(
#     page_title="FCPD Dashboard",
#     page_icon="📊",
#     initial_sidebar_state="auto",
#     layout = 'wide',
#     menu_items={
#         'Report a Bug': "mailto:openpolicedata@gmail.com"
#     }
# )

# logger = get_logger(level='DEBUG')

# logger.info(datetime.now())
# logger.info("VERSIONS:")
# logger.info(f"\tOpenPoliceData: {opd.__version__}")
# logger.info(f"\tDashboard: {__version__}")

# table_type = "STOPS"
# agency = "Fairfax County Police Department"

# @st.cache_data(show_spinner=False)
# def get_data(time):
#     return data.get_data()

# @st.cache_data(show_spinner=False)
# def get_population(time):
#     return data.get_population()

# with st.expander('Getting Help', expanded='help_expanded' not in st.session_state) or st.session_state['help_expanded']:
#     st.session_state['help_expanded'] = False
#     st.caption("See the `Help` tab for basic usage. "+
#                "Hover over question marks like the one next to this text for tips and explanations.",
#                help="Hover over question mark icons like this one for helpful information!")

# st.title("Fairfax County Police Department Stops Data")

# # Add input so that new data will be loaded once a day
# today = datetime.now().replace(hour=0, minute=0, second=0,microsecond=0)
# with st.empty():
#     police_data = get_data(today)
#     st.markdown("Welcome to Fairfax County XXXXX's dashboard on traffic and pedestrian stops by the Fairfax County Police Department. "+
#             "See the `About` section for more information about police stops and the data. ")

# if 'query' not in st.session_state: # Only occurs during load/reload of page
#     st.session_state['query'] = st.query_params.to_dict()

# filters = add_filters(police_data, sidebar=sidebar)

# if args.time:
#     filters['time_stats'] = int(args.time) if args.time.isdigit() else args.time
# if args.reason:
#     filters['reason'] = args.reason
# if args.gender:
#     filters['gender'] = args.gender
# if args.res:
#     filters['residency'] = args.res

# if "filters" not in st.session_state:
#     st.session_state['filters'] = {}
# for k,v in filters.items():
#     if k in st.session_state['filters'] and st.session_state['filters'][k]!=v:
#         logger.info(f"Value of filter {k} changed to {v}")
    
#     st.session_state['filters'][k] = v

# population = get_population(today)

# tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(['Introduction', 'Summary', "Initial Stop", "Outcomes", "Searches", "Use of Force", "About", "Help"])

# with tab0:
#     markdown_file(r"./markdown/intro.md", police_data['result']["Month"].max().strftime('%B %Y'))

# with tab1:
#     stops_summary_dashboard(police_data, population, filters['race'],
#                             filters['reason'], filters['time_stats'], filters['gender'], filters['residency'])

# with tab2:
#     stops_rate_dashboard(police_data, population,filters['race'],
#                             filters['reason'], filters['time series'], filters['gender'], filters['residency'],
#                             filters['time_scale'],
#                             _debug=args.debug)
    
# with tab3:
#     stops_outcome_dashboard(police_data, population, filters['race'],
#                             filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
#                             filters['time_scale'],
#                             _debug=args.debug)

# with tab4:
#     stops_search_dashboard(police_data, population, filters['race'],
#                             filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
#                             filters['time_scale'],
#                             _debug=args.debug)

# with tab5:
#     stops_uof_dashboard(police_data, population, filters['race'],
#                             filters['reason'], filters['time_stats'], filters['time series'], filters['gender'], filters['residency'], 
#                             filters['time_scale'],
#                             _debug=args.debug)
    
# with tab6:
#     markdown_file(r"./markdown/about.md")

# with tab7:
#     markdown_file(r"./markdown/help.md")

# st.divider()
# st.markdown("The dashboard is generated using Community Policing Act data aggregated by the Virginia State Police. The raw data can be accessed from the "+
#             "[Virginia Open Data Portal](https://data.virginia.gov/Public-Safety/Community-Policing-Data-July-1-2020-to-June-30-202/2c96-texw). "
#             "[OpenPoliceData](https://openpolicedata.readthedocs.io/) was used to load data into this dashboard " +
#             "and is freely available for others to easily download the raw data.")