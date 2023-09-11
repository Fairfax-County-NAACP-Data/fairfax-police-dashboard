import streamlit as st
import data
import pandas as pd

def stops_summary_dashboard(police_data, population, selected_races,
                            selected_reason, selected_time, selected_gender, selected_residency):
    
        
    # Determine time range
    if selected_time == "ALL":
        months = police_data['result']["Month"].unique()
    elif selected_time == "MOST RECENT YEAR":
        most_recent_month = police_data['result']["Month"].max()
        months = police_data['result']["Month"][police_data['result']["Month"]>most_recent_month-12].unique()
    else:
        months = police_data['result']["Month"][police_data['result']["Month"].dt.year==selected_time].unique()

    st.header(f"Scorecard for {months.min().strftime('%B %Y')} to {months.max().strftime('%B %Y')}")

    scard = data.get_scorecard(police_data, population, selected_reason, selected_time, selected_gender, selected_residency)

    if isinstance(scard, str):
        st.error(scard)
    else:
        column_config={
                "Total Stops": st.column_config.ProgressColumn(
                    format="%d",
                    min_value=0,
                    max_value=int(scard['Total Stops'].max()),
                ),
                "Stops per 1000 People^": st.column_config.ProgressColumn(
                    format="%0.1f",
                    min_value=0,
                    max_value=float(scard['Stops per 1000 People^'].max()),
                )
            }

        for k in range(2, len(scard.columns)):
            column_config[scard.columns[k]] = st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=float(scard[scard.columns[k]].max()),
                    format="%0.1f%%"
                )

        st.dataframe(
            scard.loc[selected_races],
            column_config=column_config
        )

    st.warning("There may currently be errors in the Stops per 1000 people!")

    st.caption("^ Calculated on a per year basis  \n"
            "\* In Virginia, individuals are frequently searched during an arrest (i.e. they are searched because they are arrested rather than a search leads to an arrest). "+
            "The data provides no ability to distinguish between searches due to an arrest and discretionary searches and searches due to an arrest are the majority of searches.  "+
            "To focus on discretionary searches, the search rate shown is only for searches that do not end in arrest. Thus, the search rate measures how often officers "+
            "use their discretionary powers to search individuals but are unable to find evidence that leads to an arrest.")

    if len(selected_races)>0:
        disparity_thresh = 1.2
        most_stops = scard.loc[selected_races]["Total Stops"].idxmax()

        msg = f'{most_stops} individuals were stopped the most'
        if selected_reason != "ALL":
            msg += f" for {selected_reason}"
        msg+=f': {int(scard.loc[most_stops]["Total Stops"])} stops'
        st.info(msg)

        highest_rate = scard.loc[selected_races]["Stops per 1000 People^"].idxmax()
        msg = f'{highest_rate} individuals were stopped at a rate of {scard.loc[highest_rate]["Stops per 1000 People^"]:.1f} stops'
        if selected_reason != "ALL":
            msg += f" for {selected_reason}"
        msg+=f' per 1000 people (relative to Fairfax Co. population).'
        if highest_rate!="WHITE":
            st.info(msg+f' This is {scard.loc[highest_rate]["Stops per 1000 People^"]/scard.loc["WHITE"]["Stops per 1000 People^"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
            for x in selected_races:
                if x!=highest_rate and scard.loc[x]["Stops per 1000 People^"]/scard.loc["WHITE"]["Stops per 1000 People^"]>disparity_thresh:
                    msg = f'{x} individuals were stopped at a rate of {scard.loc[x]["Stops per 1000 People^"]:.1f} stops'
                    if selected_reason != "ALL":
                        msg += f" for {selected_reason}"
                    msg+=f' per 1000 people (relative to Fairfax Co. population).'
                    st.info(msg+f' This is {scard.loc[x]["Stops per 1000 People^"]/scard.loc["WHITE"]["Stops per 1000 People^"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
        else:
            st.info(msg)

        highest_rate = scard.loc[selected_races]["Arrest Rate"].idxmax()
        msg = f'{highest_rate} individuals are arrested in {scard.loc[highest_rate]["Arrest Rate"]:.1f}% of stops'
        if selected_reason != "ALL":
            msg += f" for a {selected_reason}"
        if highest_rate!="WHITE":
            st.info(msg+f'. This is {scard.loc[highest_rate]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
            for x in selected_races:
                if x!=highest_rate and scard.loc[x]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]>disparity_thresh:
                    msg = f'{x} individuals are arrested in {scard.loc[x]["Arrest Rate"]:.1f}% of stops'
                    if selected_reason != "ALL":
                        msg += f" for {selected_reason}"
                    st.info(msg+f'. This is {scard.loc[x]["Arrest Rate"]/scard.loc["WHITE"]["Arrest Rate"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
        else:
            st.info(msg)

        highest_rate = scard.loc[selected_races]["Search Rate (Non-Arrests Only)*"].idxmax()
        msg = f'{highest_rate} individuals are searched in {scard.loc[highest_rate]["Search Rate (Non-Arrests Only)*"]:.1f}% of stops that do not end in arrest'
        if selected_reason != "ALL":
            msg += f" for {selected_reason}"
        if highest_rate!="WHITE":
            st.info(msg+f'. This is {scard.loc[highest_rate]["Search Rate (Non-Arrests Only)*"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)*"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
            for x in selected_races:
                if x!=highest_rate and scard.loc[x]["Search Rate (Non-Arrests Only)*"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)*"]>disparity_thresh:
                    msg = f'{x} individuals are searched in {scard.loc[x]["Search Rate (Non-Arrests Only)*"]:.1f}% of stops that do not end in arrest'
                    if selected_reason != "ALL":
                        msg += f" for {selected_reason}"
                    st.info(msg+f'. This is {scard.loc[x]["Search Rate (Non-Arrests Only)*"]/scard.loc["WHITE"]["Search Rate (Non-Arrests Only)*"]:.1f} '+
                        'times higher than the rate for WHITE individuals.')
        else:
            st.info(msg)
        
    st.warning("TODO: Confirm that statistics are correct")
    st.warning("Put data description and/or CPA link somewhere?")
