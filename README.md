
# MPV Analysis Package for HGCAL Tile Modules

A complete analysis package for extracting Most Probable Value (MPV) measurements from HGCAL tile module test beam data. The package uses Landau-Gauss convolution fitting with the Minuit minimizer to extract precise MPV values from ADC amplitude distributions.

## Package Structure

The analysis package is organized as follows:

**Core Analysis Files (root directory):**
- `Minuit_main.py` - Main analysis script
- `Minuit_Analysis.py` - Core fitting algorithms and analysis functions
- `RunManager.py` - Data loading, caching, and preprocessing
- `HistClass.py` - Histogram utilities and data reduction
- `AnalysisConfig.py` - Analysis configuration management  
- `selection_manager.py` - Channel and chip selection logic
- `findCuts.py` - Interactive cut optimization tool

**Supporting Directories:**
- `config/` - Configuration files for runs, datasets, and analysis parameters
- `plotting_visualization/` - Plotting and visualization tools  
- `testing_examples/` - Example scripts and validation tools
- `utilities/` - Data summarization and utility scripts
- `figures/` - Generated plots and analysis figures
- `cache/` - Cached data files for faster loading

## Quick Start Guide

### 1. Prerequisites and Setup
Ensure you have the required Python environment (see Installation section below).

### 2. Configure Data Cuts (Required First Step)
Before running any analysis, you must optimize the data quality cuts:

```bash
python findCuts.py
```

Follow the interactive prompts to:
- Enter your run name
- View data distributions for all detector chips
- Set trigger time and ADC threshold cuts interactively
- Save the optimized cuts for each chip/half combination

**Important:** This step is mandatory and must be completed before running the main analysis.

### 3. Run Main Analysis

```bash
python Minuit_main.py --runs 1 2 3
```

**Command Line Options:**
- `--runs 1 2 3` - Process specific runs (default: run 1 only)
- `--list-runs` - Display available runs and exit  
- `--use-tailcut` - Enable gradient-based tail cutting (default: disabled)

**Available Run Configurations:**
The run numbers correspond to entries in the RUN_MAP dictionary in `Minuit_main.py`:
1. **Run 1**: 150 MeV muon beam data
2. **Run 2**: 250 MeV muon beam data
3. **Run 3**: 250 MeV muon beam data with magnetic field

### 4. View Results
Analysis results are automatically saved in the configured output directory. Use the plotting tools to visualize:

```bash
cd plotting_visualization/
python -c "from plot_utils import plot_from_saved_data; plot_from_saved_data('/path/to/results')"
```

## Core Components

### RunManager  
The central data management system that handles:
- Loading ROOT files from test beam data
- Intelligent caching system for faster repeated access
- Configurable pre-filtering and quality cuts
- Column selection and data type optimization

**Key Features:**
- Automatic detection of cached vs. fresh data loading
- Configurable data paths via `config/runmanager_config.yaml`
- Support for multiple ROOT file formats and directory structures
- Built-in data validation and corruption filtering

### Analysis Pipeline
The complete analysis workflow:

1. **Cut Optimization**: Use `findCuts.py` to set optimal data quality cuts
2. **Data Loading**: RunManager loads and preprocesses test beam data  
3. **Channel Selection**: Configurable selection of detector chips and channels
4. **Histogram Generation**: Create ADC amplitude distributions with optimal binning
5. **Initial Fitting**: Gaussian fit for parameter estimation
6. **Langaus Fitting**: Landau-Gauss convolution fit using Minuit optimizer
7. **Bootstrap Analysis**: Statistical error estimation via resampling
8. **Results Export**: Comprehensive data saved in multiple formats

## Configuration

The package behavior is controlled by configuration files in `config/`:

### `runmanager_config.yaml`
- Data file paths and directory structure
- Caching settings and cache directory location
- File naming patterns and data organization

### `dataset_config.yaml`  
- Dataset-specific parameters for each run
- Trigger time windows and ADC thresholds per chip/half
- Channel mapping and detector geometry information

### Analysis Configuration
The `active_channels` dictionary in `Minuit_main.py` defines:
- Which detector chips to analyze (A5: chip 2, B12: chips 3&4)
- Channel lists for each detector region
- Plotting dimensions and display parameters

**To analyze different detectors:** Modify the `active_channels` and `RUN_MAP` dictionaries in `Minuit_main.py`.

## Analysis Tools and Utilities

### Interactive Cut Optimization
**Critical first step before any analysis:**

```bash
python findCuts.py
```

**Interactive Controls:**
- Hover cursor over plots and press keys to set cuts:
  - `y` - Set lower trigger time cut
  - `x` - Set upper trigger time cut
  - `c` - Set ADC threshold cut  
  - `m` - Save cuts for current chip/half (cursor must be over the plot)
- Close all figures to complete the process

### Data Validation and Testing
```bash
cd testing_examples/
python test_analysis.py --runs 1 --chips 2
```

### Statistical Analysis Tools
```bash
cd comparison_statistics/  
# Compare MPV values between different beam conditions
python Muon_MIP_Comparison_Statistical.py
```

### Results Summarization
```bash
cd utilities/
python summarize_all_results.py  # Creates consolidated CSV tables
```

## Installation and Dependencies

### Python Environment Setup
Requires Python 3.7+ with scientific computing libraries. Anaconda3 is recommended for package management.

```bash
# Create and activate conda environment
conda create --name hgcal_mpv python=3.9
conda activate hgcal_mpv

# Install core scientific packages
conda install numpy pandas matplotlib scipy pyyaml

# Install specialized packages
conda install conda-forge::uproot  # ROOT file I/O
pip install iminuit                 # Minuit minimizer interface
pip install landaupy              # Landau distribution functions
pip install PhyPraKit             # Physics analysis toolkit

# Optional: Install ROOT framework for legacy utilities
conda install root
```

**Required Dependencies:**
- `numpy`, `pandas`, `matplotlib` - Core scientific computing
- `scipy` - Advanced scientific algorithms
- `uproot` - Pure Python ROOT file reading
- `iminuit` - Python interface to Minuit minimizer
- `landaupy` - Landau and Landau-Gauss PDF implementations
- `PhyPraKit` - Physics practical analysis toolkit
- `pyyaml` - Configuration file parsing

Complete dependency specifications are in `config/environment_config.yml`.

## Adapting for New Datasets

### 1. Configure Data Paths
Edit `config/runmanager_config.yaml`:
```yaml
runmanager:
  BASE_PATH: "/path/to/your/data"
  CACHE_PATH: "./cache"
```

### 2. Define Your Runs  
Modify the `RUN_MAP` dictionary in `Minuit_main.py`:
```python
RUN_MAP = {
    1: "your_run_name_1",
    2: "your_run_name_2", 
    # Add as many runs as needed
}
```

### 3. Configure Detector Channels
Update the `active_channels` dictionary in `Minuit_main.py` for your detector configuration:
```python
active_channels = {
    "detector_name": {
        "chip": chip_number,
        "channels": np.array([list_of_channels]),
        "pedestal": pedestal_value,
        "plot_dim": (rows, cols),
    },
}
```

### 4. Set Dataset Parameters
Create entries in `config/dataset_config.yaml` for each run with appropriate trigger windows and thresholds.

### 5. Optimize Cuts
Run `python findCuts.py` for each new dataset to determine optimal quality cuts.

## Output Structure and Results

Analysis results are automatically organized in the output directory specified in `Minuit_main.py`:

```
output_directory/
├── run_name_1/
│   └── analysis_results/
│       ├── complete_results.pkl     # Full analysis data for plotting
│       ├── simplified_results.h5    # Tabular summary (HDF5 format)  
│       └── simplified_results.csv   # Human-readable summary
└── run_name_2/
    └── analysis_results/
        └── ...
```

**File Contents:**
- **complete_results.pkl**: Full analysis data including histograms, fit curves, and bootstrap results
- **simplified_results.h5/csv**: MPV values, uncertainties, fit quality metrics, and summary statistics
- Results can be loaded for further analysis or plotting using tools in `plotting_visualization/`

## Troubleshooting

**Common Issues:**
1. **Missing cuts configuration**: Always run `findCuts.py` before analysis
2. **Path errors**: Check data paths in `config/runmanager_config.yaml`  
3. **Import errors**: Ensure all dependencies are installed in the active environment
4. **ROOT file access**: Verify file permissions and directory structure
5. **Memory issues**: Large datasets may require adjusting cache settings or processing fewer runs simultaneously