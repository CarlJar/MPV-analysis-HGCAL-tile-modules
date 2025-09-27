# MPV Analysis Package - Structure Summary

## Package Transformation Complete

The project has been successfully transformed from a thesis-specific analysis into a reusable, configurable analysis package for HGCAL tile module MPV measurements.

## Current Structure

### Core Analysis Files (Root Directory)
```
Minuit_main.py          # Main analysis script with configurable RUN_MAP
Minuit_Analysis.py      # Core fitting algorithms and bootstrap analysis  
RunManager.py           # Data loading, caching, and preprocessing
HistClass.py           # Histogram utilities and data reduction
AnalysisConfig.py      # Analysis configuration management
selection_manager.py   # Channel and chip selection logic
findCuts.py           # Interactive cut optimization tool (MUST run first)
```

### Supporting Directories
```
config/                 # Configuration files (paths, datasets, analysis params)
plotting_visualization/ # Plotting tools and visualization utilities
testing_examples/      # Validation scripts and usage examples
utilities/             # Data summarization and utility scripts
figures/              # Generated plots and analysis figures  
cache/                # Cached data files for performance
comparison_statistics/ # Statistical comparison tools
```

## Key Configuration Points

### 1. Data Paths
- Configure in `config/runmanager_config.yaml`
- Set BASE_PATH to your data directory

### 2. Run Definitions  
- Modify RUN_MAP dictionary in `Minuit_main.py`
- Add your run identifiers and corresponding directory names

### 3. Detector Configuration
- Update active_channels dictionary in `Minuit_main.py`  
- Define chip numbers, channel lists, and detector regions

### 4. Analysis Parameters
- Dataset-specific cuts in `config/dataset_config.yaml`
- Analysis behavior controlled via command-line flags

## Critical Workflow

1. **Configure paths and runs** (edit config files and Minuit_main.py)
2. **Optimize cuts** (run `python findCuts.py` - REQUIRED)
3. **Run analysis** (run `python Minuit_main.py --runs 1 2 3`)  
4. **Visualize results** (use tools in plotting_visualization/)

## Package Features

- **Fully configurable**: No hardcoded paths or run names
- **Interactive cut optimization**: Visual, interactive quality cut setting
- **Intelligent caching**: Automatic detection of cached vs. fresh data
- **Comprehensive output**: Multiple result formats for different use cases
- **Modular design**: Easy to extend with new analysis methods
- **Professional structure**: Clean separation of concerns

The package is now ready for production use with any HGCAL tile module dataset!
