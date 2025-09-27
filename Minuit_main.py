import numpy as np
import itertools
import argparse
import sys

import scipy.stats as norm
import scipy as sp

from RunManager import RunManager, dataTupel
from AnalysisConfig import AnalysisConfig

import os
import pandas as pd

from HistClass import HistogramClass
from selection_manager import selection_manager
from Minuit_Analysis import perform_analysis_noplot, save_analysis_results

# ====================================================================
#   __  __       _
#  |  \/  | __ _(_)_ __
#  | |\/| |/ _` | | '_ \
#  | |  | | (_| | | | | |
#  |_|  |_|\__,_|_|_| |_|
# ====================================================================

aconf = AnalysisConfig()
reload = True

active_channels = {
    "A5": {
        "chip": 2,
        "channels": np.array([0, 1, 2, 3, 4, 5, 23, 24, 28, 29, 30, 31, 36, 37]),
        "pedestal": 0,
        "plot_dim": (4, 4),
    },
    "B12_0": {
        "chip": 3,
        "channels": np.array([9, 11, 29, 35, 38, 39, 49, 60, 66, 67]),
        "pedestal": 0,
        "plot_dim": (4, 3),
    },
    "B12_1": {
        "chip": 4,
        "channels": np.array([0, 1, 6, 7]),
        "pedestal": 0,
        "plot_dim": (2, 2),
    },
}

#                       configure output path
# ====================================================================

# output_folder = "/home/cjarschke/mount/daq/CERN_TB_2024_09_Analysis/"
# output_folder = "/home/carlj/mount/daq/CERN_TB_2024_09_Analysis/"
output_folder = "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/"


#                       Run selection
# ====================================================================

# Define run mapping dictionary
RUN_MAP = {
    1: "2024-09-16_22-34-48_beamrun_muonss_150",
    2: "2024-09-19_15-11-45_beamrun_muon_250",
    3: "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}

# Set up argument Parser
def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Minuit analysis on selected runs')
    parser.add_argument('--runs', nargs='+', type=int, default=[1],
                        help='Run numbers to process (1=150MeV, 2=250MeV, 3=250MeV+magnet)')
    parser.add_argument('--list-runs', action='store_true',
                        help='List available runs and exit')
    parser.add_argument('--use-tailcut', action='store_true',
                        help='Enable tail cut in the analysis (default: disabled)')
    return parser.parse_args()

# Parse command line arguments
args = parse_arguments()

# If --list-runs flag is provided, print available runs and exit
if args.list_runs:
    print("Available runs:")
    for num, name in RUN_MAP.items():
        print(f"{num}: {name}")
    sys.exit(0)

# Check if all specified run numbers are valid
invalid_runs = [run for run in args.runs if run not in RUN_MAP]
if invalid_runs:
    print(f"Error: Invalid run numbers: {invalid_runs}")
    print("Available runs:")
    for num, name in RUN_MAP.items():
        print(f"{num}: {name}")
    sys.exit(1)

# Process each selected run
for run_number in args.runs:
    run = RUN_MAP[run_number]
    print(f"\n{'='*60}")
    print(f"Processing run {run_number}: {run}")
    print(f"{'='*60}\n")

    #                       Run Manager
    # ====================================================================
    rm = RunManager(run, ECONT=False)

    rm.load(
        columns=dataTupel(
            daq=[
                "adc",
                "adcm",  # pedestal subtraction
                "trigtime",
                "corruption",
                "channel",
                "half",
                "chip",
            ]
        ),
        pre_cut=dataTupel(daq="(corruption == 0) & (adc > 0) & (adc < 1020)"),
        preCut_trigtimeCut=True,
        preCut_thresholdCut=True,
    )

    #                       Substract pedestal
    # ====================================================================
    rm.daq.loc[:, "adc"] = rm.daq.loc[:, "adc"] - rm.daq.loc[:, "adcm"]


    #      Selection (if only specific chips/ channel are looked at)
    # ====================================================================
    #   ____       _           _   _
#  / ___|  ___| | ___  ___| |_(_) ___  _ __
#  \___ \ / _ \ |/ _ \/ __| __| |/ _ \| '_ \
#   ___) |  __/ |  __/ (__| |_| | (_) | | | |
#  |____/ \___|_|\___|\___|\__|_|\___/|_| |_|

    selected_items=selection_manager(active_channels,channel=None,chip=None)
    # selected_items = selection_manager(active_channels, chip=4, channel=[0,1,6,7])


    #               Fitting and plotting for each channel
    # ====================================================================

    analysis_results = []

    for tbname, tbconf in selected_items.items():
        df_tb_chip = rm.daq.query(f"chip == {tbconf['chip']} &  adc < 400")

        for ch in tbconf["channels"]:
            print("===============================================")
            print(tbname, f"channel {ch}")
            print("===============================================")

            df_channel = df_tb_chip.query(f"channel == {ch}")

            if df_channel.empty:
                print(f"No data for channel {ch}, skipping this channel.")
                continue

            adc_values_above_pedestal = df_channel["adc"].values[
                df_channel["adc"] > tbconf["pedestal"]
            ]
            if len(adc_values_above_pedestal) == 0:
                print(f"No ADC values above pedestal for channel {ch}. Skipping.")
                continue

            #                       Analysis without plotting
            # ====================================================================
            try:
                result = perform_analysis_noplot(
                    df_channel,
                    "adc",
                    ch,
                    use_tailcut=args.use_tailcut,
                )
                if result is None:
                    print(f"Analysis returned None for channel {ch}")
                    continue
            except Exception as e:
                print(f"Error analyzing channel {ch}: {str(e)}")
                print("Skipping this channel.")
                continue

            # Store all analysis results for later plotting
            if result is not None:
                result['chip'] = tbconf['chip']  # Add chip info
                result['tbname'] = tbname
                analysis_results.append(result)

            # Skip to the next channel if fitting failed or had issues
            if result is None or result['status'] != 'success':
                print(f"Channel {ch}: Analysis status: {result['status'] if result else 'None'}")
                continue

            # Print analysis status
            print(f"Channel {ch}: Analysis status: {result['status']}")

    # ====================================================================
    #                       Save analysis results to file
    # ====================================================================
    if not os.path.exists(output_folder + run):
        os.makedirs(output_folder + run, exist_ok=True)

    # Save comprehensive analysis results
    comprehensive_output_path = output_folder + run + "/analysis_results"
    df_simplified = save_analysis_results(analysis_results, comprehensive_output_path)
    print(f"Analysis results saved to {comprehensive_output_path}/complete_results.pkl and {comprehensive_output_path}/simplified_results.h5")

    print(f"\nAnalysis complete for run {run_number} ({run})!")
    print(f"Channels processed: {len(analysis_results)}")
    print(f"Successful fits: {len([r for r in analysis_results if r['status'] == 'success'])}")

    # Example of how to create plots from saved data:
    print(f"\nTo create plots for this run, use:")
    print(f"from plot_utils import plot_from_saved_data")
    print(f"plot_from_saved_data('{comprehensive_output_path}')")
    print(f"# or for specific chip:")
    print(f"plot_from_saved_data('{comprehensive_output_path}', chip=2)")
    print(f"# or for specific channel:")
    print(f"plot_from_saved_data('{comprehensive_output_path}', chip=2, channel=0)")

print("\nAll requested runs have been processed!")