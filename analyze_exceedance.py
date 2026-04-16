import csv
import sys
import configparser
from collections import defaultdict

# Check if config file is provided
if len(sys.argv) < 2:
    print("Usage: python3 analyze_exceedance.py <config_file.ini>")
    print("Example: python3 analyze_exceedance.py analyzer-internal.ini")
    sys.exit(1)

config_file = sys.argv[1]

# Read configuration with inline comment support
config = configparser.ConfigParser(inline_comment_prefixes=('#',))
try:
    config.read(config_file)
except Exception as e:
    print(f"Error reading config file '{config_file}': {e}")
    sys.exit(1)

# Get main configuration parameters
try:
    STANDBY = float(config['MAIN'].get('STANDBY', '0.1'))
    INTERVAL = int(config['MAIN'].get('INTERVAL', '5'))
    DATA_DIR = config['MAIN'].get('DATA_DIR', 'data-internal')
    PERCENT_GROWTH = float(config['MAIN'].get('PERCENT_GROWTH', '5'))
    NUM_OF_YEAR = int(config['MAIN'].get('NUM_OF_YEAR', '5'))
    REFERENCE_CORE = float(config['MAIN'].get('REFERENCE_CORE', '47'))
except Exception as e:
    print(f"Error parsing MAIN section in config: {e}")
    sys.exit(1)

# Get LPARs from config
lpars = {}
missing_lpars = []

for section in config.sections():
    if section != 'MAIN':
        lpars[section] = []
        for pool in config[section]:
            lpar_list = [l.strip() for l in config[section][pool].split(',')]
            lpars[section].extend(lpar_list)

if not lpars:
    print("Error: No machine sections found in config file")
    sys.exit(1)

print(f"Configuration loaded from: {config_file}")
print(f"  Data directory: {DATA_DIR}")
print(f"  Standby value: {STANDBY} cores")
print(f"  Interval: {INTERVAL} minutes")
print(f"  Growth rate: {PERCENT_GROWTH}%")
print(f"  Number of years: {NUM_OF_YEAR}")
print(f"  Reference sizing: {REFERENCE_CORE} cores")
print()

# Read all LPAR data
lpar_data = {}
for machine, lpar_list in lpars.items():
    print(f"Loading LPARs for {machine}:")
    for lpar in lpar_list:
        filename = f'{DATA_DIR}/{lpar.lower()}.csv'
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Skip header
                lpar_data[lpar] = {}
                for row in reader:
                    date = row[0]
                    # Calculate number of intervals based on INTERVAL setting
                    intervals_per_day = (24 * 60) // INTERVAL
                    # Read interval values (exclude last 3 columns: Max, P90, P95)
                    values = [float(row[i]) if i < len(row) and row[i] else 0.0 
                             for i in range(1, min(intervals_per_day + 1, len(row) - 3))]
                    # Pad with zeros if needed
                    while len(values) < intervals_per_day:
                        values.append(0.0)
                    lpar_data[lpar][date] = values
            print(f"  ✓ {lpar}: {len(lpar_data[lpar])} dates")
        except FileNotFoundError:
            print(f"  ⚠ {lpar}: File not found - treating as standby LPAR ({STANDBY} cores)")
            missing_lpars.append(lpar)

print()

# Get all dates
all_dates = set()
for lpar in lpar_data.values():
    all_dates.update(lpar.keys())
all_dates = sorted(list(all_dates))

print(f"Analysis Summary:")
print(f"  Total dates: {len(all_dates)}")
print(f"  LPARs with data: {len(lpar_data)}")
print(f"  Standby LPARs: {len(missing_lpars)}")

# Calculate annualization factor
# - If less than 1 year (< 360 days): scale up to 360 days
# - If 1 year or more (>= 360 days): no adjustment needed (factor = 1.0)
if len(all_dates) >= 360:
    annualization_factor = 1.0
    print(f"  Annualization factor: {annualization_factor:.4f} (full year or more - no adjustment needed)")
else:
    annualization_factor = 360 / len(all_dates)
    print(f"  Annualization factor: {annualization_factor:.4f} (scaling up {len(all_dates)} days to 360 days)")
print()

# Calculate intervals per day
intervals_per_day = (24 * 60) // INTERVAL

# Find exceedances for each year
print("=" * 80)
print("CAPACITY PLANNING RESULTS (Year by Year)")
print("=" * 80)
print()

growth_rate = PERCENT_GROWTH / 100
yearly_exceedances = {}

for year in range(1, NUM_OF_YEAR + 1):
    growth_multiplier_year = (1 + growth_rate) ** (year - 1)
    
    exceedances = []
    total_excess_cores = 0
    
    for date in all_dates:
        # Get intervals for this date
        for interval_idx in range(intervals_per_day):
            # Calculate per-LPAR contributions
            lpar_contributions = {}
            total = 0
            
            # Add data from available LPARs
            for lpar_name, dates_data in lpar_data.items():
                if date in dates_data and interval_idx < len(dates_data[date]):
                    value = dates_data[date][interval_idx]
                    lpar_contributions[lpar_name] = value
                    total += value
            
            # Add standby LPARs
            for missing_lpar in missing_lpars:
                lpar_contributions[missing_lpar] = STANDBY
            total += len(missing_lpars) * STANDBY
            
            # Apply growth
            projected = total * growth_multiplier_year
            
            if projected > REFERENCE_CORE:
                hour = (interval_idx * INTERVAL) // 60
                minute = (interval_idx * INTERVAL) % 60
                time_str = f"{hour:02d}:{minute:02d}"
                excess = projected - REFERENCE_CORE
                total_excess_cores += excess
                
                # Store exceedance with LPAR details
                exceedances.append({
                    'date': date,
                    'time': time_str,
                    'interval': interval_idx,
                    'actual': total,
                    'projected': projected,
                    'excess': excess,
                    'lpar_contributions': lpar_contributions,
                    'growth_multiplier': growth_multiplier_year
                })
    
    yearly_exceedances[year] = exceedances
    
    raw_minutes = len(exceedances) * INTERVAL
    annualized_minutes = raw_minutes * annualization_factor
    annualized_cores = total_excess_cores * annualization_factor
    
    print(f"Year {year} (Growth: {(growth_multiplier_year - 1) * 100:.1f}%, Multiplier: {growth_multiplier_year:.4f})")
    print(f"  Raw (from {len(all_dates)} sampled days):")
    print(f"    Exceeded minutes: {raw_minutes}")
    print(f"    Exceeded cores:   {total_excess_cores:.2f}")
    print(f"  Annualized (projected to 1 year):")
    print(f"    Exceeded minutes: {annualized_minutes:.0f}")
    print(f"    Exceeded cores:   {annualized_cores:.2f}")
    print()

print("=" * 80)

# Write CSV files for each year
for year in range(1, NUM_OF_YEAR + 1):
    exceedances = yearly_exceedances[year]
    filename = f'exceedances_year{year}.csv'
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['machine', 'lpar', 'date', 'time', 'reference_core', 'actual_core', 'exceed_core'])
        
        for exc in exceedances:
            # Write one row per exceedance interval showing the total excess
            # Use machine name from lpars dict
            machine_name = list(lpars.keys())[0] if lpars else 'UNKNOWN'
            writer.writerow([
                machine_name,
                'ALL_LPARS',
                exc['date'],
                exc['time'],
                f"{REFERENCE_CORE:.4f}",
                f"{exc['projected']:.4f}",
                f"{exc['excess']:.4f}"
            ])
    
    print(f"Created {filename} with {len(exceedances)} exceedance intervals")

print()

# Made with Bob
