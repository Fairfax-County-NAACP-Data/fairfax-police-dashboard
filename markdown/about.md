## About
- [Fairfax County XXXXX](#fairfax-county-xxxxx)
- [Virginia Community Policing Act](#virginia-comunity-policing-act)
- [Population Data](#population-data)
- [OpenPoliceData](#openpolicedata)

## Fairfax County XXXXX
Insert description?

## Virginia Comunity Policing Act
Data for this dashboard was collected by the Fairfax County Police Department (FCPD) as required by the [Virginia Community Policing Act](https://law.lis.virginia.gov/vacodefull/title52/chapter6.1/). Data is aggregated by the Virginia State Police and is made available on the [Virginia Open Data Portal](https://data.virginia.gov/dataset/community-policing-data). The Virginia Community Policing Act requires law enforcement officers in Virginia to collect data for:
- All investigatory motor vehicle stops
- All stop-and-frisks of a person based on reasonable suspicion
- All other investigatory detentions that do not result in an arrest or the issuance of a summons

Collection of the following data began in July 2020:
- Date of stop
- Race, ethnicity, age, and gender of the person stopped
- Location of the stop
- Reason for the stop: traffic violation, equipment violation, Terry stop (i.e. stop and frisk), check point, or other investigative detenction
- Whether a warning, written citation, or summons was issued or whether any person was arrested
- The most serious violation (if a warning, written citation, or summons was issued or an arrest was made)
- Whether the vehicle or person was searched

Additional data was collected starting in July 2021:
- Whether the person stopped spoke English
- Whether the law-enforcement officer or State Police officer used physical force against any person
- Whether any person used physical force against any officers
- Residency of person stopped (resident of city/county, other VA resident, or out of state resident)
- Whether the person stopped was a driver, passenger or individual

**Note**: Race and ethnicity data are combined in this dashboard in a manner constent with annual reports ([2023 report](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/report-analysis-traffic-stop-data-fiscal-year-2023.pdf): p. 20) of this data by the [Virginia Department of Criminal Justice Services](https://www.dcjs.virginia.gov/criminal-justice-research-center) (DCJS). For combined race/ethnicity categories, the value is Hispanic/Latino if the ethnicity is Hispanic/Latino, and Unknown if the race or ethnicity is unknown. Otherwise, the race is used. This results in categories of Hispanic/Latino of all races, Unknown, and each racial group non-Hispanic/Latino.

More specific details on the data and how it is collected are found [here](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/cpad-appendices/2023/Appendix-H.pdf).

## Population Data
Populations are estimated using the same methodology as DCJS used in the 2023 annual Community Policing Act data report (see [Appendix I](https://www.dcjs.virginia.gov/sites/dcjs.virginia.gov/files/publications/research/cpad-appendices/2023/Appendix-I.pdf)). DCJS uses [Annual County Resident Population Estimates by Age, Sex, Race, and Hispanic Origin](https://www.census.gov/data/tables/time-series/demo/popest/2020s-counties-detail.html) from the U.S. Census. The population estimates used by this dashboard can be found [here](https://github.com/Fairfax-County-NAACP-Data/fcpd-data/blob/main/data/FairfaxCountyPopulation.csv).

## OpenPoliceData
The [OpenPoliceData](https://openpolicedata.readthedocs.io/) Python library is used to download the raw Virginia Community Policing Act data from the [Virginia Open Data Portal](https://data.virginia.gov/stories/s/Virginia-Community-Policing-Act-Data-Collection/rden-cz3h/). OpenPoliceData makes it easy to access and analyze police data and provides centralized access to data from over 3500 police agencies from around the United States.