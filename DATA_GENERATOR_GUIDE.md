# Data Generator
- [Data Generator](#data-generator)
- [CPU Utilization Data Generator](#cpu-utilization-data-generator)
  - [🚀 Features](#-features)
  - [📋 Prerequisites](#-prerequisites)
  - [🛠️ Command Line Arguments](#️-command-line-arguments)
  - [💡 Usage Examples](#-usage-examples)
    - [1. High-Performance Database LPAR](#1-high-performance-database-lpar)
    - [2. Standard Web Server](#2-standard-web-server)
    - [3. Testing Standby Logic](#3-testing-standby-logic)
  - [📊 Data Logic Details](#-data-logic-details)
    - [Time of Day](#time-of-day)
    - [Peak Day Multiplier](#peak-day-multiplier)
  - [📁 Output Format](#-output-format)

# CPU Utilization Data Generator

A Python-based utility to generate synthetic CPU utilization data. This tool creates CSV files compatible with the **CPU Utilization Visualizer**, simulating daily workloads, off-peak and peak hour surges, and specific monthly peak-day events.

## 🚀 Features

* **24-Hour Interval Data**: Generates 288 data points per day (5-minute intervals).
* **Dual Peak Windows**: Simulates two distinct daily peak periods (e.g., morning and afternoon).
* **Specific Peak Days**: Apply a utilization multiplier to specific dates of the month (e.g., month-end processing or payroll days).
* **Customizable Core Ranges**: Define separate Minimum and Maximum CPU core consumption for Peak and Off-Peak hours.
* **Automatic Regular Hours**: Automatically calculates "Regular" hour utilization as an average between Peak and Off-Peak ranges.
* **Gaussian Noise**: Adds subtle random variations to the data to mimic real-world system behavior.

---

## 📋 Prerequisites

This script requires Python 3 and the following libraries:
* **Pandas**: For data structuring and CSV export.
* **NumPy**: For random number generation and mathematical scaling.

Install dependencies via pip:
```bash
pip install pandas numpy
```

---

## 🛠️ Command Line Arguments

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--lpar` | String | (Required) | Name of the LPAR (used for the filename). |
| `--start` | YYYY-MM-DD | `2025-01-01` | The start date for data generation. |
| `--end` | YYYY-MM-DD | `2025-03-31` | The end date for data generation. |
| `--peak-min` | Float | `4.0` | Minimum CPU cores during peak hours. |
| `--peak-max` | Float | `12.0` | Maximum CPU cores during peak hours. |
| `--offpeak-min` | Float | `0.5` | Minimum CPU cores during off-peak (00:00-05:00). |
| `--offpeak-max` | Float | `2.0` | Maximum CPU cores during off-peak (00:00-05:00). |
| `--peak-days` | String | `1,15,30` | Comma-separated list of days of the month. |
| `--peak-day-multiplier` | Float | `1.55` | Factor to increase load on peak days (1.55 = +55%). |
| `--interval` | Integer | `5` | Time interval in minutes (5, 10, 15, 30, etc.). |
| `--volatility` | Float | `0.20` | Daily baseline shift (0.2 = 20% variation). |
| `--output-dir` | String | `data` | Directory where CSV files will be saved. |

---

## 💡 Usage Examples

### 1. High-Performance Database LPAR
Generate a full year of data for a database server that runs heavy loads (10–20 cores) during peaks and has significant month-end spikes on the 1st and 30th.
```bash
python generate_cpu_data.py --lpar DB_PROD --start 2025-01-01 --end 2025-12-31 --peak-min 10.0 --peak-max 20.0 --peak-days 1,30
```

### 2. Standard Web Server
Generate 3 months of data for a light web server with standard peak hours and a 20% increase on specific reporting days.
```bash
python generate_cpu_data.py --lpar WEB_SRV --peak-min 2.0 --peak-max 5.0 --peak-days 5,10,15,20,25 --peak-day-multiplier 1.20
```

### 3. Testing Standby Logic
Generate a very low-usage LPAR to test the "Standby" visualization in the dashboard.
```bash
python generate_cpu_data.py --lpar TEST_STANDBY --peak-min 0.1 --peak-max 0.2 --offpeak-min 0.05 --offpeak-max 0.1
```

### 4. Generate Data with 15-Minute Intervals
Generate data with 15-minute intervals instead of the default 5-minute intervals (96 intervals per day).
```bash
python generate_cpu_data.py --lpar LPAR_15MIN --interval 15 --peak-min 4.0 --peak-max 12.0
```

### 5. Generate Data with 30-Minute Intervals
Generate data with 30-minute intervals for systems with less frequent monitoring (48 intervals per day).
```bash
python generate_cpu_data.py --lpar LPAR_30MIN --interval 30 --peak-min 6.0 --peak-max 15.0
```

---

## 📊 Data Logic Details

### Time of Day
* **Off-Peak**: 12:00 AM – 05:00 AM.
* **Peak 1**: 08:00 AM – 12:00 PM (Noon).
* **Peak 2**: 02:00 PM – 08:00 PM.
* **Regular**: All other hours (Calculated as the midpoint between Peak and Off-Peak settings).

### Peak Day Multiplier
If the current date matches a day in your `--peak-days` list, the generated utilization for the *entire day* is multiplied by the `--peak-day-multiplier`. 

**Example Calculation:**
* Base Peak Core: `8.0`
* Peak Day Multiplier: `1.55`
* **Resulting Core:** `12.4`

---

## 📁 Output Format
The script generates a CSV file named `<lpar_name>.csv` in the specified output directory. The structure is:
* **Column 0**: Date (`MM/DD/YYYY`).
* **Columns 1-288**: CPU Core utilization for every 5-minute interval of the day.

This file can be uploaded directly into the **CPU Utilization Visualizer** application.