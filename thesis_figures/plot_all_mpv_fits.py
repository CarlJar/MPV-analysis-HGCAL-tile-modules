"""
Create a comprehensive multi-panel plot showing MPV fits for all channels.
Each panel shows:
- Raw histogram
- Landau-Gauss fit
- MPV with error region
- Goodness of fit value
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from plotting_visualization.plot_utils import plot_from_saved_data, AnalysisPlotter
from plotting_visualization.thesis_plotting_config import (
    COLORS, 
    format_axis_labels,
    add_subplot_label,
    get_figure_dimensions
)

from plotting_visualization.enhanced_plotter import ThesisPlotter

def create_mpv_overview_plot(run_path, output_dir="thesis_figures/mpv_fits"):
    """
    Create overview plots for all channels in a run.
    
    Parameters:
    -----------
    run_path : str
        Path to the run directory containing analysis results
    output_dir : str
        Directory where to save the output plots
    """
    plotter = ThesisPlotter(run_path)
    
    # Group results by chip
    chip_results = {}
    for result in plotter.complete_data:
        if result['status'] != 'success':
            continue
        
        chip = result.get('chip', 0)
        if chip not in chip_results:
            chip_results[chip] = []
        chip_results[chip].append(result)
    
    # Create plots for each chip
    for chip, results in chip_results.items():
        # Sort by channel number
        results.sort(key=lambda x: x['channel'])
        
        # Calculate grid size - make it as square as possible
        n_channels = len(results)
        n_cols = int(np.ceil(np.sqrt(n_channels)))
        n_rows = int(np.ceil(n_channels / n_cols))
        
        # Calculate figure size for appendix page (A4 landscape)
        # A4 landscape size in inches: 11.69 × 8.27
        # Make it 85% of A4 size to leave room for captions
        scale_factor = 0.85
        max_width = 11.69 * scale_factor
        max_height = 8.27 * scale_factor
        # Account for margins and title
        usable_width = max_width - 0.8
        usable_height = max_height - 1.0
        # Calculate subplot size
        width_per_plot = usable_width / n_cols
        height_per_plot = usable_height / n_rows
        
        # Create figure
        fig, axes = plt.subplots(n_rows, n_cols, 
                                figsize=(max_width, max_height),
                                squeeze=False)
        
        # Add combined title with run information
        run_name = os.path.basename(run_path)
        title_text = f'Chip {chip} - MPV Fits Overview\n{run_name}'
        plt.suptitle(title_text, y=0.98, fontsize=10, linespacing=1.5)
        
        # Plot each channel
        for idx, result in enumerate(results):
            row = idx // n_cols
            col = idx % n_cols
            ax = axes[row, col]
            
            # Get data
            hist_data = result['hist_data']
            fit_data = result['reduced_hist_data']['fit']
            langaus_fit = result['langaus_fit']
            bootstrap = result['bootstrap_results']
            channel = result['channel']
            gof = result['langaus_fit']['gof']
            
            # Plot histogram
            ax.hist(result['adc_values'], bins=hist_data['bin_edges'],
                   histtype='step', color='black', linewidth=1, alpha=0.3)
            
            # Plot fitted data points
            bin_centers = fit_data['bin_mids']
            bin_contents = fit_data['bin_counts']
            bin_errors = np.sqrt(bin_contents)
            ax.errorbar(bin_centers, bin_contents, yerr=bin_errors,
                      fmt='o', color=COLORS['data'], markersize=3,
                      capsize=1, label='Fitted Data')
            
            # Plot Landau-Gauss fit
            ax.plot(langaus_fit['x_fit'], langaus_fit['y_fit'],
                   color=COLORS['langaus'], linewidth=1.5,
                   label='Landau-Gauss Fit')
            
            # Add MPV and error region
            mpv = bootstrap['mpv']
            mpv_err_lower = bootstrap['mpv_err_estimate'][0][0] if 'mpv_err_estimate' in bootstrap else bootstrap['mpv_err']
            mpv_err_upper = bootstrap['mpv_err_estimate'][1][0] if 'mpv_err_estimate' in bootstrap else bootstrap['mpv_err']
            
            # Plot MPV line and error region
            ax.axvline(mpv, color=COLORS['error_band'], linestyle='-', linewidth=1.5)
            ax.axvspan(mpv - mpv_err_lower, mpv + mpv_err_upper,
                      color=COLORS['error_band'], alpha=0.15)
            
            # Add info box in top right
            info_text = (
                f'Channel {channel}\n'
                f'MPV = {mpv:.1f}\n'
                f'+{mpv_err_upper:.1f}/-{mpv_err_lower:.1f}\n'
                f'GoF = {gof:.1f}'
            )
            ax.text(0.95, 0.95, info_text,
                   transform=ax.transAxes,
                   va='top', ha='right',
                   bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
                   color='red' if gof > 3.0 * np.sum(fit_data['bin_counts']) else 'black',
                   fontsize=8)
            
            ax.set_xlim(0, 400)
            ax.grid(True, alpha=0.2)
            
            # Reduce tick label size
            ax.tick_params(axis='both', which='major', labelsize=8)
            
            if row == n_rows-1:
                ax.set_xlabel('ADC Value', fontsize=8)
            if col == 0:
                ax.set_ylabel('Counts', fontsize=8)
                
            # Set channel title
            ax.set_title(f"Channel {channel}", fontsize=8, pad=2)
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Optional: Highlight bad fit quality visually
            if gof > 3.0 * np.sum(fit_data['bin_counts']):
                for spine in ax.spines.values():
                    spine.set_edgecolor('red')
                    spine.set_linewidth(1.2)
        
        # Remove empty subplots
        for idx in range(len(results), n_rows * n_cols):
            row = idx // n_cols
            col = idx % n_cols
            fig.delaxes(axes[row, col])
        
        plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
        
        # Save figure
        os.makedirs(output_dir, exist_ok=True)
        # Create filename from run name and chip
        run_name = os.path.basename(run_path)
        output_path = os.path.join(output_dir, f'mpv_fits_{run_name}_chip_{chip}.pdf')
        # Save in landscape orientation
        plt.savefig(output_path, bbox_inches='tight', dpi=300, orientation='landscape')
        print(f"Saved figure to {output_path}")
        
        plt.close(fig)

if __name__ == "__main__":
    # Example usage
    run_paths = [
        "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/2024-09-16_22-34-48_beamrun_muonss_150",
        "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/2024-09-19_15-11-45_beamrun_muon_250",
        "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
    ]
    
    for run_path in run_paths:
        print(f"\nProcessing run: {Path(run_path).name}")
        create_mpv_overview_plot(run_path)
