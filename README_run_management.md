# Run Management for Minuit Analysis and Plotting

This document explains the enhancements made to the analysis and plotting workflow for muon data processing.

## Overview

The analysis scripts have been updated to use command-line arguments for selecting which runs to process, making it easier to analyze and plot data from multiple runs without modifying the source code.

## Available Runs

The following runs are available:

1. **Run 1**: 2024-09-16_22-34-48_beamrun_muonss_150 (150 MeV muons)
2. **Run 2**: 2024-09-19_15-11-45_beamrun_muon_250 (250 MeV muons)
3. **Run 3**: 2024-09-21_12-29-11_beamrun_muon_250_magnetOn (250 MeV muons with magnet on)

## Analysis with Minuit_main.py

The `Minuit_main.py` script has been updated to allow selecting which runs to analyze via command-line arguments.

### Usage

```bash
# List available runs
python Minuit_main.py --list-runs

# Run analysis on a single run (default is run 1)
python Minuit_main.py

# Run analysis on specific runs
python Minuit_main.py --runs 2 3

# Run analysis on all runs
python Minuit_main.py --runs 1 2 3
```

### Parameters

- `--runs`: Specify one or more run numbers to process. Default is `[1]`.
- `--list-runs`: Show the available runs and exit.

## Plotting with test_analysis.py

The `test_analysis.py` script has been updated to allow selecting which runs and chips to plot via command-line arguments.

### Usage

```bash
# List available runs
python test_analysis.py --list-runs

# Generate plots for a single run (default is run 1) with default settings
python test_analysis.py

# Generate plots for specific runs
python test_analysis.py --runs 2 3

# Generate plots for specific chips
python test_analysis.py --runs 1 --chips 2 4

# Generate only standard plots
python test_analysis.py --plot-type standard

# Generate plots showing only the fit region
python test_analysis.py --fit-region-only

# Combine multiple options
python test_analysis.py --runs 2 3 --chips 3 --plot-type comparison --fit-region-only
```

### Parameters

- `--runs`: Specify one or more run numbers to plot. Default is `[1]`.
- `--chips`: Specify one or more chip numbers to plot. Default is `[2, 3, 4]`.
- `--plot-type`: Type of plot to generate. Options are `standard`, `comparison`, or `both` (default).
- `--fit-region-only`: Show only the fit region in plots. Default is to show all data.
- `--list-runs`: Show the available runs and exit.

## Examples

### Example 1: Analyze all runs

```bash
python Minuit_main.py --runs 1 2 3
```

This will process all three runs sequentially, generating analysis results for each.

### Example 2: Plot specific chips for a specific run

```bash
python test_analysis.py --runs 3 --chips 2 4
```

This will generate both standard and comparison plots for chips 2 and 4 from run 3 (250 MeV with magnet on).

### Example 3: Generate only comparison plots

```bash
python test_analysis.py --runs 1 2 --plot-type comparison
```

This will generate only comparison plots for all chips in runs 1 and 2.

## Technical Details

### Run Mapping

The runs are mapped from numbers to their full names using a dictionary:

```python
RUN_MAP = {
    1: "2024-09-16_22-34-48_beamrun_muonss_150",
    2: "2024-09-19_15-11-45_beamrun_muon_250",
    3: "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}
```

This allows referencing runs by their number rather than typing out the full name.

### Output Structure

Analysis results are saved to:

```
/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/<run_name>/analysis_results/
```

Where `<run_name>` is the full name of the run from the RUN_MAP.
