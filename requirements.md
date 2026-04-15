# CPU Utilization Visualizer
## Overall
- Create single page application that can run locally on laptop with brower
- This app show historical CPU utilization of 2 IBM System P machines name P780#1 and P780#2
- Each machine contains 3 group of LPAR called CPU Pool. Information keep in file name config.ini with following format
```ini
[Machine Name]
<CPU POOL NAME>=<LPAR1>,<LPAR2>,<LPAR3>,...
```
- config.ini parser need to skips comment lines starting with #
- CPU Utilization of each LPAR stored in folder data in CSV format
  - file name is LPAR name in lower characters with extension csv
  - each row is date in format mm/dd/yyyy
  - First column is date
  - Next columns are CPU utilization in core in 5 min interval and last 3 column is max,percentile 90 and percentile 95 
  - If LPAR name specified in config.ini is not found in folder data. this LPAR is standby LPAR then use CPU core with constant value 0.1


## Visualization
### Machine Utilization
- Display stack daily CPU utilization for each machine separately and group by CPU Pool name
- Can choose max, Percentile 90 and Percentile 95
- Can on and off display for each CPU pool
- Y axis is sort from past to present i.e. 4/1/2025 to 31/1/2026 (Format is month/date/year)
- Summary dashboard of machine utilization based on selected max, percentile 90 or percentile 95 with following criteria
    - Min and max of Sum of daily CPU core of all selected pool  selected criteria i.e. max, percentile 90 or percentile 95
### LPAR Utilization
- Select one or multiple LPAR on the same machine with specified date
- Display stacked CPU utilization of selected date in 5 min interval
- Summary dashboard of LPAR utilization with min,max,average,percentile 90 and percentile 95
## Capacity Planning
- Work independently from calculate exeeded capacity in Machine Utilization tab but can use the same calculation method
- Input
  - Use select what statistic metrics to use for capacity planning that is max capacity planning, P95 capacity planning, P90 capacity planning,...,Average capacity planning.
  - %Growth rate and number of years for capacity planning from 1 to 5 years
  - Button for start calculation
- Calculation method
  - Use input data as 1st year
  - Reference sizing is calculate from user input for example 5% growth with 5 years and P90 capacity planning is 50 cores then use 50*1.05*1.05*1.05*1.05 = 78.125 cores then round up to 79 cores as reference sizing
  - Use % growth rate to calculate actual peak for each year, i.e. for 5% growth rate, 2nd year peak is 1.05 * 1st year peak and so on
  - Compare reference sizing with actual peak with %growth rate and calculate from 1st year to 5th year that sizing is enough or not along show % available
- Output in table format with 2 table on compare reference sizing with max of sums and sum of max.
add additional 2 columns to 1st  table output that calculated from actual peak
- minutes/year
- cores/year
This two column contains value only if status is "Not enough"
- minutes/year  is total minutes exceed reference sizing
- core/year is total core exceed reference sizing
Both number calculate from interpolation of the same calculation method used by Machine Utilization tab
i.e. if exceed core is 10 cores and data is from 300 days then 1 year  = 360/300*10 = 12 cores