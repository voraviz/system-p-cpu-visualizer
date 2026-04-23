# How to Calculate CPU Exceedances

This document explains the step-by-step calculation methodology used by both the Python script and the visualizer.

## Configuration Parameters

From `analyzer-sample.ini`:
```ini
REFERENCE_CORE = 38.46          # Base year (Year 1) capacity in cores
CAPACITY_PLANNING_YEARS = 3     # Number of years for capacity planning
CPU_UTILIZATION_YEARS = 5       # Number of years to project CPU utilization
BASE_PLANNING_GROWTH = 5        # Annual growth rate for capacity planning (%)
CPU_UTILIZATION_GROWTH = 5      # Annual growth rate for CPU utilization (%)
ANNUALIZATION_DAYS = 365        # Days in a full year for annualization
```

## Step 1: Calculate Reference Sizing

Reference sizing represents the target capacity for Year N (where N = CAPACITY_PLANNING_YEARS).

### Formula:
```
Reference Sizing = CEILING(REFERENCE_CORE × (1 + growth_rate)^(years - 1))
```

### Example Calculation:
```
REFERENCE_CORE = 38.46 cores
CAPACITY_PLANNING_YEARS = 3
BASE_PLANNING_GROWTH = 5% = 0.05

Reference Sizing = CEILING(38.46 × (1.05)^(3-1))
                 = CEILING(38.46 × (1.05)^2)
                 = CEILING(38.46 × 1.1025)
                 = CEILING(42.40215)
                 = 43 cores
```

**Result:** The target capacity for Year 3 is **43 cores**.

## Step 2: Calculate Growth Multipliers for Each Year

For each projection year, calculate how much the CPU usage will grow.

### Formula:
```
Growth Multiplier (Year N) = (1 + growth_rate)^(N - 1)
```

### Example Calculations:
```
CPU_UTILIZATION_GROWTH = 5% = 0.05

Year 1: (1.05)^(1-1) = (1.05)^0 = 1.0000      (0% growth - baseline)
Year 2: (1.05)^(2-1) = (1.05)^1 = 1.0500      (5% growth)
Year 3: (1.05)^(3-1) = (1.05)^2 = 1.1025      (10.25% growth)
Year 4: (1.05)^(4-1) = (1.05)^3 = 1.1576      (15.76% growth)
Year 5: (1.05)^(5-1) = (1.05)^4 = 1.2155      (21.55% growth)
```

## Step 3: Load and Process LPAR Data

For each LPAR (Logical Partition):
1. Read CPU usage data from CSV files (5-minute intervals)
2. For missing LPARs, use standby value (0.1 cores)
3. Sum all LPAR usage for each time interval

### Example:
```
Date: 10/1/2025, Time: 12:00

LPAR Usage:
- LPAR1: 8.5 cores
- LPAR2: 7.2 cores
- LPAR3: 6.8 cores
- LPAR4: 5.3 cores
- LPAR5: 4.2 cores
- LPAR6: 4.5 cores
- Standby LPARs (5 × 0.1): 0.5 cores

Total actual usage = 8.5 + 7.2 + 6.8 + 5.3 + 4.2 + 4.5 + 0.5 = 37.0 cores
```

## Step 4: Project Usage and Count Exceedances

For each time interval in the data:

### Formula:
```
Projected Usage = Actual Usage × Growth Multiplier

If Projected Usage > Reference Sizing:
    - Count as exceedance
    - Record excess cores = Projected Usage - Reference Sizing
```

### Example for Year 5:
```
Interval: 10/1/2025 12:00
Actual usage: 37.0 cores
Growth multiplier (Year 5): 1.2155
Reference sizing: 43 cores

Projected usage = 37.0 × 1.2155 = 44.97 cores

Since 44.97 > 43:
    ✓ This is an exceedance
    Excess cores = 44.97 - 43 = 1.97 cores
    Exceeded time = 5 minutes (one interval)
```

## Step 5: Sum Raw Exceedances

Count all exceedances across all dates in the sample data.

### Example Results (Year 5):
```
Sample period: 306 days
Total exceedance intervals: 659
Total exceeded minutes: 659 × 5 = 3,295 minutes
Total excess cores: 1,286.81 cores
```

## Step 6: Annualize Results

Scale the results from the sample period to a full year.

### Formula:
```
Annualization Factor = ANNUALIZATION_DAYS / Sample Days

Annualized Minutes = Raw Minutes × Annualization Factor
Annualized Cores = Raw Cores × Annualization Factor
```

### Example Calculation:
```
Sample days: 306
Annualization days: 365
Annualization factor = 365 / 306 = 1.1928

Raw results:
- Exceeded minutes: 3,295
- Excess cores: 1,286.81

Annualized results:
- Exceeded minutes = 3,295 × 1.1928 = 3,930 minutes
- Excess cores = 1,286.81 × 1.1928 = 1,535 cores
```

## Complete Example: Year 5 Calculation

### Input:
- Reference sizing: 43 cores
- Growth multiplier: 1.2155
- Sample data: 306 days
- Annualization: 365 days

### Process:
1. For each of 306 days × 288 intervals/day = 88,128 intervals:
   - Sum all LPAR usage
   - Multiply by 1.2155
   - Check if result > 43 cores
   
2. Count exceedances:
   - Found: 659 intervals exceed threshold
   - Minutes: 659 × 5 = 3,295 minutes
   - Excess: 1,286.81 cores

3. Annualize:
   - Factor: 365/306 = 1.1928
   - Minutes: 3,295 × 1.1928 = 3,930 minutes
   - Cores: 1,286.81 × 1.1928 = 1,535 cores

### Output:
```
Year 5 Exceedances:
- Exceeded minutes per year: 3,930
- Excess cores per year: 1,535
```

## Summary of Key Formulas

1. **Reference Sizing:**
   ```
   CEILING(REFERENCE_CORE × 1.05^(CAPACITY_PLANNING_YEARS - 1))
   ```

2. **Growth Multiplier:**
   ```
   1.05^(Year - 1)
   ```

3. **Projected Usage:**
   ```
   Actual Usage × Growth Multiplier
   ```

4. **Exceedance Check:**
   ```
   IF Projected Usage > Reference Sizing THEN count as exceedance
   ```

5. **Annualization:**
   ```
   Annualized Value = Raw Value × (365 / Sample Days)
   ```

## Notes

- All calculations use standard IEEE 754 floating-point arithmetic
- CEILING function rounds up to nearest integer
- Growth rates are compounded annually
- Exceedances are counted at 5-minute interval granularity
- Annualization assumes uniform distribution across the year