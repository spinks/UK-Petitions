# Visualisation of Petition and EU Referendum Data

This folder contains data and code behind the "[Signatures by Constituency](https://public.tableau.com/views/SignaturesbyConstituency4th/DashboardFixedSize?:embed=y&:display_count=yes)" tableau visualisation.

## gather.py

This script will aggregate and format all the data required from the various
sources (listed below,) it can take a while to run due to rate limiting when
downloading the petition data.

## write_up.pdf

This writeup outlines:
1. Links to versions of the visualisation
2. Summary of visualisation and story
3. Design choices
4. Feedback
5. Sources

## Sources
### Petition Data
- Petition Data is gathered from petition.parliament.uk
- Working on archived published petitions from 2015-2017 (10905 petitions), a list of these is available at: [petition.parliament.uk](https://petition.parliament.uk/archived/petitions?parliament=1&state=published)

### Population Data
- 2016 mid year population estimates by parliamentary constituency available at: [House of Commons Tableau Profile](https://public.tableau.com/profile/house.of.commons.library.statistics/#!/vizhome/Populationbyage_0/Dataconstituencyincontext)

### Map Data
- Shape files for constituencies is available at: [data.gov.uk](https://data.gov.uk/dataset/westminster-parliamentary-constituencies-december-2016-super-generalised-clipped-boundaries-in-4)
- Data for hex map of constituencies is available at: [thedataschool.co.uk](https://www.thedataschool.co.uk/rob-suddaby/getting-creative-building-visualisations-from-web-content/)

### EU Referendum Data
- Estimates for votes by constituency available at: [House of Commons Library Parliament and Elections](https://commonslibrary.parliament.uk/parliament-and-elections/elections-elections/brexit-votes-by-constituency/)
