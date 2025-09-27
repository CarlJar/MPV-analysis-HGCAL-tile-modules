
# MPV Analysis for HGCAL Tile Modules

This repository contains analysis tools for Most Probable Value (MPV) analysis of HGCAL tile modules using muon test beam data. The analysis uses Landau-Gauss convolution fitting to extract MPV values from ADC distributions.

## Project Structure

The codebase is organized into focused directories based on functionality:

- **`core_analysis/`** - Essential files for the main Minuit analysis pipeline
- **`plotting_visualization/`** - Plotting and visualization tools
- **`comparison_statistics/`** - Statistical comparison tools for different runs
- **`thesis_figures/`** - Scripts for generating publication-quality figures
- **`occupancy_studies/`** - Detector occupancy analysis tools
- **`alternative_analysis/`** - Alternative fitting methods and approaches
- **`testing_examples/`** - Testing scripts and examples
- **`utilities/`** - General utility scripts and tools
- **`config/`** - Configuration files
- **`cache/`** - Cached data files

See [FOLDER_ORGANIZATION.md](FOLDER_ORGANIZATION.md) for detailed documentation of each directory.

## Quick Start

### Running the Main Analysis

Navigate to the core analysis directory and run the main analysis script:

```bash
cd core_analysis/
python Minuit_main.py --runs 1 2 3
```

Available command line options:
- `--runs 1 2 3` - Process specific runs (default: run 1 only)
- `--list-runs` - Display available runs and exit
- `--use-tailcut` - Enable tail cutting in the analysis (default: disabled)

### Available Datasets
The analysis supports three muon beam datasets:
1. **Run 1**: 150 MeV muons
2. **Run 2**: 250 MeV muons  
3. **Run 3**: 250 MeV muons with magnetic field

## Core Analysis Components

### RunManager
Located in `core_analysis/RunManager.py`, this component handles:
- Loading ROOT files from test beam data
- Data caching for faster subsequent access
- Pre-filtering and quality cuts
- Column selection and data formatting

Key features:
- Automatic caching system to avoid reloading large datasets
- Configurable pre-cuts for data quality
- Support for multiple file formats and structures

### Analysis Pipeline
The main analysis workflow consists of:
1. **Data Loading**: RunManager loads and caches test beam data
2. **Channel Selection**: Select specific chips and channels for analysis
3. **Histogram Creation**: Generate ADC amplitude distributions
4. **Gaussian Fitting**: Initial parameter estimation
5. **Langaus Fitting**: Landau-Gauss convolution fit using Minuit
6. **Bootstrap Analysis**: Error estimation via bootstrap resampling
7. **Results Storage**: Save comprehensive results for later analysis

## Analysis Tools

### Cut Optimization (utilities/findCuts.py)
Interactive tool for optimizing data quality cuts:

```bash
cd utilities/
python findCuts.py
```

Usage:
1. Enter the run name when prompted
2. View plots for all chip/half combinations
3. Set cuts interactively:
   - Press 'y' for lower trigger time cut
   - Press 'x' for upper trigger time cut  
   - Press 'c' for ADC threshold cut
   - Press 'm' to save cuts for current chip/half
4. Close figures to finish

### Visualization Tools
Located in `plotting_visualization/`, these tools create plots from saved analysis results:

```bash
cd plotting_visualization/
python -c "from plot_utils import plot_from_saved_data; plot_from_saved_data('/path/to/results')"
```

### Statistical Comparisons
Compare MPV values across different beam conditions:

```bash
cd comparison_statistics/
python Muon_MIP_Comparison_Statistical.py
```

## Installation and Setup

### Python Environment Setup
The analysis requires Python 3.7+ with scientific computing libraries. We recommend using Anaconda3.

#### Installing Anaconda3
1. Download Anaconda3 installer from https://www.anaconda.com/download/
2. Install Anaconda3:
```bash
cd ~/Downloads
chmod +x Anaconda3-2024.06-1-Linux-x86_64.sh
./Anaconda3-2024.06-1-Linux-x86_64.sh
```

#### Creating Analysis Environment
```bash
# Create and activate a new conda environment
conda create --name hgcal_analysis python=3.9
conda activate hgcal_analysis

# Install required packages
conda install numpy pandas matplotlib pyyaml
conda install conda-forge::uproot
conda install root  # ROOT framework and PyROOT
```

#### Required Dependencies
Core dependencies:
- **numpy** - Numerical computations
- **pandas** - Data manipulation and analysis
- **matplotlib** - Plotting and visualization
- **uproot** - ROOT file I/O in pure Python
- **scipy** - Scientific computing algorithms
- **iminuit** - Python interface to Minuit minimizer
- **landaupy** - Landau and Landau-Gauss distributions
- **PhyPraKit** - Physics practical toolkit

Optional dependencies:
- **root** - Full ROOT framework (for legacy utilities)
- **pyyaml** - Configuration file parsing

Complete dependency information is available in `config/environment_config.yml`.

## Configuration

The analysis behavior is controlled by configuration files in the `config/` directory:
- `runmanager_config.yaml` - Data paths and caching settings
- `dataset_config.yaml` - Dataset-specific parameters and cuts
- `analysis_config.yaml` - Analysis parameters and fit settings

Modify these files to adapt the analysis to your data location and requirements.

## Output Structure

Analysis results are saved in structured format:
```
output_directory/
├── run_name/
│   └── analysis_results/
│       ├── complete_results.pkl     # Full analysis data
│       ├── simplified_results.h5    # Summary statistics
│       └── simplified_results.csv   # Human-readable summary
```

The complete results contain all fitting data for later plotting and analysis. The simplified results provide MPV values, errors, and fit quality metrics in tabular format.