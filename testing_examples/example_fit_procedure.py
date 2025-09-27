"""
Create a comprehensive figure showing the MPV extraction procedure steps.
Uses thesis-quality plotting standards and colorblind-friendly colors.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import os

from thesis_plotting_config import (
    COLORS, 
    AXIS_LABELS,
    format_axis_labels,
    add_subplot_label,
    get_figure_dimensions
)

from enhanced_plotter import ThesisPlotter

def create_procedure_plot(channel=0, chip=2):
    """
    Create a 2x2 panel figure showing the MPV extraction procedure.
    Uses a well-behaving channel as example.
    """
    # Initialize plotter with analysis results
    base_path = "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/2024-09-16_22-34-48_beamrun_muonss_150"
    base_path = "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/2024-09-19_15-11-45_beamrun_muon_250"
    plotter = ThesisPlotter(base_path)
    
    # Create figure with 2x2 layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Get data for the selected channel
    result = None
    for data in plotter.complete_data:
        if data['chip'] == chip and data['channel'] == channel:
            result = data
            break
    
    if result is None or result['status'] != 'success':
        print(f"No successful results for chip {chip}, channel {channel}")
        return None
        
    #print(result)
        
    # Panel A: Raw Histogram
    hist_data = result['hist_data']
    ax1.hist(result['adc_values'], bins=hist_data['bin_edges'], 
             histtype='step', color='black', linewidth=1.5)
    ax1.set_xlabel('ADC Value')
    ax1.set_ylabel('Counts')
    add_subplot_label(ax1, 'A', title='Raw Data')
    
    # Plot B: Initial Gaussian guess
    # Plot histogram like in panel A
    ax2.hist(result['adc_values'], bins=hist_data['bin_edges'], 
             histtype='step', color='black', linewidth=1.5)
    
    # Plot Gaussian guess over the histogram
    x_gauss = result['gauss_fit']['x_fit']
    y_gauss = result['gauss_fit']['y_fit']
    ax2.plot(x_gauss, y_gauss, color=COLORS['gauss'], 
             label='Gaussian Initial Guess', linestyle='--', linewidth=2)
    
    ax2.set_xlabel('ADC Sample Value')
    ax2.set_ylabel('Counts')
    add_subplot_label(ax2, 'B', title='Gaussian Initial Guess')
    
    ax2.set_xlabel('ADC Sample Value')
    ax2.set_ylabel('Counts')
    ax2.legend(loc='upper left')
    
    
    
    
    # Panel C: Landau-Gauss Fit (moved from D)
    fit_data = result['reduced_hist_data']['fit']
    ax3.hist(result['adc_values'], bins=hist_data['bin_edges'],
             histtype='step', color='black', linewidth=1.5)
    
    # Show Landau-Gauss fit range
    ax3.axvspan(fit_data['bin_edges'][0], fit_data['bin_edges'][-1],
                color=COLORS['fit_langaus'], alpha=0.1, label='Landau-Gauss Fit Range')
    
    # Plot data points and Landau-Gauss fit
    langaus_fit = result['langaus_fit']
    bin_centers = fit_data['bin_mids']
    bin_contents = fit_data['bin_counts']
    bin_errors = np.sqrt(bin_contents)
    
    ax3.errorbar(bin_centers, bin_contents, yerr=bin_errors,
                fmt='o', color='black', markersize=4, 
                capsize=2, label='Data')
    
    # Plot the Landau-Gauss fit curve
    ax3.plot(langaus_fit['x_fit'], langaus_fit['y_fit'],
             color=COLORS['fit_langaus'], linestyle='--', linewidth=2,
             label='Landau-Gauss Fit')
    
    ax3.set_xlabel('ADC Sample Value')
    ax3.set_ylabel('Counts')
    ax3.legend()
    add_subplot_label(ax3, 'C', title='Landau-Gauss Fit')
    
    # Panel D: MPV and Error Estimates
    langaus_fit = result['langaus_fit']
    bootstrap = result['bootstrap_results']
    fit_data = result['reduced_hist_data']['fit']
    
    # Plot only the data points with error bars
    bin_centers = fit_data['bin_mids']
    bin_contents = fit_data['bin_counts']
    bin_errors = np.sqrt(bin_contents)
    
    ax4.errorbar(bin_centers, bin_contents, yerr=bin_errors,
                fmt='o', color='black', markersize=4, 
                capsize=2, label='Data')
    
    # Plot the Landau-Gauss fit curve
    ax4.plot(langaus_fit['x_fit'], langaus_fit['y_fit'],
             color=COLORS['fit_langaus'], linewidth=2,
             label='Landau-Gauss Fit')
             
    # Add MPV with asymmetric error region
    mpv = bootstrap['mpv']
    # Get asymmetric errors from bootstrap results
    mpv_err_lower = bootstrap['mpv_err_estimate'][0][0] if 'mpv_err_estimate' in bootstrap else bootstrap['mpv_err']
    mpv_err_upper = bootstrap['mpv_err_estimate'][1][0] if 'mpv_err_estimate' in bootstrap else bootstrap['mpv_err']
    
    # Plot MPV line
    ax4.axvline(mpv, color=COLORS['mpv'], linestyle='-', linewidth=2,
                label=f'MPV = {mpv:.1f}')
    
    # Add asymmetric error region
    ax4.axvspan(mpv - mpv_err_lower, mpv + mpv_err_upper,
                color=COLORS['mpv'], alpha=0.2,
                label=f'MPV Error Range (+{mpv_err_upper:.1f}/-{mpv_err_lower:.1f})')
    
    ax4.set_xlabel('ADC Sample Value')
    ax4.set_ylabel('Counts')
    ax4.legend()
    add_subplot_label(ax4, 'D', title='Fit & MPV')
    
    # Overall formatting
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 400)
    
    plt.tight_layout()
    
    # Save figure
    output_path = "thesis_figures/mpv_extraction_procedure.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Saved figure to {output_path}")
    
    return fig, ((ax1, ax2), (ax3, ax4))

if __name__ == "__main__":
    create_procedure_plot(channel=23, chip=2)