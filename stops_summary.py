import streamlit as st
import data
import pandas as pd
from util import text_file, stops_per_1000_txt
import math

def stops_summary_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time, selected_gender, selected_residency):
    
        
    # Determine time range
    min_date, max_date = data.get_date_range(selected_time, data=police_data, residency=selected_residency)

    st.header(f"Scorecard for {min_date.strftime('%B %Y')} to {max_date.strftime('%B %Y')}")

    scard, _ = data.get_summary_stats(police_data, population, selected_reason, selected_time, selected_gender, selected_residency)

    if isinstance(scard, str):
        st.error(scard)
    else:
        def getmax(x, type=float):
            return type(x.max()) if (x.notnull() & (x>0)).any() else 1

        stops_per_1000_max = float(scard['Stops per 1000 People'].max())
        stops_per_1000_format = max(1,math.ceil(-math.log10(stops_per_1000_max))) if stops_per_1000_max!=0 and pd.notnull(stops_per_1000_max) else 1
        column_config={
                'Population':  st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=100,
                    format="%0.1f%%",
                    help='Total county population 15 and older. See About tab for details.'
                ),
                "Total Stops": st.column_config.ProgressColumn(
                    format="%d",
                    min_value=0,
                    max_value=getmax(scard['Total Stops'],int),
                    help="Total number of stops for each group in the selected period"
                ),
                "Stops per 1000 People": st.column_config.ProgressColumn(
                    format=f"%0.{stops_per_1000_format}f",
                    min_value=0,
                    max_value=getmax(scard['Stops per 1000 People']),
                    help=stops_per_1000_txt
                )
            }

        help = {"Arrest Rate":"Percent of stops that end in arrest out of the total number of stops for a group",
                "Search Rate":"Percent of stops where a person or vehicle search occurs out of the total number of stops for a group",
                "Search Rate (Non-Arrests Only)":"Percent of stops NOT ending in arrest where a person or vehicle search occurs out of the total number of stops for a group. \n\n"+\
                    text_file("./markdown/non_arrests_searches.md"),
                "Officer Use of Force Rate":"Percent of stops where an officer uses force out of the total number of stops for a group",
                }
        for k in range(0, len(scard.columns)):
            if 'Rate' in scard.columns[k]:
                column_config[scard.columns[k]] = st.column_config.ProgressColumn(
                        min_value=0,
                        max_value=getmax(scard[scard.columns[k]]),
                        format="%0.1f%%",
                        help=help[scard.columns[k]] if scard.columns[k] in help else None
                    )

        st.dataframe(
            scard.loc[selected_races],
            column_config=column_config
        )

    st.caption("*Hover over column headers for column definitions*")

    if len(selected_races)>0:
        disparity_thresh = 1.2

        highest_rate = scard.loc[selected_races]["Stops per 1000 People"].idxmax()
        if pd.notnull(scard.loc[selected_races]["Stops per 1000 People"][highest_rate]) and scard.loc[selected_races]["Stops per 1000 People"][highest_rate]>0:
            msg = f'{highest_rate} individuals were stopped at a rate of {scard.loc[highest_rate]["Stops per 1000 People"]:.{stops_per_1000_format}f} stops'
            if selected_reason != "ALL":
                msg += f" for {selected_reason}"
            msg+=f' per 1000 people (relative to Fairfax Co. population).'
            if highest_rate!="WHITE":
                st.info(msg+f' This is {scard.loc[highest_rate]["Stops per 1000 People"]/scard.loc["WHITE"]["Stops per 1000 People"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
                for x in selected_races:
                    if x!=highest_rate and pd.notnull(scard.loc[x]["Stops per 1000 People"]) and \
                        scard.loc[x]["Stops per 1000 People"]/scard.loc["WHITE"]["Stops per 1000 People"]>disparity_thresh:
                        msg = f'{x} individuals were stopped at a rate of {scard.loc[x]["Stops per 1000 People"]:.{stops_per_1000_format}f} stops'
                        if selected_reason != "ALL":
                            msg += f" for {selected_reason}"
                        msg+=f' per 1000 people (relative to Fairfax Co. population).'
                        st.info(msg+f' This is {scard.loc[x]["Stops per 1000 People"]/scard.loc["WHITE"]["Stops per 1000 People"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
            else:
                st.info(msg)

        highest_rate = scard.loc[selected_races]["Arrest Rate"].idxmax()
        if highest_rate!='WHITE' and pd.notnull(highest_rate) and scard.loc[selected_races]["Arrest Rate"][highest_rate]>0:
            msg = f'{highest_rate} individuals were arrested in {scard.loc[highest_rate]["Arrest Rate"]:.1f}% of stops'
            if selected_reason != "ALL":
                msg += f" for a {selected_reason}"
            if highest_rate!="WHITE":
                st.info(msg+f'. This is {scard.loc[highest_rate]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
                for x in selected_races:
                    if x!=highest_rate and scard.loc[x]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]>disparity_thresh:
                        msg = f'{x} individuals were arrested in {scard.loc[x]["Arrest Rate"]:.1f}% of stops'
                        if selected_reason != "ALL":
                            msg += f" for {selected_reason}"
                        st.info(msg+f'. This is {scard.loc[x]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
            else:
                st.info(msg)

        highest_rate = scard.loc[selected_races]["Search Rate (Non-Arrests Only)"].idxmax()
        if highest_rate!='WHITE' and pd.notnull(highest_rate) and\
            scard.loc[selected_races]["Search Rate (Non-Arrests Only)"][highest_rate]>0:
            msg = f'{highest_rate} individuals were searched in {scard.loc[highest_rate]["Search Rate (Non-Arrests Only)"]:.1f}% of stops where the individual was not arrested'
            if selected_reason != "ALL":
                msg += f" for {selected_reason}"
            if highest_rate!="WHITE":
                st.info(msg+f'. This is {scard.loc[highest_rate]["Search Rate (Non-Arrests Only)"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
                for x in selected_races:
                    if x!=highest_rate and scard.loc[x]["Search Rate (Non-Arrests Only)"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)"]>disparity_thresh:
                        msg = f'{x} individuals were searched in {scard.loc[x]["Search Rate (Non-Arrests Only)"]:.1f}% of stops where the individual was not arrested'
                        if selected_reason != "ALL":
                            msg += f" for {selected_reason}"
                        st.info(msg+f'. This is {scard.loc[x]["Search Rate (Non-Arrests Only)"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)"]:.1f} '+
                            'times higher than the rate for WHITE individuals.')
            else:
                st.info(msg)
