"""
Generate thesis-quality plots to explain the analysis steps and results.
Follows accessibility guidelines and focuses on clarity.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec

def set_thesis_style():
    """Set publication-quality plot style with colorblind-friendly colors."""
    plt.style.use('seaborn-v0_8-paper')
    
    # Use colorblind-friendly palette from colorbrewer2.org
    colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a']  # Dark2 palette, proven for colorblindness
    
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.figsize': (10, 5),
        'figure.dpi': 300,
        'lines.linewidth': 1.5,
        'lines.markersize': 8,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.labelpad': 10,
        'axes.prop_cycle': plt.cycler('color', colors)
    })

def create_mpv_boxplot(data, output_path):
    """
    Create a boxplot of MPV distributions per chip for each run.
    
    Parameters:
    - data: DataFrame with the analysis results
    - output_path: Path to save the plot
    """
    set_thesis_style()
    
    # Identify outlier points (more than 3 std from median)
    chip_stats = data.groupby('Chip')['MPV'].agg(['median', 'std'])
    outliers = []
    
    # for chip in chip_stats.index:
    #     median = chip_stats.loc[chip, 'median']
    #     std = chip_stats.loc[chip, 'std']
    #     mask = (data['Chip'] == chip) & \
    #            (np.abs(data['MPV'] - median) > 3 * std)
    #     outliers.extend(data[mask].index.tolist())
    
    fig = plt.figure(figsize=(12, 6))
    
    # Create boxplot with all data
    box_plot = sns.boxplot(data=data, x='Chip', y='MPV', hue='Run', width=0.7, showfliers=True)
    
    # Get the legend handles and labels from the boxplot
    box_handles, box_labels = box_plot.get_legend_handles_labels()
    
    # Print debugging information about the data
    print("\nDebugging MPV distribution:")
    for chip in sorted(data['Chip'].unique()):
        chip_data = data[data['Chip'] == chip]
        print(f"\nChip {chip} statistics:")
        print(chip_data.groupby('Run')['MPV'].describe())
    
    # Highlight and label outlier points
    # outlier_data = data.loc[outliers]
    # print("\nCustom identified outliers (>3σ):")
    # print(outlier_data)
    # if not outlier_data.empty:
    #     # Plot outliers with distinct markers
    #     outlier_scatter = plt.scatter(outlier_data['Chip'], outlier_data['MPV'],
    #                                 color='red', marker='*', s=200, 
    #                                 label='Outliers (>3σ)',
    #                                 zorder=10)  # ensure outliers are on top
        
    #     # Add outlier to legend handles
    #     box_handles.append(outlier_scatter)
        
    #     # Add channel number labels
    #     for idx, row in outlier_data.iterrows():
    #         plt.annotate(f'Ch {row["Channel"]}',
    #                     xy=(row['Chip'], row['MPV']),
    #                     xytext=(15, 15), textcoords='offset points',
    #                     bbox=dict(facecolor='white', edgecolor='red', alpha=0.8,
    #                             boxstyle='round,pad=0.5'),
    #                     arrowprops=dict(arrowstyle='fancy',
    #                                   connectionstyle='arc3,rad=0.2',
    #                                   color='red'),
    #                     fontsize=10,
    #                     fontweight='bold')
    
    # Customize plot
    plt.xlabel('Chip Number')
    plt.ylabel('Most Probable Value (ADC)')
    plt.title('Distribution of MPV Values per Chip and Run')
    
    # Create legend with both boxplot elements and outliers
    # plt.legend(box_handles, box_labels + (['Outliers (>3σ)'] if outlier_data is not None and not outlier_data.empty else []),
    #           title='Run', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.legend(box_handles, box_labels,
              title='Run', bbox_to_anchor=(1.02, 1), loc='upper left')
    # Add grid for better readability
    plt.grid(True, alpha=0.3)
    
    # Save plot with extra space for legend
    plt.savefig(os.path.join(output_path, 'mpv_distribution_per_chip.pdf'), 
                bbox_inches='tight', dpi=300,
                bbox_extra_artists=(plt.gca().get_legend(),))
    plt.close()

def create_uncertainty_scatter(data, output_path):
    """
    Create a scatter plot of MPV uncertainty vs. number of entries.
    
    Parameters:
    - data: DataFrame with the analysis results
    - output_path: Path to save the plot
    """
    set_thesis_style()
    
    # Calculate average uncertainty for each point
    data['Avg_Uncertainty'] = (np.abs(data['MPV_err_low']) + 
                             np.abs(data['MPV_err_high'])) / 2
    
    fig = plt.figure(figsize=(10, 6))
    
    # Create scatter plot using matplotlib for more marker flexibility
    markers = ['x', 'o', '+']  # Mix of filled and unfilled markers
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    
    # Plot each chip separately
    for chip in sorted(data['Chip'].unique()):
        chip_data = data[data['Chip'] == chip]
        plt.scatter(chip_data['N_entries'], chip_data['Avg_Uncertainty'],
                   marker=markers[int(chip-2)],  # chip numbers start at 2
                   label=f'Chip {chip}',
                   alpha=0.8, s=100)
    
    # Customize plot
    plt.xlabel('Number of Entries')
    plt.ylabel('Average MPV Uncertainty (ADC)')
    plt.title('MPV Uncertainty vs. Statistics')
    
    # Use log scale for better visualization
    plt.xscale('log')
    plt.yscale('log')
    
    # Add grid with minor gridlines for log scale
    plt.grid(True, which="major", ls="-", alpha=0.2)
    plt.grid(True, which="minor", ls=":", alpha=0.1)
    
    # Adjust legend to prevent overlap
    plt.legend(title='Run', bbox_to_anchor=(1.02, 1), loc='upper left')
    
    # Save plot with extra space for legend
    plt.savefig(os.path.join(output_path, 'mpv_uncertainty_vs_statistics.pdf'),
                bbox_inches='tight', dpi=300,
                bbox_extra_artists=(plt.gca().get_legend(),))
    plt.close()

def main():
    # Read the summary data
    summary_path = "thesis_summary_tables/detailed_summary.csv"
    output_path = "thesis_figures"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Set style for better-looking plots
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 12,
        'figure.figsize': (10, 5)
    })
    
    # Read data
    print("Reading summary data...")
    data = pd.read_csv(summary_path)
    
    # Create plots
    print("Creating boxplot...")
    print(data)
    create_mpv_boxplot(data, output_path)
    
    print("Creating uncertainty scatter plot...")
    create_uncertainty_scatter(data, output_path)
    
    print(f"Plots have been saved to {output_path}/")

if __name__ == "__main__":
    main()
