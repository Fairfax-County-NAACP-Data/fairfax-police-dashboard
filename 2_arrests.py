import streamlit as st
import altair as alt

import pandas as pd
import os

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

chart = alt.Chart(df).mark_line().encode(
    x='yearmonth(Date):T',
    y='Total',
    color='Type'
)
st.altair_chart(chart)

chart = alt.Chart(df).mark_line().encode(
    x='yearmonth(Date):T',
    y=perc_label,
    color='Type'
)
st.altair_chart(chart)

st.markdown('Crime data from [FCPD Crime Mapping Dashboard](https://experience.arcgis.com/experience/03bcc658f4f44662ab70308157c31d0e). '+\
            'Charges/Arrests data from [FCPD Arrests Incident Level Data](https://www.fairfaxcounty.gov/police/data/archive). '+\
            'Each row of the Arrests table is a charge. To estimate the number of arrests, which is defined as the number of times that '+
            'FCPD seizes a person to charge them, the number of arrests is estimated based on unique combination of case number and arrest ID.')