## About
- [Fairfax County XXXXX](#fairfax-county-xxxxx)
- [Virginia Community Policing Act](#virginia-comunity-policing-act)
- [Population Data](#population-data)
- [OpenPoliceData](#openpolicedata)

## Fairfax County XXXXX
Insert description?

## Virginia Comunity Policing Act
Data for this dashboard was collected by the Fairfax County Police Department as required by the [Virginia Community Policing Act](https://law.lis.virginia.gov/vacodefull/title52/chapter6.1/). Data is aggregated by the Virginia State Police and is made available on the Virginia Open Data Portal, which provides a [description](https://data.virginia.gov/stories/s/Virginia-Community-Policing-Act-Data-Collection/rden-cz3h/), and [raw data](https://data.virginia.gov/Public-Safety/Community-Policing-Data-July-1-2020-to-June-30-202/2c96-texw). The [Virginia Community Policing Act](https://law.lis.virginia.gov/vacodefull/title52/chapter6.1/) requires law enforcement officers in Virginia to collect certain data for:
>(i) all investigatory motor vehicle stops, (ii) all stop-and-frisks of a person based on reasonable suspicion, and (iii) all other investigatory detentions that do not result in an arrest or the issuance of a summons

The following data began being collected in July 2020:
- Date of stop
- The race, ethnicity, age, and gender of the person stopped
- Location of the stop
- Reason for the stop: traffic violation, equipment violation, Terry stop (i.e. stop and frisk, check point, or other investigative detenction)
- Whether a warning, written citation, or summons was issued or whether any person was arrested
- If a warning, written citation, or summons was issued or an arrest was made, the most serious violation
- Whether the vehicle or person was searched

The following data began being collected in July 2021:
- Whether the person stopped spoke English
- Whether the law-enforcement officer or State Police officer used physical force against any person
- Whether any person used physical force against any officers
- Residency of person stopped (resident of city/county, other VA resident, out of state resident)
- Whether person stopped was a driver, passenger or individual

The only modification that we make to the raw data accessed from data.virginia.gov is to combine the race and ethnicity columns into a single Race/Ethnicity column. The values of the Race/Ethnicity are equal to the ethnicity if the ethnicity is Hispanic/Latino or Unknown. Otherwise, the value is equal to the race. This calculation is consistent with the formula used by the [Virginia Department of Criminal Justice Services](https://www.dcjs.virginia.gov/) (DCJS) in its annual report ([2023 report](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/report-analysis-traffic-stop-data-fiscal-year-2023.pdf): p. 20) on the Community Policing Act Data.

More specific details on the data and how it is collected can be found in the [Community Policing Data Collection Instructions and Technical Specifications](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/cpad-appendices/2023/Appendix-H.pdf).

## Population Data
Populations are estimated using the same methodology as DCJS as described in [Appendix I](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/cpad-appendices/2023/Appendix-I.pdf) of the 2023 annual Community Policing Act data report. DCJS uses [Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin](https://www.census.gov/data/tables/time-series/demo/popest/2020s-counties-detail.html) from the U.S. Census. The population estimates used by this dashboard can be found [here](https://github.com/Fairfax-County-NAACP-Data/fcpd-data/blob/main/data/FairfaxCountyPopulation.csv).

## OpenPoliceData
The [OpenPoliceData](https://openpolicedata.readthedocs.io/) Python library is used to download the raw Virginia Community Policing Act data from the [Virginia Open Data Portal](https://data.virginia.gov/stories/s/Virginia-Community-Policing-Act-Data-Collection/rden-cz3h/). OpenPoliceData makes it easier to access and analyze police data and provides centralized access to data from over 3500 police agencies including the Virginia agencies covered under the Virginia Community Policing Act.