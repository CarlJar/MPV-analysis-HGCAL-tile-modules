
**RunManager** 

is a generic tool to load, cache and pre-cut datasets. See "findCuts.py" (line 114-126) as an example how to use it.

use:
1. - create a RunManager
2. - RunManager.load: choose columns, pre_cut, number of files...
    
- unless you force a Reload the RunManager will decide if it takes cached Data or reload the Data
- after changing the number of files, preview_size etc a forced reload is recommended

**findCuts.py**

This tool is made for classify new aquired data and to find and set data-cuts which will then be used by the **RunManager**.

Start the tool with `python ./findCuts.py` and enter the run-name of the data-set you want to work with. 
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