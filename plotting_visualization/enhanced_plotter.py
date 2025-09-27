"""
Enhanced plotting functionality for thesis-quality figures focused on fit analysis and error estimation.
"""
from plot_utils import AnalysisPlotter
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from thesis_plotting_config import (
    COLORS, 
    AXIS_LABELS,
    format_axis_labels,
    add_subplot_label,
    get_figure_dimensions
)
from landaupy import langauss as landaupy_langauss

class ThesisPlotter(AnalysisPlotter):
    def __init__(self, data_path):
        """Initialize with parent class."""
        # If data_path is a directory, append default filenames
        if Path(data_path).is_dir():
            data_path = Path(data_path) / "analysis_results"
        super().__init__(str(data_path))
    
    def plot_fit_procedure(self, channel, chip):
        """Create a comprehensive plot showing the fit procedure steps."""
        result = None
        for data in self.complete_data:
            if data['chip'] == chip and data['channel'] == channel:
                result = data
                break
                
        if result is None or result['status'] != 'success':
            return None
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=get_figure_dimensions('square'))
        
        # 1. Raw data with Gaussian pre-fit
        hist_data = result['hist_data']
        bin_centers = hist_data['bin_mids']
        counts = hist_data['bin_counts']
        errors = np.sqrt(counts)
        
        ax1.errorbar(bin_centers, counts, yerr=errors, fmt='o',
                    color=COLORS['blue'], label='Data',
                    markersize=4, elinewidth=1, capsize=2)
                    
        x_fit = result['gauss_fit']['x_fit']
        y_fit = result['gauss_fit']['y_fit']
        ax1.plot(x_fit, y_fit, color=COLORS['green'],
                linestyle='--', label='Gaussian Pre-fit')
                
        format_axis_labels(ax1, AXIS_LABELS['adc'], AXIS_LABELS['counts'])
        ax1.set_title('1. Initial Gaussian Fit')
        ax1.legend(loc='upper right')
        
        # 2. Gradient-based range selection
        reduced_data = result['reduced_hist_data']['fit']
        bin_centers_red = reduced_data['bin_mids']
        counts_red = reduced_data['bin_counts']
        errors_red = np.sqrt(counts_red)
        
        ax2.errorbar(bin_centers, counts, yerr=errors, fmt='o',
                    color=COLORS['gray'], alpha=0.3,
                    markersize=4, elinewidth=1, capsize=2, label='Full Data')
        ax2.errorbar(bin_centers_red, counts_red, yerr=errors_red, fmt='o',
                    color=COLORS['blue'], label='Selected Range',
                    markersize=4, elinewidth=1, capsize=2)
                    
        if 'gradient_data' in reduced_data:
            grad_data = reduced_data['gradient_data']
            if isinstance(grad_data, dict):
                ax2.axvline(grad_data.get('left_cut', 0), color=COLORS['red'], 
                          linestyle='--', label='Gradient Cut')
                ax2.axvline(grad_data.get('right_cut', max(bin_centers)), 
                          color=COLORS['red'], linestyle='--')
                
        format_axis_labels(ax2, AXIS_LABELS['adc'], AXIS_LABELS['counts'])
        ax2.set_title('2. Range Selection')
        ax2.legend(loc='upper right')
        
        # 3. Final Fit with Components
        ax3.errorbar(bin_centers_red, counts_red, yerr=errors_red, fmt='o',
                    color=COLORS['blue'], label='Data',
                    markersize=4, elinewidth=1, capsize=2)
                    
        x_fit = result['langaus_fit']['x_fit']
        y_fit = result['langaus_fit']['y_fit']
        y_landau = result['langaus_fit'].get('y_landau', None)
        
        ax3.plot(x_fit, y_fit, color=COLORS['red'],
                linestyle='-', label='Langaus Fit')
        if y_landau is not None:
            ax3.plot(x_fit, y_landau, color=COLORS['purple'],
                    linestyle=':', label='Landau Component')
            
        format_axis_labels(ax3, AXIS_LABELS['adc'], AXIS_LABELS['counts'])
        ax3.set_title('3. Final Langaus Fit')
        ax3.legend(loc='upper right')
        
        # 4. Parameter Space Analysis
        params = result['langaus_fit']['params']
        param_errs = result['langaus_fit']['param_errors']
        mpv = params[0]
        mpv_err = float(param_errs[0] if isinstance(param_errs[0], (int, float)) else param_errs[0][0])
        
        x_dense = np.linspace(max(0, mpv-50), mpv+50, 200)
        
        # Base Langaus
        base = landaupy_langauss.pdf(x_dense, mpv, params[1], params[2])
        # MPV + error
        up = landaupy_langauss.pdf(x_dense, mpv + mpv_err, params[1], params[2])
        # MPV - error
        down = landaupy_langauss.pdf(x_dense, mpv - mpv_err, params[1], params[2])
        
        ax4.plot(x_dense, base, color=COLORS['red'], 
                label=f'MPV = {mpv:.1f}')
        ax4.plot(x_dense, up, color=COLORS['blue'], linestyle='--',
                label=f'MPV + {mpv_err:.1f}')
        ax4.plot(x_dense, down, color=COLORS['green'], linestyle=':',
                label=f'MPV - {mpv_err:.1f}')
        if isinstance(mpv_err, (list, np.ndarray)):
            try:
                err_low = float(mpv_err[0][0]) if isinstance(mpv_err[0], (list, np.ndarray)) else float(mpv_err[0])
                err_high = float(mpv_err[1][0]) if isinstance(mpv_err[1], (list, np.ndarray)) else float(mpv_err[1])
                ax4.axvspan(mpv - err_low, mpv + err_high,
                          color=COLORS['orange'], alpha=0.2,
                          label='MPV Uncertainty')
            except (IndexError, TypeError):
                # Fallback to symmetric error
                err = float(mpv_err if isinstance(mpv_err, (int, float)) else np.mean(mpv_err))
                ax4.axvspan(mpv - err, mpv + err,
                          color=COLORS['orange'], alpha=0.2,
                          label='MPV Uncertainty')
                
        format_axis_labels(ax4, AXIS_LABELS['adc'], 'Probability')
        ax4.set_title('4. Parameter Space')
        ax4.legend(loc='upper right')
        
        # Add subplot labels
        add_subplot_label(ax1, 'a')
        add_subplot_label(ax2, 'b')
        add_subplot_label(ax3, 'c')
        add_subplot_label(ax4, 'd')
        
        fig.suptitle(f'Channel {channel}, Chip {chip} - Fit Analysis Steps', fontsize=14)
        fig.tight_layout()
        return fig
        
    def plot_error_analysis(self, channel, chip):
        """Create a plot explaining the error estimation procedure."""
        result = None
        for data in self.complete_data:
            if data['chip'] == chip and data['channel'] == channel:
                result = data
                break
                
        if result is None or result['status'] != 'success':
            return None
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=get_figure_dimensions('wide'))
        
        # 1. Show fit variations
        hist_data = result['reduced_hist_data']['fit']
        bin_centers = hist_data['bin_mids']
        counts = hist_data['bin_counts']
        errors = np.sqrt(counts)
        
        ax1.errorbar(bin_centers, counts, yerr=errors, fmt='o',
                    color=COLORS['blue'], label='Data',
                    markersize=4, elinewidth=1, capsize=2)
        
        # Plot several variations of the fit
        x_fit = result['langaus_fit']['x_fit']
        params = result['langaus_fit']['params']
        param_errs = result['langaus_fit']['param_errors']
        
        # Base fit
        y_base = result['langaus_fit']['y_fit']
        ax1.plot(x_fit, y_base, color=COLORS['red'],
                linestyle='-', label='Best Fit')
        
        # Variation 1: MPV + error
        # Handle parameter variations carefully
        mpv_err = float(param_errs[0] if isinstance(param_errs[0], (int, float)) else param_errs[0][0])
        
        # MPV + error
        y_up = landaupy_langauss.pdf(x_fit, params[0] + mpv_err, params[1], params[2])
        ax1.plot(x_fit, y_up, color=COLORS['green'],
                linestyle='--', label='MPV + σ')
        
        # MPV - error
        y_down = landaupy_langauss.pdf(x_fit, params[0] - mpv_err, params[1], params[2])
        ax1.plot(x_fit, y_down, color=COLORS['purple'],
                linestyle=':', label='MPV - σ')
        
        format_axis_labels(ax1, AXIS_LABELS['adc'], AXIS_LABELS['counts'])
        ax1.set_title('Parameter Variations')
        ax1.legend(loc='upper right')
        
        # 2. Get MPV and errors from bootstrap results
        mpv = result['bootstrap_results']['mpv']
        mpv_errs = result['bootstrap_results']['mpv_err_estimate']
        err_low = float(mpv_errs[0][0] if isinstance(mpv_errs[0], (list, np.ndarray)) else mpv_errs[0])
        err_high = float(mpv_errs[1][0] if isinstance(mpv_errs[1], (list, np.ndarray)) else mpv_errs[1])

        # Generate x values around the MPV for plotting
        x_dense = np.linspace(max(0, mpv-50), mpv+50, 1000)
        y_dense = landaupy_langauss.pdf(x_dense, 
                                      result['langaus_fit']['params'][0],
                                      result['langaus_fit']['params'][1],
                                      result['langaus_fit']['params'][2])
        
        # Plot the function
        ax2.plot(x_dense, y_dense, color=COLORS['red'],
                label='Langaus PDF')
        
        # Add MPV and asymmetric uncertainty region
        ax2.axvspan(mpv - err_low, mpv + err_high,
                   color=COLORS['orange'], alpha=0.2,
                   label=f'MPV = {mpv:.1f} +{err_high:.1f}/-{err_low:.1f}')
                          
        ax2.axvline(mpv, color=COLORS['orange'], linestyle='--')
        
        format_axis_labels(ax2, AXIS_LABELS['adc'], 'Probability')
        ax2.set_title('Maximum Finding')
        ax2.legend(loc='upper right')
        
        # Add subplot labels
        add_subplot_label(ax1, 'a')
        add_subplot_label(ax2, 'b')
        
        fig.suptitle(f'Channel {channel}, Chip {chip} - Error Analysis', fontsize=14)
        fig.tight_layout()
        return fig
