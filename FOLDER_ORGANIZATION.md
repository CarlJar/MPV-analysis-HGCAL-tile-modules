# Folder Organization Guide

This document describes the reorganized folder structure of the MPV-analysis-HGCAL-tile-modules project. Files have been organized based on their functionality and relationship to the core Minuit analysis routine.

## Folder Structure

### 📁 `core_analysis/` - **Essential Files for Minuit Analysis**
**Purpose**: Contains all files that are directly used by the main Minuit analysis pipeline.

Files:
- `Minuit_main.py` - Main analysis script (entry point)
- `Minuit_Analysis.py` - Core fitting and analysis functions
- `RunManager.py` - Data loading and run management
- `AnalysisConfig.py` - Analysis configuration
- `HistClass.py` - Histogram utilities
- `selection_manager.py` - Channel/chip selection logic

**Usage**: Run the main analysis from this folder:
```bash
cd core_analysis/
python Minuit_main.py --runs 1 2 3
```

### 📁 `plotting_visualization/` - **Plotting and Visualization Tools**
**Purpose**: All files related to creating plots and visualizations of analysis results.

Files:
- `plot_utils.py` - Main plotting utilities with AnalysisPlotter class
- `enhanced_plotter.py` - Enhanced plotting with ThesisPlotter class
- `PlotUtils.py` - Legacy plotting utilities
- `PlotSTCCorrelations_BX.py` - Correlation plotting
- `thesis_plotting_config.py` - Configuration for thesis-style plots

**Usage**: For plotting results after running the analysis:
```bash
cd plotting_visualization/
python -c "from plot_utils import plot_from_saved_data; plot_from_saved_data('path/to/results')"
```

### 📁 `alternative_analysis/` - **Alternative Analysis Methods**
**Purpose**: Alternative fitting implementations and analysis approaches.

Files:
- `LangausClass3.py` - Alternative Langaus fitting class with Minuit backend
- `utils.py` - ROOT-based plotting utilities and legacy functions

**Usage**: For testing different analysis approaches or comparing methods.

### 📁 `occupancy_studies/` - **Occupancy Analysis**
**Purpose**: Scripts for analyzing detector occupancy patterns.

Files:
- `occupancy.py` - General occupancy analysis
- `occupancy_A5.py` - Occupancy analysis specific to A5 chip
- `occupancy_B12.py` - Occupancy analysis specific to B12 chip

**Usage**: For studying detector response patterns and occupancy distributions.

### 📁 `comparison_statistics/` - **Statistical Comparisons**
**Purpose**: Tools for comparing MIP values across different runs and conditions.

Files:
- `Muon_MIP_Comparison.py` - MIP comparison analysis
- `Muon_MIP_Comparison_Statistical.py` - Statistical MIP comparisons
- `mip_comparison_statistical.py` - Statistical comparison utilities

**Usage**: For comparing results between different beam energies, magnetic field conditions, etc.

### 📁 `testing_examples/` - **Testing and Examples**
**Purpose**: Scripts for testing functionality and demonstrating analysis procedures.

Files:
- `test_analysis.py` - Testing script for analysis results
- `test_error_bars.py` - Error bar analysis testing
- `example_fit_procedure.py` - Example fitting demonstrations
- `function_comparison.py` - Function comparison utilities
- `errorbar_analysis.py` - Error analysis examples

**Usage**: For validation, debugging, and learning how the analysis works.

### 📁 `thesis_figures/` - **Thesis Figure Generation**
**Purpose**: Scripts and resources for generating thesis/publication figures.

Files:
- `thesis_plots.py` - Thesis-specific plotting scripts
- `create_thesis_plots.py` - Script to generate all thesis figures
- `plot_all_mpv_fits.py` - Generate comprehensive MPV fit plots
- `appendix/` - Subfolder for appendix figures
- `mpv_fits/` - Subfolder for MPV fit figures

**Usage**: For generating publication-quality figures for thesis/papers.

### 📁 `utilities/` - **General Utilities**
**Purpose**: General utility scripts and tools.

Files:
- `summarize_all_results.py` - Results summarization tools
- `findCuts.py` - Cut optimization utilities

**Usage**: For general data processing and analysis support tasks.

### 📁 `config/` - **Configuration Files** (existing)
**Purpose**: Configuration files for analysis parameters, datasets, and environments.

### 📁 `cache/` - **Cache Directory** (existing)
**Purpose**: Cached data files for faster loading.

### 📁 `__pycache__/` - **Python Cache** (existing)
**Purpose**: Python bytecode cache files.

## Dependency Relationships

### Core Analysis Chain (Used by Minuit_main.py):
```
Minuit_main.py
├── RunManager.py
├── AnalysisConfig.py  
├── HistClass.py
├── selection_manager.py
└── Minuit_Analysis.py
```

### Post-Analysis Tools:
- **Plotting**: Files in `plotting_visualization/` use results from core analysis
- **Comparisons**: Files in `comparison_statistics/` analyze results across runs
- **Thesis**: Files in `thesis_figures/` create publication-ready plots

### Independent Tools:
- **Occupancy**: Files in `occupancy_studies/` can run independently
- **Alternative**: Files in `alternative_analysis/` provide different analysis methods
- **Testing**: Files in `testing_examples/` test various components

## Running the Complete Analysis Workflow

1. **Core Analysis**: 
   ```bash
   cd core_analysis/
   python Minuit_main.py --runs 1 2 3
   ```

2. **Generate Plots**:
   ```bash
   cd ../plotting_visualization/
   # Use plot_utils functions to create plots from saved results
   ```

3. **Statistical Comparisons**:
   ```bash
   cd ../comparison_statistics/
   python Muon_MIP_Comparison_Statistical.py
   ```

4. **Thesis Figures**:
   ```bash
   cd ../thesis_figures/
   python create_thesis_plots.py
   ```

## Import Path Considerations

When running scripts from different folders, you may need to adjust Python paths. Consider using:

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_analysis'))
```

Or run scripts from the project root directory and use relative imports.

## Summary

This organization separates:
- ✅ **Core functionality** (5 files) - minimal, focused
- 📊 **Post-processing tools** - organized by purpose
- 🔬 **Research tools** - testing, comparison, alternative methods
- 📝 **Documentation tools** - thesis figures and examples

This structure makes it easier to:
- Understand what files are essential vs. optional
- Maintain the core analysis pipeline
- Add new functionality without cluttering the main workflow
- Share specific components with collaborators
