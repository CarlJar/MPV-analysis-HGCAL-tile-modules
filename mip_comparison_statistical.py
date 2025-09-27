import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from itertools import combinations

"""
Statistical analysis of MPV values using chi-square and significance in sigma.
This script is based on Muon_MIP_Comparison.py but replaces percentage deviation
with statistical measures for a more physical analysis.
"""

# Define the base paths for each run
BASE_DATA_PATH = '/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/'

# Define the runs to compare
RUNS = {
    "muon_150": "2024-09-16_22-34-48_beamrun_muonss_150",
    "muon_250": "2024-09-19_15-11-45_beamrun_muon_250",
    "muon_250_magnetOn": "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}

# Define the output folder for comparison plots
output_folder = os.path.join(BASE_DATA_PATH, "comparison_plots_statistical")
os.makedirs(output_folder, exist_ok=True)

# Use colorblind-friendly palette
chip_colors = {
    2: '#1b9e77',  # Teal
    3: '#d95f02',  # Orange
    4: '#7570b3'   # Purple
}
all_chips = [2, 3, 4]

# Define chip combinations for thesis plots
chip_run = [
    all_chips,      # All chips together
    [2],            # Chip 2 alone
    [3, 4]          # Chips 3 and 4 together
]
run_names = ["All_Chips", "Chip_2", "Chips_3_and_4"]

def load_analysis_results(run_name):
    """
    Load analysis results from the comprehensive analysis output
    """
    results_path = os.path.join(BASE_DATA_PATH, RUNS[run_name], "analysis_results")
    df_path = os.path.join(results_path, "simplified_results.csv")
    
    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
        return df
    else:
        print(f"Warning: Could not find simplified results at {df_path}")
        return None

def create_statistical_comparison_plots(dfs, titles, chip_sets, run_names):
    """
    Create comparison plots for each combination of runs and chip sets with statistical analysis.
    """
    for (chips, run_name) in zip(chip_sets, run_names):
        for (df1, title1), (df2, title2) in combinations(zip(dfs, titles), 2):
            if df1 is None or df2 is None:
                continue

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), gridspec_kw={"height_ratios": [3, 1]})
            fig.suptitle(f"MIP Value Comparison: {title1} vs {title2}", fontsize=18, y=0.98)

            df1_filtered = df1[df1["chip"].isin(chips)]
            df2_filtered = df2[df2["chip"].isin(chips)]

            if df1_filtered.empty or df2_filtered.empty:
                plt.close(fig)
                continue

            # Extract MPV values and errors
            x_mpv = df1_filtered["mpv"].values
            y_mpv = df2_filtered["mpv"].values
            x_err = np.sqrt(df1_filtered["mpv_err_lower"]**2 + df1_filtered["mpv_err_upper"]**2)
            y_err = np.sqrt(df2_filtered["mpv_err_lower"]**2 + df2_filtered["mpv_err_upper"]**2)

            # Calculate chi-square and significance
            chi_square = np.sum(((y_mpv - x_mpv) / np.sqrt(x_err**2 + y_err**2))**2)
            significance = (y_mpv - x_mpv) / np.sqrt(x_err**2 + y_err**2)

            # Main plot
            ax1.errorbar(x_mpv, y_mpv, xerr=x_err, yerr=y_err, fmt='o', label=f"Chip {chips}")
            ax1.plot([x_mpv.min(), x_mpv.max()], [x_mpv.min(), x_mpv.max()], '--', color='gray', label="Equal Line")
            ax1.set_xlabel(f"MPV ({title1}) [ADC sample value]")
            ax1.set_ylabel(f"MPV ({title2}) [ADC sample value]")
            ax1.legend()
            ax1.text(0.05, 0.95, f"Chi-Square: {chi_square:.2f}", transform=ax1.transAxes, fontsize=12, verticalalignment='top')

            # Residual plot (Significance in sigma)
            ax2.errorbar(x_mpv, significance, fmt='o', label="Significance")
            ax2.axhline(0, color='gray', linestyle='--')
            ax2.set_xlabel(f"MPV ({title1}) [ADC sample value]")
            ax2.set_ylabel("Significance (σ)")
            ax2.legend()

            plt.tight_layout()
            plt.savefig(os.path.join(output_folder, f"Comparison_{title1}_vs_{title2}_{run_name}.pdf"))
            plt.close(fig)

def main():
    # Load data
    data_frames = {}
    run_titles = {}
    
    for run_key, run_name in RUNS.items():
        print(f"Loading data for {run_key} ({run_name})")
        df = load_analysis_results(run_key)
        
        if df is not None:
            readable_title = run_key.replace('_', ' ').title()
            data_frames[run_key] = df
            run_titles[run_key] = readable_title
    
    if len(data_frames) < 2:
        print("Error: Need at least two valid datasets for comparison")
        return
    
    # Create all requested comparisons
    comparisons = [
        ('muon_150', 'muon_250', "150 GeV vs 250 GeV"),
        ('muon_250', 'muon_250_magnetOn', "250 GeV with/without Magnet"),
        ('muon_150', 'muon_250_magnetOn', "150 GeV vs 250 GeV with Magnet")
    ]
    
    for run1, run2, description in comparisons:
        if run1 in data_frames and run2 in data_frames:
            print(f"\nCreating comparison: {description}")
            dfs = [data_frames[run1], data_frames[run2]]
            titles = [run_titles[run1], run_titles[run2]]
            create_statistical_comparison_plots(dfs, titles, chip_run, run_names)
    
    print("Statistical comparison plots created successfully")

if __name__ == "__main__":
    main()