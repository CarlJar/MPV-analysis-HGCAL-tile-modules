
# MPV Analysis for HGCAL Tile Modules

This repository contains analysis tools for Most Probable Value (MPV) analysis of HGCAL tile modules using muon test beam data.

## 📁 Project Organization

The project has been organized into focused folders based on functionality:

- **`core_analysis/`** - Essential files for the main Minuit analysis pipeline
- **`plotting_visualization/`** - All plotting and visualization tools  
- **`comparison_statistics/`** - Statistical comparison tools for different runs
- **`thesis_figures/`** - Scripts for generating thesis/publication figures
- **`occupancy_studies/`** - Detector occupancy analysis tools
- **`alternative_analysis/`** - Alternative fitting methods and approaches
- **`testing_examples/`** - Testing scripts and examples
- **`utilities/`** - General utility scripts
- **`config/`** - Configuration files
- **`cache/`** - Cached data files

📋 **See [FOLDER_ORGANIZATION.md](FOLDER_ORGANIZATION.md) for detailed documentation.**

## 🚀 Quick Start

### Running the Main Analysis

```bash
# Navigate to core analysis folder
cd core_analysis/

# Run analysis for all available runs
python Minuit_main.py --runs 1 2 3

# Run analysis for specific runs  
python Minuit_main.py --runs 1

# List available runs
python Minuit_main.py --list-runs
```

### Available Runs
1. **Run 1**: 150 MeV muons
2. **Run 2**: 250 MeV muons
3. **Run 3**: 250 MeV muons with magnet on

## 🔧 Core Components

**RunManager** (in `core_analysis/`)

**findCuts.py** (in `utilities/`)

This tool is made for classify new aquired data and to find and set data-cuts which will then be used by the **RunManager**.

Start the tool with `python utilities/findCuts.py` and enter the run-name of the data-set you want to work with. 
It will load data with the RunManager from file or from cache. Parameter can be modified in findCuts.py line 115-125.

After loading the data it will plot data for all chip/half combinations. 

To set the data cuts:

```
hover over the plot with your curser to the place you want to set a cut on and press:
    "y" - for the lower trigtime-cut
    "x" - for the higher trigtime-cut
    "c" - for the adc threshold-cut
    
    hit "m" to save the cuts for this chip/half while your curser is still over the plot(!)
```


Close all figures to end the program

**Python Environment using Anaconda3**

How to setup an anaconda3 environment to run the analysis:

Install anaconda3
directory:: `/home/USER/anaconda3`
- download file `Anaconda3-2024.06-1-Linux-x86_64.sh` from https://www.anaconda.com/download/success

```bash
cd ~/Downloads
chmod +x Anaconda3-2024.06-1-Linux-x86_64.sh
./Anaconda3-2024.06-1-Linux-x86_64.sh
```
When followig the instructions, there is the option to run the 'base' conda environment as default in the shell. If you don't run the base environment you have to activate it using `source ~/anaconda3/bin/activate` before using the `conda`-command. 

```bash
#setup conda environment and activate it
conda create --name ENV_NAME
conda activate ENV_NAME

#deactive environment by using:
conda deactivate
```
current dependencies:
- numpy
- pandas
- uproot: `conda install conda-forge::uproot`
- matplotlib
- pyyaml
- root: `conda install root`  (full root framework and PyRoot)

Full dependencies and versions can be found at `config/environment_config.yml`.