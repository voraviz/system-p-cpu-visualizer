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
    peak_min_cores=4.0,
    peak_max_cores=12.0,
    offpeak_min_cores=0.5,
    offpeak_max_cores=2.0,
    peak_hour_intervals=[(8, 12), (14, 20)], # 8AM-12PM and 2PM-8PM
    peak_days=[1, 2, 3, 4, 5, 25, 26, 27, 28, 29, 30, 31], # 1-5 and 25-End
    peak_day_factor=1.55,  # 55% increase
    daily_volatility=0.20, # 20% random shift per day
    interval_minutes=5,    # Time interval in minutes
    output_dir="data"
):
    os.makedirs(output_dir, exist_ok=True)
    dates = pd.date_range(start_date, end_date, freq='D')
    
    # Generate time intervals based on interval_minutes
    time_intervals = []
    for h in range(24):
        for m in range(0, 60, interval_minutes):
            time_intervals.append(f"{h:02d}:{m:02d}")
    
    data = []
    
    print(f"Generating Master Data for {lpar_name}...")
    print(f"  [Config] Peak: {peak_min_cores}-{peak_max_cores} | Off: {offpeak_min_cores}-{offpeak_max_cores}")
    print(f"  [Config] Peak Days: {peak_days}")
    print(f"  [Config] Interval: {interval_minutes} minutes ({len(time_intervals)} intervals/day)")

    for date in dates:
        cpu_values = []
        
        # 1. Daily Volatility: Shift the baseline for this specific day
        day_shift = np.random.uniform(1 - daily_volatility, 1 + daily_volatility)
        
        # 2. Peak Day Multiplier
        is_p_day = is_peak_day(date, peak_days)
        day_multiplier = peak_day_factor if is_p_day else 1.0
        
        # Final combined scaling factor for the day
        total_scale = day_shift * day_multiplier

        for hour in range(24):
            for minute in range(0, 60, interval_minutes):
                # 3. Determine Base Range
                if 0 <= hour < 5:
                    min_c, max_c = offpeak_min_cores, offpeak_max_cores
                elif is_peak_hour(hour, peak_hour_intervals):
                    min_c, max_c = peak_min_cores, peak_max_cores
                else:
                    # Regular hours (average of peak and off-peak)
                    min_c = (peak_min_cores + offpeak_min_cores) / 2
                    max_c = (peak_max_cores + offpeak_max_cores) / 2
                
                # 4. Generate Core Value
                cpu_core = np.random.uniform(min_c, max_c) * total_scale
                
                # 5. Add Random Spikes (0.5% chance)
                if np.random.random() < 0.005:
                    cpu_core += np.random.uniform(2.0, 5.0)

                # 6. Add Minute Jitter (Gaussian Noise)
                noise = np.random.normal(0, 0.1)
                cpu_core = max(0.01, cpu_core + noise)
                
                cpu_values.append(round(cpu_core, 2))
        
        row = [date.strftime('%m/%d/%Y')] + cpu_values
        data.append(row)
    
    df = pd.DataFrame(data, columns=['Date'] + time_intervals)
    filepath = os.path.join(output_dir, f"{lpar_name.lower()}.csv")
    df.to_csv(filepath, index=False)
    print(f"✓ Generated: {filepath} ({len(time_intervals)} intervals | Shift: {day_shift:.2f}x | Peak Day: {is_p_day})")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Master CPU Utilization Data Generator')
    parser.add_argument('--lpar', type=str, required=True, help='LPAR name')
    parser.add_argument('--start', type=str, default='2025-01-01')
    parser.add_argument('--end', type=str, default='2025-03-31')
    
    # Range Parameters
    parser.add_argument('--peak-min', type=float, default=4.0)
    parser.add_argument('--peak-max', type=float, default=12.0)
    parser.add_argument('--offpeak-min', type=float, default=0.5)
    parser.add_argument('--offpeak-max', type=float, default=2.0)
    
    # Peak Day Parameters (Date-only list)
    parser.add_argument('--peak-days', type=str, default='1,2,3,4,5,25,26,27,28,29,30,31', 
                        help='Specific days of month as peak days')
    parser.add_argument('--peak-day-multiplier', type=float, default=1.55)
    
    # Variation Parameter
    parser.add_argument('--volatility', type=float, default=0.20, help='Daily baseline shift (e.g., 0.2 for 20%)')
    
    # Interval Parameter
    parser.add_argument('--interval', type=int, default=5, help='Time interval in minutes (5, 10, 15, 30, etc.)')
    
    args = parser.parse_args()
    peak_days_list = [int(d) for d in args.peak_days.split(',')]
    
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
        daily_volatility=args.volatility,
        interval_minutes=args.interval
    )

if __name__ == "__main__":
    main()