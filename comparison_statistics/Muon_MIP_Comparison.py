import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import json
from itertools import combinations
import math
import re
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

"""
Reads the analysis results from the comprehensive analysis output and compares MPV values 
from different runs. Shows error bars in both x and y directions and plots the diagonal line 
(Winkelhalbierende) as the optimal line if all MIP values were equal.
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
output_folder = os.path.join(BASE_DATA_PATH, "comparison_plots")
output_plot_folder = os.path.join(output_folder, "Plots_for_MPV_comparison")
os.makedirs(output_plot_folder, exist_ok=True)

# Use colorblind-friendly palette from colorbrewer2.org (same as thesis_plots.py)
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
    [3, 4]         # Chips 3 and 4 together
]
run_names = ["All_Chips", "Chip_2", "Chips_3_and_4"]

def load_analysis_results(run_name):
    """
    Load analysis results from the comprehensive analysis output
    """
    results_path = os.path.join(BASE_DATA_PATH, RUNS[run_name], "analysis_results")
    
    # Load the simplified DataFrame that should have been created by save_analysis_results
    df_path = os.path.join(results_path, "simplified_results.csv")
    
    if os.path.exists(df_path):
        df = pd.read_csv(df_path)
        return df
    else:
        print(f"Warning: Could not find simplified results at {df_path}")
        return None

def ratio_with_asymmetric_errors(A, A_err_plus, A_err_minus, B, B_err_plus, B_err_minus):
    """
    Calculate the ratio R = A / B and the asymmetric errors ΔR+ and ΔR-.

    Parameters:
    A : float - Value of A
    A_err_plus : float - Upper error of A
    A_err_minus : float - Lower error of A
    B : float - Value of B
    B_err_plus : float - Upper error of B
    B_err_minus : float - Lower error of B

    Returns:
    (R, R_err_plus, R_err_minus)
    """
    # Handle division by zero or negative values
    if B == 0 or A <= 0 or B <= 0:
        return np.nan, np.nan, np.nan
        
    R = A / B  # Ratio

    # Relative errors for upper and lower bounds
    rel_err_plus = np.sqrt((A_err_plus / A) ** 2 + (B_err_minus / B) ** 2)
    rel_err_minus = np.sqrt((A_err_minus / A) ** 2 + (B_err_plus / B) ** 2)

    # Absolute errors
    R_err_plus = R * rel_err_plus
    R_err_minus = R * rel_err_minus

    return R, R_err_plus, R_err_minus

def confidence_ellipse(x, y, ax, n_std=1.0, **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.
    
    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.
    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.
    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.
    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`
    
    Returns
    -------
    matplotlib.patches.Ellipse
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      **kwargs)

    # Calculating the standard deviation of x from the square root of the variance
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)
    
    # Calculating the standard deviation of y from the square root of the variance
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def create_comparison_plots(dfs, titles, chip_sets, run_names):
    """
    Create comparison plots for each combination of runs and chip sets with thesis-quality formatting
    """
    # Set up thesis-quality plotting style
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.figsize': (12, 14),  # Increased figure size
        'figure.dpi': 300,
        'lines.linewidth': 1.5,
        'lines.markersize': 8,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.labelpad': 10,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.2  # Increased padding
    })
    
    # For each chip set (e.g., chip 3 only, chips 2 & 3, all chips)
    for (chips, run_name) in zip(chip_sets, run_names):
        print(f"Creating plots for {run_name} (chips {', '.join(map(str, chips))})")
        
        # Get all combinations of dataframes/titles to compare
        for (df1, title1), (df2, title2) in combinations(zip(dfs, titles), 2):
            if df1 is None or df2 is None:
                print(f"Skipping comparison of {title1} vs {title2} due to missing data")
                continue
                
            print(f"Comparing {title1} vs {title2}")
            
            # Create figure with two subplots (main plot and residual plot)
            fig, (ax1, ax2) = plt.subplots(
                2, 1, figsize=(10, 12), gridspec_kw={"height_ratios": [3, 1]}
            )
            fig.suptitle(f"MIP Value Comparison: {title1} vs {title2}", fontsize=18, y=0.98)

            # Filter for chips we want to include
            df1_filtered = df1[df1["chip"].isin(chips)]
            df2_filtered = df2[df2["chip"].isin(chips)]
            
            if df1_filtered.empty or df2_filtered.empty:
                print(f"No data for selected chips in one or both datasets")
                plt.close(fig)
                continue

            # Find min/max for the diagonal line
            upper1 = df1_filtered["mpv"].max() if not df1_filtered.empty else 0
            upper2 = df2_filtered["mpv"].max() if not df2_filtered.empty else 0
            upper = max(upper1, upper2)

            lower1 = df1_filtered["mpv"].min() if not df1_filtered.empty else 0
            lower2 = df2_filtered["mpv"].min() if not df2_filtered.empty else 0
            lower = min(lower1, lower2)
            
            # Add some margin to min/max
            margin = 0.1 * (upper - lower)
            plot_min = lower - margin
            plot_max = upper + margin

            # Plot diagonal line (Winkelhalbierende)
            x_sample = np.linspace(plot_min, plot_max, 500)
            ax1.plot(x_sample, x_sample, "--", color='gray', alpha=0.7, linewidth=2)
            
            # Empty lists to collect ratio data for all chips
            all_x_mpv = []
            all_y_mpv = []
            all_ratio = []
            all_ratio_err_plus = []
            all_ratio_err_minus = []
            all_x_err_minus = []
            all_x_err_plus = []
            
            # Prepare a list to store channel information for annotations
            channel_info = []
            
            # Plot each chip separately
            for chip in chips:
                # Filter data for this chip
                df1_chip = df1_filtered[df1_filtered["chip"] == chip].copy()
                df2_chip = df2_filtered[df2_filtered["chip"] == chip].copy()
                
                if df1_chip.empty or df2_chip.empty:
                    print(f"No data for chip {chip} in one or both datasets")
                    continue
                    
                # Set channel as index for easier matching
                df1_chip.set_index("channel", inplace=True)
                df2_chip.set_index("channel", inplace=True)
                
                # Find common channels between the two datasets
                common_channels = df1_chip.index.intersection(df2_chip.index)
                
                if len(common_channels) == 0:
                    print(f"No common channels for chip {chip} in {title1} and {title2}")
                    continue
                
                # Filter for common channels
                df1_chip = df1_chip.loc[common_channels]
                df2_chip = df2_chip.loc[common_channels]
                
                # Extract MPV values and errors
                x_mpv = df1_chip["mpv"].values
                y_mpv = df2_chip["mpv"].values
                
                # Get channel numbers for annotations
                channels = df1_chip.index.values
                
                # For plotting error bars, iminuit/bootstrap can give asymmetric errors
                x_err_minus = df1_chip["mpv_err_lower"].values
                x_err_plus = df1_chip["mpv_err_upper"].values
                y_err_minus = df2_chip["mpv_err_lower"].values
                y_err_plus = df2_chip["mpv_err_upper"].values
                
                # Calculate relative errors for filtering out points with excessive errors
                rel_err_x = (x_err_plus + x_err_minus) / (2 * np.abs(x_mpv))
                rel_err_y = (y_err_plus + y_err_minus) / (2 * np.abs(y_mpv))
                
                # Collect all valid data points for this chip
                valid_indices = np.where((rel_err_x < 0.3) & (rel_err_y < 0.3))[0]
                
                if len(valid_indices) < len(x_mpv):
                    print(f"Filtered out {len(x_mpv) - len(valid_indices)} points with excessive errors for chip {chip}")
                
                # Store channel info for annotations
                for i in valid_indices:
                    channel_info.append((x_mpv[i], y_mpv[i], channels[i], chip))
                
                # Plot data points with error bars (only for valid points)
                ax1.errorbar(
                    x_mpv[valid_indices], y_mpv[valid_indices],
                    xerr=[x_err_minus[valid_indices], x_err_plus[valid_indices]],
                    yerr=[y_err_minus[valid_indices], y_err_plus[valid_indices]],
                    linestyle="None",
                    marker="o",
                    markersize=8,
                    color=chip_colors.get(chip, "black"),
                    label=f"Chip {chip} (n={len(valid_indices)})",
                    capsize=3,
                    alpha=0.8,
                    elinewidth=1.5,
                    zorder=3
                )
                
                # Add confidence ellipse if we have enough points
                if len(valid_indices) >= 3:
                    confidence_ellipse(
                        x_mpv[valid_indices], 
                        y_mpv[valid_indices], 
                        ax1,
                        n_std=1.0, 
                        edgecolor=chip_colors.get(chip, "black"), 
                        facecolor='none', 
                        linestyle='--',
                        alpha=0.5,
                        linewidth=1.5
                    )
                
                # Calculate ratio and errors for residual plot
                ratios = []
                ratio_errs_plus = []
                ratio_errs_minus = []
                valid_x_mpv = []
                valid_y_mpv = []
                
                for i in valid_indices:
                    r, r_plus, r_minus = ratio_with_asymmetric_errors(
                        y_mpv[i], y_err_plus[i], y_err_minus[i],
                        x_mpv[i], x_err_plus[i], x_err_minus[i]
                    )
                    ratios.append(r)
                    ratio_errs_plus.append(r_plus)
                    ratio_errs_minus.append(r_minus)
                    valid_x_mpv.append(x_mpv[i])
                    valid_y_mpv.append(y_mpv[i])
                
                # Plot residual (ratio)
                ax2.errorbar(
                    valid_x_mpv,
                    ratios,
                    xerr=[x_err_minus[valid_indices], x_err_plus[valid_indices]],
                    yerr=[ratio_errs_minus, ratio_errs_plus],
                    fmt="o",
                    markersize=8,
                    color=chip_colors.get(chip, "black"),
                    label=f"Chip {chip}",
                    capsize=3,
                    alpha=0.8,
                    elinewidth=1.5,
                    zorder=3
                )
                
                # Collect data for calculating overall statistics
                all_x_mpv.extend(valid_x_mpv)
                all_y_mpv.extend(valid_y_mpv)
                all_ratio.extend(ratios)
                all_ratio_err_plus.extend(ratio_errs_plus)
                all_ratio_err_minus.extend(ratio_errs_minus)
                all_x_err_minus.extend(x_err_minus[valid_indices])
                all_x_err_plus.extend(x_err_plus[valid_indices])
            
            # Optional: Add channel labels to selected points
            # for x, y, ch, chip in channel_info:
            #     ax1.annotate(f"{int(ch)}", (x, y), xytext=(5, 5), textcoords='offset points', 
            #                  fontsize=8, color=chip_colors.get(chip, "black"), alpha=0.7)
            
            # Add unity line to the plot
            unity_x = np.linspace(plot_min, plot_max, 100)
            ax1.plot(unity_x, unity_x, '--', color='gray', alpha=0.7, zorder=1)
            
            # Format main plot
            ax1.set_xlabel(f"MPV ({title1}) [ADC sample value]", fontsize=14)
            ax1.set_ylabel(f"MPV ({title2}) [ADC sample value]", fontsize=14)
            ax1.grid(True, alpha=0.3)
            # Place legend to the right of the plot
            box = ax1.get_position()
            ax1.set_position([box.x0, box.y0, box.width * 0.9, box.height])
            ax1.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left', framealpha=0.9)
            ax1.set_xlim(plot_min, plot_max)
            ax1.set_ylim(plot_min, plot_max)
            ax1.tick_params(axis='both', which='major', labelsize=12)
            
            # Add title inside the plot
            plot_description = f"Run comparison: {run_name.replace('_', ' ')}"
            ax1.text(0.02, 0.02, plot_description, transform=ax1.transAxes, 
                    fontsize=13, bbox=dict(facecolor='white', alpha=0.8))
            
            # Add unity line to ratio plot
            ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7, zorder=2)
            
            # Calculate mean ratio and std dev for annotation
            valid_ratios = [r for r in all_ratio if not np.isnan(r)]
            if valid_ratios:
                mean_ratio = np.mean(valid_ratios)
                std_ratio = np.std(valid_ratios)
                median_ratio = np.median(valid_ratios)
                
                # Add detailed statistics to the ratio plot
                stats_text = (f"Mean ratio: {mean_ratio:.3f} ± {std_ratio:.3f}\n"
                              f"Median ratio: {median_ratio:.3f}\n"
                              f"Points: {len(valid_ratios)}")
                              
                # Format statistics text with each value on a new line
                box = ax2.get_position()
                ax2.set_position([box.x0, box.y0, box.width * 0.9, box.height])
                stats_lines = [
                    f"Mean: {mean_ratio:.3f} ± {std_ratio:.3f}",
                    f"n = {len(valid_ratios)}"
                ]
                ax2.legend(fontsize=10, bbox_to_anchor=(1.05, 1.4), loc='upper left', framealpha=0.9,
                          title='\n'.join(stats_lines), title_fontsize=10)
            
            # Format ratio plot
            ax2.set_xlabel(f"MPV ({title1}) [ADC sample value]", fontsize=12)
            ax2.set_ylabel(f"Ratio {title2}/{title1}", fontsize=12)
            ax2.grid(True, alpha=0.3, which='both')
            ax2.grid(True, which='minor', alpha=0.1)
            ax2.set_xlim(plot_min, plot_max)
            
            # Set reasonable y-limits for ratio plot with symmetrical margins
            valid_ratio_min = np.nanmin(all_ratio) if all_ratio else 0.8
            valid_ratio_max = np.nanmax(all_ratio) if all_ratio else 1.2
            ratio_margin = max(0.1, abs(1 - valid_ratio_min), abs(1 - valid_ratio_max))
            ax2.set_ylim(1 - ratio_margin - 0.05, 1 + ratio_margin + 0.05)
            ax2.tick_params(axis='both', which='major', labelsize=10)
            ax2.tick_params(axis='both', which='minor', labelsize=8)
            
            # Calculate percentage deviation from unity
            mean_deviation = abs(mean_ratio - 1.0) * 100 if 'mean_ratio' in locals() else None
            
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])
            
            # Save figure
            filename = f"Comparison_{title1.replace(' ', '_')}_vs_{title2.replace(' ', '_')}_{run_name}.pdf"
            filepath = os.path.join(output_plot_folder, filename)
            plt.savefig(filepath)
            print(f"Saved plot to {filepath}")
            
            # Also save as PNG for easier viewing
            png_filepath = filepath.replace('.pdf', '.png')
            plt.savefig(png_filepath)
            
            plt.close(fig)

def main():
    # Load data
    data_frames = {}
    run_titles = {}
    
    for run_key, run_name in RUNS.items():
        print(f"Loading data for {run_key} ({run_name})")
        df = load_analysis_results(run_key)
        
        if df is not None:
            # Create a more readable title
            readable_title = run_key.replace('_', ' ').title()
            data_frames[run_key] = df
            run_titles[run_key] = readable_title
    
    # Check if we have at least two datasets for comparison
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
            create_comparison_plots(dfs, titles, chip_run, run_names)
    
    print("Comparison plots created successfully")

if __name__ == "__main__":
    main()
