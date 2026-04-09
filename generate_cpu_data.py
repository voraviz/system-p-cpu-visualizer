#!/usr/bin/env python3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import os

def is_peak_hour(hour, intervals):
    """Checks if a given hour falls within the defined peak intervals."""
    return any(start <= hour < end for start, end in intervals)

def is_peak_day(current_date, peak_days):
    """Checks if the current day of the month is in the peak days list."""
    return current_date.day in peak_days

def generate_cpu_data(
    lpar_name,
    start_date,
    end_date,
    peak_min_cores=2.0,
    peak_max_cores=8.0,
    offpeak_min_cores=0.5,
    offpeak_max_cores=3.0,
    peak_hour_intervals=[(8, 12), (14, 20)], 
    peak_days=[1, 5, 25, 26, 27, 28, 29, 30, 31],
    peak_day_factor=1.55,
    output_dir="data"
):
    os.makedirs(output_dir, exist_ok=True)
    dates = pd.date_range(start_date, end_date, freq='D')
    time_intervals = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 5)]
    data = []
    
    print(f"Generating data for {lpar_name}...")
    print(f"  [Peak Hours]   Min: {peak_min_cores}, Max: {peak_max_cores}")
    print(f"  [Off-Peak]     Min: {offpeak_min_cores}, Max: {offpeak_max_cores}")
    print(f"  [Peak Days]    Dates: {peak_days} (Multiplier: {peak_day_factor}x)")

    for date in dates:
        cpu_values = []
        day_multiplier = peak_day_factor if is_peak_day(date, peak_days) else 1.0
        
        for hour in range(24):
            for minute in range(0, 60, 5):
                # 1. Determine base range based on hour
                if 0 <= hour < 5:
                    # Off-peak hours (midnight to 5 AM)
                    min_c, max_c = offpeak_min_cores, offpeak_max_cores
                elif is_peak_hour(hour, peak_hour_intervals):
                    # Defined Peak hours
                    min_c, max_c = peak_min_cores, peak_max_cores
                else:
                    # Regular hours (average of peak and off-peak)
                    min_c = (peak_min_cores + offpeak_min_cores) / 2
                    max_c = (peak_max_cores + offpeak_max_cores) / 2
                
                # 2. Generate value and apply peak day multiplier
                cpu_core = np.random.uniform(min_c, max_c) * day_multiplier
                
                # 3. Add noise and ensure it stays above zero
                noise = np.random.normal(0, 0.05)
                cpu_core = max(0.01, cpu_core + noise)
                
                cpu_values.append(round(cpu_core, 2))
        
        row = [date.strftime('%m/%d/%Y')] + cpu_values
        data.append(row)
    
    df = pd.DataFrame(data, columns=['Date'] + time_intervals)
    filepath = os.path.join(output_dir, f"{lpar_name.lower()}.csv")
    df.to_csv(filepath, index=False)
    print(f"✓ Generated: {filepath}\n")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='CPU Data Generator')
    parser.add_argument('--lpar', type=str, help='LPAR name')
    parser.add_argument('--start', type=str, default='2025-01-01')
    parser.add_argument('--end', type=str, default='2025-03-31')
    
    # NEW: Core range arguments
    parser.add_argument('--peak-min', type=float, default=4.0, help='Min cores during peak hours')
    parser.add_argument('--peak-max', type=float, default=12.0, help='Max cores during peak hours')
    parser.add_argument('--offpeak-min', type=float, default=0.5, help='Min cores during off-peak')
    parser.add_argument('--offpeak-max', type=float, default=2.0, help='Max cores during off-peak')
    
    parser.add_argument('--peak-days', type=str, default='1,15,30', help='Specific peak dates')
    parser.add_argument('--peak-day-multiplier', type=float, default=1.55)
    parser.add_argument('--output-dir', type=str, default='data')
    
    args = parser.parse_args()
    peak_days_list = [int(d) for d in args.peak_days.split(',')]
    
    if args.lpar:
        generate_cpu_data(
            lpar_name=args.lpar,
            start_date=args.start,
            end_date=args.end,
            peak_min_cores=args.peak_min,
            peak_max_cores=args.peak_max,
            offpeak_min_cores=args.offpeak_min,
            offpeak_max_cores=args.offpeak_max,
            peak_days=peak_days_list,
            peak_day_factor=args.peak_day_multiplier,
            output_dir=args.output_dir
        )
    else:
        # Default behavior if no LPAR specified
        generate_cpu_data(
            lpar_name="SAMPLE_LPAR",
            start_date=args.start,
            end_date=args.end,
            peak_min_cores=args.peak_min,
            peak_max_cores=args.peak_max,
            offpeak_min_cores=args.offpeak_min,
            offpeak_max_cores=args.offpeak_max,
            peak_days=peak_days_list,
            peak_day_factor=args.peak_day_multiplier,
            output_dir=args.output_dir
        )

if __name__ == "__main__":
    main()