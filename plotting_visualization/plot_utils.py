import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
from pathlib import Path


class AnalysisPlotter:
    """
    Utility class for plotting analysis results from saved data files.
    """
    
    def __init__(self, data_path):
        """
        Initialize the plotter with data from saved analysis results.
        
        Parameters:
        - data_path: Path to the saved analysis results (without extension)
        """
        self.data_path = data_path
        self.complete_data = None
        self.simplified_data = None
        
        data_path = Path(data_path)
        
        # Try different possible file paths for complete data
        complete_paths = [
            str(data_path) + '_complete_results.pkl',
            str(data_path) + '.pkl',
            str(data_path) + '/complete_results.pkl'  # Added this format
        ]
        for path in complete_paths:
            try:
                with open(path, 'rb') as f:
                    self.complete_data = pickle.load(f)
                    break
            except FileNotFoundError:
                continue
        
        if self.complete_data is None:
            print(f"Complete data file not found in: {data_path}")
            print(f"Tried paths: {complete_paths}")
        
        # Try different possible paths for simplified data
        simplified_paths = [
            str(data_path) + '_simplified_results.h5',
            str(data_path) + '.h5',
            str(data_path) + '/simplified_results.h5'  # Added this format
        ]
        for path in simplified_paths:
            try:
                self.simplified_data = pd.read_hdf(path, key='fit_results')
                break
            except (FileNotFoundError, KeyError):
                continue
        
        if self.simplified_data is None:
            print(f"Simplified data file not found in: {data_path}")
            print(f"Tried paths: {simplified_paths}")
    
    def plot_single_channel(self, channel, chip=None, save_path=None, show_components=True, 
                           error_bars=True, show_histogram=True, show_only_fit_region=False):
        """
        Plot analysis results for a single channel.
        
        Parameters:
        - channel: Channel number to plot
        - chip: Chip number (if None, will search all data)
        - save_path: Path to save the plot (optional)
        - show_components: Whether to show individual fit components
        - error_bars: Whether to show Poisson error bars on data points
        - show_histogram: Whether to show histogram outline
        - show_only_fit_region: If True, only shows data points with error bars in the fit region
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find the analysis result for this channel
        result = None
        matching_results = []
        
        for data in self.complete_data:
            if data is not None and data['channel'] == channel:
                matching_results.append(data)
                # If chip is specified, make sure it matches
                if chip is not None and data.get('chip') != chip:
                    continue
                result = data
                break
        
        if result is None:
            if len(matching_results) > 1 and chip is None:
                chips = [str(r.get('chip', 'unknown')) for r in matching_results]
                print(f"Channel {channel} found on multiple chips: {', '.join(chips)}")
                print(f"Please specify chip parameter: plot_single_channel({channel}, chip=X)")
            else:
                print(f"No data found for channel {channel}" + (f" on chip {chip}" if chip else ""))
            return None
        
        if result['status'] != 'success':
            print(f"Channel {channel} analysis was not successful: {result['status']}")
            return None
        
        # Extract configuration
        config = result.get('config', {})
        use_tailcut = config.get('use_tailcut', False)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot full histogram as points with Poisson error bars
        hist_data = result['hist_data']
        poisson_errors = np.sqrt(hist_data['bin_counts'])
        
        # Get fit region
        reduced_fit = result['reduced_hist_data']['fit']
        fit_region_mask = ((hist_data['bin_mids'] >= reduced_fit['bin_edges'][0]) & 
                          (hist_data['bin_mids'] <= reduced_fit['bin_edges'][-1]))
        
        # Show fit region with appropriate color and label based on tail cut configuration
        region_color = 'red' if use_tailcut else 'blue'
        region_label = 'Fit Region (with tail cut)' if use_tailcut else 'Fit Region'
        ax.axvspan(reduced_fit['bin_edges'][0], reduced_fit['bin_edges'][-1],
                  alpha=0.15, color=region_color, label=region_label)
        
        if show_histogram:
            # Plot histogram as gray line
            ax.hist(hist_data['bin_mids'], 
                    bins=hist_data['bin_edges'],
                    weights=hist_data['bin_counts'],
                    facecolor='none', 
                    edgecolor='gray', 
                    alpha=0.4,
                    label='Histogram outline',
                    histtype='step',
                    linewidth=1)
        
        if error_bars:
            if show_only_fit_region:
                # Show only points in fit region with error bars
                ax.errorbar(hist_data['bin_mids'][fit_region_mask], 
                           hist_data['bin_counts'][fit_region_mask],
                           yerr=poisson_errors[fit_region_mask],
                           fmt='o', 
                           color='black',
                           markersize=3,
                           capsize=2,
                           alpha=0.7,
                           label='Data (fit region)')
            else:
                # Show all points with error bars
                ax.errorbar(hist_data['bin_mids'], 
                           hist_data['bin_counts'],
                           yerr=poisson_errors,
                           fmt='o', 
                           color='black',
                           markersize=3,
                           capsize=2,
                           alpha=0.7,
                           label='Data with Poisson errors')
        
        if show_components:
            # Plot reduced histograms as points with error bars
            reduced_fit = result['reduced_hist_data']['fit']
            reduced_fit_errors = np.sqrt(reduced_fit['bin_counts'])
            
            ax.errorbar(reduced_fit['bin_mids'],
                       reduced_fit['bin_counts'],
                       yerr=reduced_fit_errors,
                       fmt='s',
                       color='red',
                       markersize=4,
                       capsize=2,
                       alpha=0.8,
                       label='Reduced Data (Fit Region)')
            
            reduced_gauss = result['reduced_hist_data']['gauss']
            reduced_gauss_errors = np.sqrt(reduced_gauss['bin_counts'])
            
            ax.errorbar(reduced_gauss['bin_mids'],
                       reduced_gauss['bin_counts'],
                       yerr=reduced_gauss_errors,
                       fmt='^',
                       color='blue',
                       markersize=4,
                       capsize=2,
                       alpha=0.6,
                       label='Reduced Data (Gauss Region)')
        
        # Plot Gaussian fit
        gauss_fit = result['gauss_fit']
        ax.plot(gauss_fit['x_fit'], gauss_fit['y_fit'],
                label='Gauss Fit', color='darkgreen', linestyle='--')
        
        # Plot Langaus fits
        langaus_fit = result['langaus_fit']
        ax.plot(langaus_fit['x_fit'], langaus_fit['y_guess'],
                label='Langaus Guess', color='orange', linestyle='--')
                
        # Plot Langaus fit only in the fit region
        fit_mask = ((langaus_fit['x_fit'] >= reduced_fit['bin_edges'][0]) & 
                   (langaus_fit['x_fit'] <= reduced_fit['bin_edges'][-1]))
        ax.plot(langaus_fit['x_fit'][fit_mask], langaus_fit['y_fit'][fit_mask],
                label='Langaus Fit', color='red', linewidth=2)
        
        # Plot bootstrap results
        bootstrap = result['bootstrap_results']
        mpv = bootstrap['mpv']
        mpv_err_estimate = bootstrap['mpv_err_estimate']
        mpv_edges = bootstrap['mpv_edges']
        
        ax.vlines(mpv, 0, max(hist_data['bin_counts']), 
                 color='blue', linestyle='--', label='MPV')
        ax.vlines(mpv_edges[0], 0, max(hist_data['bin_counts']), 
                 color='orange', linestyle='--', alpha=0.7)
        ax.vlines(mpv_edges[1], 0, max(hist_data['bin_counts']), 
                 color='orange', linestyle='--', alpha=0.7)
        
        ax.errorbar(mpv, max(hist_data['bin_counts']),
                   xerr=mpv_err_estimate,
                   fmt='.', color='blue', capsize=5)
        
        # Set labels and title
        title = f"Channel {channel}"
        if chip is not None:
            title += f", Chip {chip}"
        if 'config' in result:
            config = result['config']
            if config.get('use_tailcut', False):
                title += f"\nTail Cut: Fit {config.get('fit_gradient_threshold', 0.1):.1f}, Gauss {config.get('gauss_gradient_threshold', 0.5):.1f}"
            else:
                title += "\nNo Tail Cut"
        ax.set_title(title)
        
        ax.set_xlabel('ADC Amplitude')
        ax.set_ylabel('Counts')
        ax.set_xlim(0, 400)
        
        gof = langaus_fit['gof']
        ax.set_title(f'MPV={mpv:.2f}, Ch: {channel}, GoF: {gof:.2f}', fontsize=12)
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, ax
    
    def plot_chip_summary(self, chip, channels=None, save_path=None, plot_dim=None):
        """
        Plot summary for all channels in a chip.
        
        Parameters:
        - chip: Chip number
        - channels: List of channels to plot (if None, plots all available)
        - save_path: Path to save the plot
        - plot_dim: Tuple (rows, cols) for subplot arrangement
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find all successful results for this chip
        chip_results = []
        for data in self.complete_data:
            if (data is not None and 
                data.get('chip') == chip and 
                data['status'] == 'success'):
                chip_results.append(data)
        
        if not chip_results:
            print(f"No successful results found for chip {chip}")
            return None
        
        # Filter by channels if specified
        if channels is not None:
            chip_results = [r for r in chip_results if r['channel'] in channels]
        
        n_channels = len(chip_results)
        if n_channels == 0:
            print("No matching channels found")
            return None
        
        # Determine plot dimensions
        if plot_dim is None:
            cols = int(np.ceil(np.sqrt(n_channels)))
            rows = int(np.ceil(n_channels / cols))
            plot_dim = (rows, cols)
        
        # Create figure
        fig_width = plot_dim[1] * 6
        fig_height = plot_dim[0] * 3
        fig, axs = plt.subplots(*plot_dim, figsize=(fig_width, fig_height))
        
        # Ensure axs is always iterable
        if isinstance(axs, plt.Axes):
            axs = [axs]
        elif isinstance(axs, np.ndarray):
            axs = axs.flatten()
        
        # Plot each channel
        for i, result in enumerate(chip_results):
            if i >= len(axs):
                break
            
            ax = axs[i]
            channel = result['channel']
            
            # Plot histogram as points with error bars for chip summary
            hist_data = result['hist_data']
            poisson_errors = np.sqrt(hist_data['bin_counts'])
            
            # Only plot every nth point to avoid overcrowding in small subplots
            step = max(1, len(hist_data['bin_mids']) // 20)  # Show ~20 points max
            
            ax.errorbar(hist_data['bin_mids'][::step],
                       hist_data['bin_counts'][::step],
                       yerr=poisson_errors[::step],
                       fmt='o',
                       color='black',
                       markersize=2,
                       capsize=1,
                       alpha=0.6)
            
            # Plot reduced histogram for fit as different markers
            reduced_fit = result['reduced_hist_data']['fit']
            reduced_errors = np.sqrt(reduced_fit['bin_counts'])
            
            ax.errorbar(reduced_fit['bin_mids'],
                       reduced_fit['bin_counts'],
                       yerr=reduced_errors,
                       fmt='s',
                       color='red',
                       markersize=3,
                       capsize=1,
                       alpha=0.7)
            
            # Plot fits
            gauss_fit = result['gauss_fit']
            ax.plot(gauss_fit['x_fit'], gauss_fit['y_fit'],
                    color='darkgreen', linestyle='--', alpha=0.7)
            
            langaus_fit = result['langaus_fit']
            ax.plot(langaus_fit['x_fit'], langaus_fit['y_fit'],
                    color='red')
            
            # Plot MPV
            bootstrap = result['bootstrap_results']
            mpv = bootstrap['mpv']
            ax.vlines(mpv, 0, max(hist_data['bin_counts']),
                     color='blue', linestyle='--')
            
            # Set limits and title
            ax.set_xlim(0, 400)
            gof = langaus_fit['gof']
            ax.set_title(f'MPV={mpv:.2f}, Ch: {channel}, GoF: {gof:.1f}', fontsize=8)
        
        # Hide unused subplots
        for i in range(len(chip_results), len(axs)):
            axs[i].set_visible(False)
        
        # Add overall title and labels
        fig.suptitle(f'Chip {chip}', fontsize=16)
        fig.text(0.5, 0.04, 'ADC Amplitude', ha='center', fontsize=12)
        fig.text(0.04, 0.5, 'Counts', va='center', rotation='vertical', fontsize=12)
        
        plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, axs
    
    def plot_mpv_summary(self, save_path=None):
        """
        Plot summary of MPV values across all channels.
        """
        if self.simplified_data is None:
            print("No simplified data available for MPV summary")
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # MPV vs Channel
        ax1.errorbar(self.simplified_data['channel'], 
                    self.simplified_data['bootstrap_mpv'],
                    yerr=[self.simplified_data['bootstrap_mpv_lower_err'],
                          self.simplified_data['bootstrap_mpv_upper_err']],
                    fmt='o', capsize=3)
        ax1.set_xlabel('Channel')
        ax1.set_ylabel('MPV [ADC]')
        ax1.set_title('MPV vs Channel')
        ax1.grid(True, alpha=0.3)
        
        # MPV distribution
        ax2.hist(self.simplified_data['bootstrap_mpv'], bins=20, alpha=0.7, edgecolor='black')
        ax2.set_xlabel('MPV [ADC]')
        ax2.set_ylabel('Number of Channels')
        ax2.set_title('MPV Distribution')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, (ax1, ax2)
    
    def get_summary_table(self):
        """
        Return a summary table of fit results.
        """
        if self.simplified_data is None:
            print("No simplified data available for summary table")
            return None
        
        summary = self.simplified_data.copy()
        summary['mpv_rel_error'] = (summary['bootstrap_mpv_upper_err'] + 
                                   summary['bootstrap_mpv_lower_err']) / (2 * summary['bootstrap_mpv'])
        
        print("\nAnalysis Summary:")
        print(f"Total channels analyzed: {len(summary)}")
        print(f"Mean MPV: {summary['bootstrap_mpv'].mean():.2f} ± {summary['bootstrap_mpv'].std():.2f}")
        print(f"MPV range: {summary['bootstrap_mpv'].min():.2f} - {summary['bootstrap_mpv'].max():.2f}")
        print(f"Mean relative error: {summary['mpv_rel_error'].mean():.3f}")
        print(f"Mean GoF: {summary['gof'].mean():.2f}")
        
        return summary
    
    def plot_fit_comparison(self, channel, chip=None, save_path=None, show_only_fit_region=False):
        """
        Plot data vs fit with residuals subplot.
        
        Parameters:
        - channel: Channel number to plot
        - chip: Chip number (if None, will search all data)
        - save_path: Path to save the plot (optional)
        - show_only_fit_region: If True, only shows data points with error bars in the fit region
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find the analysis result for this channel
        result = None
        for data in self.complete_data:
            if data is not None and data['channel'] == channel:
                # If chip is specified, make sure it matches
                if chip is not None and data.get('chip') != chip:
                    continue
                result = data
                break
        
        if result is None:
            print(f"No data found for channel {channel}" + (f" on chip {chip}" if chip else ""))
            return None
        
        if result['status'] != 'success':
            print(f"Channel {channel} analysis was not successful: {result['status']}")
            return None
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), 
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # Top plot: Data and fit
        hist_data = result['hist_data']
        poisson_errors = np.sqrt(hist_data['bin_counts'])
        
        # Get fit region
        reduced_fit = result['reduced_hist_data']['fit']
        fit_region_mask = ((hist_data['bin_mids'] >= reduced_fit['bin_edges'][0]) & 
                          (hist_data['bin_mids'] <= reduced_fit['bin_edges'][-1]))
        
        # Always show the histogram outline
        ax1.hist(hist_data['bin_mids'], 
                bins=hist_data['bin_edges'],
                weights=hist_data['bin_counts'],
                facecolor='none', 
                edgecolor='gray', 
                alpha=0.4,
                histtype='step',
                linewidth=1,
                label='Histogram outline')
                
        # Plot data points with error bars
        if show_only_fit_region:
            # Only show points in fit region
            ax1.errorbar(hist_data['bin_mids'][fit_region_mask], 
                        hist_data['bin_counts'][fit_region_mask],
                        yerr=poisson_errors[fit_region_mask],
                        fmt='o', 
                        color='black',
                        markersize=4,
                        capsize=3,
                        alpha=0.8,
                        label='Data (fit region)')
        else:
            # Show all data points
            ax1.errorbar(hist_data['bin_mids'], 
                        hist_data['bin_counts'],
                        yerr=poisson_errors,
                        fmt='o', 
                        color='black',
                        markersize=4,
                        capsize=3,
                        alpha=0.8,
                        label='Data')
        
        # Plot fit curve in fit region only
        langaus_fit = result['langaus_fit']
        fit_mask = ((langaus_fit['x_fit'] >= reduced_fit['bin_edges'][0]) & 
                   (langaus_fit['x_fit'] <= reduced_fit['bin_edges'][-1]))
        ax1.plot(langaus_fit['x_fit'][fit_mask], langaus_fit['y_fit'][fit_mask],
                color='red', linewidth=2, label='Langaus Fit')
        
        # Plot fit region span
        ax1.axvspan(reduced_fit['bin_edges'][0], reduced_fit['bin_edges'][-1],
                   alpha=0.15, color='red', label='Fit Region')
        
        # MPV line
        bootstrap = result['bootstrap_results']
        mpv = bootstrap['mpv']
        ax1.axvline(mpv, color='blue', linestyle='--', linewidth=2, label=f'MPV = {mpv:.1f}')
        
        ax1.set_ylabel('Counts')
        ax1.set_xlim(0, 400)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Bottom plot: Residuals
        # Interpolate fit curve to data bin centers for residuals calculation
        fit_interp = np.interp(hist_data['bin_mids'], langaus_fit['x_fit'], langaus_fit['y_fit'])
        residuals = hist_data['bin_counts'] - fit_interp
        
        # Avoid divide by zero in residuals normalization
        valid_errors = poisson_errors.copy()
        valid_errors[valid_errors == 0] = 1  # Replace zeros with ones to avoid division by zero
        residuals_normalized = residuals / valid_errors
        
        # Plot residuals with same fit region highlighting as main plot
        if show_only_fit_region:
            ax2.errorbar(hist_data['bin_mids'][fit_region_mask], 
                        residuals_normalized[fit_region_mask],
                        yerr=np.ones_like(residuals_normalized[fit_region_mask]),
                        fmt='o', color='black', markersize=3, capsize=2, alpha=0.7)
        else:
            ax2.errorbar(hist_data['bin_mids'], 
                        residuals_normalized,
                        yerr=np.ones_like(residuals_normalized),
                        fmt='o', color='black', markersize=3, capsize=2, alpha=0.7)
        
        # Show fit region in residuals plot
        ax2.axvspan(reduced_fit['bin_edges'][0], reduced_fit['bin_edges'][-1],
                   alpha=0.15, color='red')
        
        ax2.axhline(0, color='red', linestyle='-', alpha=0.8)
        ax2.axhline(2, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(-2, color='red', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('ADC Amplitude')
        ax2.set_ylabel('Normalized\nResiduals')
        ax2.set_xlim(0, 400)
        ax2.grid(True, alpha=0.3)
        
        # Overall title
        gof = langaus_fit['gof']
        fig.suptitle(f'Channel {channel} - Fit Comparison (GoF: {gof:.2f})', fontsize=14)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, (ax1, ax2)

    def plot_channel_detailed(self, channel, chip=None, save_path=None):
        """
        Create a detailed multi-panel plot for a single channel showing:
        1. Full data with all fit components
        2. Fit region zoom
        3. Residuals
        4. Bootstrap distribution
        
        Parameters:
        - channel: Channel number to plot
        - chip: Chip number (if None, will search all data)
        - save_path: Path to save the plot (optional)
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find the analysis result for this channel
        result = None
        for data in self.complete_data:
            if data is not None and data['channel'] == channel:
                # If chip is specified, make sure it matches
                if chip is not None and data.get('chip') != chip:
                    continue
                result = data
                break
        
        if result is None:
            print(f"No data found for channel {channel}" + (f" on chip {chip}" if chip else ""))
            return None
        
        if result['status'] != 'success':
            print(f"Channel {channel} analysis was not successful: {result['status']}")
            return None
        
        # Create 2x2 subplot layout
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        hist_data = result['hist_data']
        poisson_errors = np.sqrt(hist_data['bin_counts'])
        
        # Panel 1: Full view with all components
        ax1.errorbar(hist_data['bin_mids'], hist_data['bin_counts'],
                    yerr=poisson_errors, fmt='o', color='black', markersize=2,
                    capsize=1, alpha=0.7, label='Data')
        
        # All fit components
        gauss_fit = result['gauss_fit']
        langaus_fit = result['langaus_fit']
        
        ax1.plot(gauss_fit['x_fit'], gauss_fit['y_fit'],
                '--', color='green', label='Gaussian Guess')
        ax1.plot(langaus_fit['x_fit'], langaus_fit['y_guess'],
                '--', color='orange', label='Langaus Guess')
        ax1.plot(langaus_fit['x_fit'], langaus_fit['y_fit'],
                '-', color='red', linewidth=2, label='Langaus Fit')
        
        bootstrap = result['bootstrap_results']
        mpv = bootstrap['mpv']
        ax1.axvline(mpv, color='blue', linestyle='--', label=f'MPV = {mpv:.1f}')
        
        ax1.set_xlabel('ADC Amplitude')
        ax1.set_ylabel('Counts')
        ax1.set_title('Full View with Fit Components')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Panel 2: Zoomed fit region
        reduced_fit = result['reduced_hist_data']['fit']
        fit_region_mask = ((hist_data['bin_mids'] >= reduced_fit['bin_edges'][0]) & 
                          (hist_data['bin_mids'] <= reduced_fit['bin_edges'][-1]))
        
        ax2.errorbar(hist_data['bin_mids'][fit_region_mask], 
                    hist_data['bin_counts'][fit_region_mask],
                    yerr=poisson_errors[fit_region_mask],
                    fmt='o', color='black', markersize=4, capsize=2, alpha=0.8)
        
        fit_mask = ((langaus_fit['x_fit'] >= reduced_fit['bin_edges'][0]) & 
                   (langaus_fit['x_fit'] <= reduced_fit['bin_edges'][-1]))
        ax2.plot(langaus_fit['x_fit'][fit_mask], langaus_fit['y_fit'][fit_mask],
                '-', color='red', linewidth=2, label='Langaus Fit')
        
        ax2.set_xlabel('ADC Amplitude')
        ax2.set_ylabel('Counts')
        ax2.set_title('Fit Region (Zoomed)')
        ax2.grid(True, alpha=0.3)
        
        # Panel 3: Residuals
        fit_interp = np.interp(hist_data['bin_mids'], langaus_fit['x_fit'], langaus_fit['y_fit'])
        residuals = hist_data['bin_counts'] - fit_interp
        
        # Avoid divide by zero in residuals normalization
        valid_errors = poisson_errors.copy()
        valid_errors[valid_errors == 0] = 1  # Replace zeros with ones to avoid division by zero
        residuals_normalized = residuals / valid_errors
        
        ax3.errorbar(hist_data['bin_mids'], residuals_normalized,
                    yerr=np.ones_like(residuals_normalized),
                    fmt='o', color='black', markersize=3, capsize=2, alpha=0.7)
        ax3.axhline(0, color='red', linestyle='-')
        ax3.axhline(2, color='red', linestyle='--', alpha=0.5)
        ax3.axhline(-2, color='red', linestyle='--', alpha=0.5)
        
        ax3.set_xlabel('ADC Amplitude')
        ax3.set_ylabel('Normalized Residuals')
        ax3.set_title('Fit Residuals')
        ax3.grid(True, alpha=0.3)
        
        # Panel 4: Bootstrap results
        bootstrap_all = bootstrap['all_results']
        mpv_values = [res[0] for res in bootstrap_all]
        
        ax4.hist(mpv_values, bins=20, alpha=0.7, color='blue', edgecolor='black')
        ax4.axvline(mpv, color='red', linestyle='--', linewidth=2, 
                   label=f'Mean MPV = {mpv:.1f}')
        
        mpv_err_estimate = bootstrap['mpv_err_estimate']
        ax4.axvline(mpv - mpv_err_estimate[0][0], color='orange', linestyle='--', alpha=0.7)
        ax4.axvline(mpv + mpv_err_estimate[1][0], color='orange', linestyle='--', alpha=0.7)
        
        ax4.set_xlabel('MPV Value')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Bootstrap MPV Distribution')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Overall title
        gof = langaus_fit['gof']
        fig.suptitle(f'Detailed Analysis - Channel {channel} (GoF: {gof:.2f})', fontsize=16)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, ((ax1, ax2), (ax3, ax4))

    def plot_gradient_analysis(self, channel, chip=None, save_path=None):
        """
        Plot gradient analysis for a single channel, showing the histogram and its gradient.
        
        Parameters:
        - channel: Channel number to plot
        - chip: Chip number (if None, will search all data)
        - save_path: Path to save the plot (optional)
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find the analysis result for this channel
        result = None
        for data in self.complete_data:
            if data is not None and data['channel'] == channel:
                if chip is not None and data.get('chip') != chip:
                    continue
                result = data
                break
        
        if result is None or 'reduced_hist_data' not in result:
            print(f"No gradient data found for channel {channel}")
            return None
        
        # Get gradient data from both fit and gauss reductions
        fit_gradient = result['reduced_hist_data'].get('fit', {}).get('gradient_data')
        gauss_gradient = result['reduced_hist_data'].get('gauss', {}).get('gradient_data')
        
        if fit_gradient is None and gauss_gradient is None:
            print(f"No gradient data available for channel {channel}")
            return None
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot fit region gradient analysis
        if fit_gradient:
            self._plot_single_gradient(axes[0], fit_gradient, "Fit Region")
        
        # Plot Gauss region gradient analysis
        if gauss_gradient:
            self._plot_single_gradient(axes[1], gauss_gradient, "Gauss Region")
        
        # Overall title
        fig.suptitle(f'Gradient Analysis - Channel {channel}' + 
                    (f', Chip {chip}' if chip else ''), fontsize=16)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig, axes
    
    def _plot_single_gradient(self, axes, gradient_data, title_prefix):
        """Helper function to plot gradient analysis for a single region."""
        ax1, ax2 = axes
        
        # Plot histogram and smoothed data
        bin_mids = (gradient_data['bin_edges'][:-1] + gradient_data['bin_edges'][1:]) / 2
        ax1.hist(bin_mids, bins=gradient_data['bin_edges'],
                weights=gradient_data['hist'],
                facecolor='none', edgecolor='b', alpha=1,
                label='Data', histtype='step')
        
        ax1.plot(bin_mids, gradient_data['hist_smoothed'],
                label='Smoothed', linestyle='--', color='g')
        
        if gradient_data['tail_cut_index'] is not None:
            ax1.axvline(bin_mids[gradient_data['tail_cut_index']],
                       color='r', linestyle='--',
                       label='Tail Cut')
        
        ax1.set_ylabel('Counts')
        ax1.set_title(f'{title_prefix} - Histogram')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot gradient
        ax2.plot(bin_mids, gradient_data['first_derivative'],
                label='Gradient', color='b')
        
        if gradient_data['gradient_threshold_value'] is not None:
            ax2.axhline(gradient_data['gradient_threshold_value'],
                       color='g', linestyle='--',
                       label='Threshold')
        
        if gradient_data['tail_cut_index'] is not None:
            ax2.axvline(bin_mids[gradient_data['tail_cut_index']],
                       color='r', linestyle='--',
                       label='Cut Point')
        
        # Mark important points
        ax2.plot(bin_mids[gradient_data['maxium']], 
                gradient_data['first_derivative'][gradient_data['maxium']],
                'go', label='Maximum')
        
        ax2.plot(bin_mids[gradient_data['min_idx']], 
                gradient_data['first_derivative'][gradient_data['min_idx']],
                'ro', label='Minimum')
        
        boundary_idx = gradient_data['min_idx'] + gradient_data['boundary']
        ax2.plot(bin_mids[boundary_idx],
                gradient_data['first_derivative'][boundary_idx],
                'mo', label='Boundary')
        
        ax2.set_xlabel('ADC Amplitude')
        ax2.set_ylabel('Gradient')
        ax2.set_title(f'{title_prefix} - Gradient Analysis')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
    def debug_data_structure(self):
        """
        Debug function to show the structure of loaded data.
        """
        if self.complete_data is None:
            print("No complete data available")
            return
        
        print("="*50)
        print("DATA STRUCTURE DEBUG")
        print("="*50)
        
        print(f"Total analysis results: {len(self.complete_data)}")
        
        # Group by status
        status_counts = {}
        chip_channel_map = {}
        
        for data in self.complete_data:
            if data is None:
                continue
                
            status = data.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            chip = data.get('chip', 'unknown')
            channel = data.get('channel', 'unknown')
            
            if chip not in chip_channel_map:
                chip_channel_map[chip] = []
            chip_channel_map[chip].append(channel)
        
        print(f"\nStatus summary:")
        for status, count in status_counts.items():
            print(f"  {status}: {count}")
        
        print(f"\nChip-Channel mapping:")
        for chip, channels in chip_channel_map.items():
            channels_sorted = sorted(set(channels))
            print(f"  Chip {chip}: channels {channels_sorted}")
        
        # Show first few successful results
        successful_results = [r for r in self.complete_data if r and r['status'] == 'success']
        print(f"\nFirst 5 successful results:")
        for i, result in enumerate(successful_results[:5]):
            chip = result.get('chip', 'N/A')
            channel = result.get('channel', 'N/A')
            mpv = result.get('bootstrap_results', {}).get('mpv', 'N/A')
            print(f"  {i+1}. Chip {chip}, Channel {channel}, MPV: {mpv}")
        
        print("="*50)
        
    def plot_all_channels_for_chip(self, chip, output_dir=None, plot_type='standard', 
                                 show_only_fit_region=True, save_plots=True):
        """
        Plot all channels for a specific chip as individual plots.
        
        Parameters:
        - chip: Chip number
        - output_dir: Directory to save plots (required if save_plots=True)
        - plot_type: Type of plot ('standard', 'detailed', 'comparison')
        - show_only_fit_region: If True, only shows data points with error bars in the fit region
        - save_plots: Whether to save plots
        
        Returns:
        - list of successful channel plots
        """
        if self.complete_data is None:
            print("No complete data available for plotting")
            return None
        
        # Find all successful results for this chip
        chip_results = []
        for data in self.complete_data:
            if (data is not None and 
                data.get('chip') == chip and 
                data['status'] == 'success'):
                chip_results.append(data)
        
        if not chip_results:
            print(f"No successful results found for chip {chip}")
            return None
        
        # Sort results by channel
        chip_results.sort(key=lambda x: x['channel'])
        
        # Create output directory if needed
        if save_plots and output_dir is None:
            print("Output directory is required when save_plots=True")
            save_plots = False
        
        if save_plots:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
        successful_plots = []
        
        # Plot each channel individually
        for result in chip_results:
            channel = result['channel']
            save_path = None
            
            if save_plots:
                if plot_type == 'detailed':
                    save_path = f"{output_dir}/chip{chip}_channel{channel}_detailed.png"
                elif plot_type == 'comparison':
                    save_path = f"{output_dir}/chip{chip}_channel{channel}_comparison.png"
                else:  # standard
                    save_path = f"{output_dir}/chip{chip}_channel{channel}.png"
            
            try:
                if plot_type == 'detailed':
                    fig, axs = self.plot_channel_detailed(
                        channel,
                        chip=chip,
                        save_path=save_path
                    )
                elif plot_type == 'comparison':
                    fig, axs = self.plot_fit_comparison(
                        channel,
                        chip=chip,
                        save_path=save_path,
                        show_only_fit_region=show_only_fit_region
                    )
                else:  # standard
                    fig, ax = self.plot_single_channel(
                        channel,
                        chip=chip,
                        save_path=save_path,
                        show_only_fit_region=show_only_fit_region
                    )
                
                if fig:
                    plt.close(fig)  # Close figure to avoid memory issues
                    successful_plots.append(channel)
                    print(f"Plotted chip {chip}, channel {channel}")
            except Exception as e:
                print(f"Error plotting chip {chip}, channel {channel}: {str(e)}")
        
        print(f"Successfully plotted {len(successful_plots)} channels for chip {chip}")
        return successful_plots

def plot_from_saved_data(data_path, chip=None, channel=None, save_plots=True, output_dir=None, 
                        plot_type='standard', error_bars=True, show_only_fit_region=False,
                        plot_all_channels=False):
    """
    Convenience function to create plots from saved analysis data.
    
    Parameters:
    - data_path: Path to saved analysis results (without extension)
    - chip: Specific chip to plot (if None, plots all)
    - channel: Specific channel to plot (if None, plots all in chip)
    - save_plots: Whether to save plots
    - output_dir: Directory to save plots (if None, uses same as data_path)
    - plot_type: Type of plot ('standard', 'detailed', 'comparison')
    - error_bars: Whether to show Poisson error bars
    - show_only_fit_region: If True, only shows data points with error bars in the fit region
    - plot_all_channels: If True and chip is specified, plots all channels as individual plots
    
    Examples:
    # Basic chip summary
    plot_from_saved_data('path/to/results', chip=3)
    
    # Single channel with only fit region points and comparison view
    plot_from_saved_data('path/to/results', chip=3, channel=39, 
                         plot_type='comparison', show_only_fit_region=True)
    
    # Plot all channels for a chip as individual plots
    plot_from_saved_data('path/to/results', chip=3, plot_all_channels=True, 
                         plot_type='standard', show_only_fit_region=True)
    """
    plotter = AnalysisPlotter(data_path)
    
    # Debug data structure if no specific plotting requested
    if chip is None and channel is None:
        print("Loading data structure...")
        plotter.debug_data_structure()
        print("\nUse specific chip/channel parameters for targeted plotting.")
        print("Example: plot_from_saved_data(data_path, chip=2, channel=0)")
    
    if output_dir is None:
        output_dir = Path(data_path).parent
    
    # Plot all channels in a chip as individual plots
    if chip is not None and plot_all_channels:
        plotter.plot_all_channels_for_chip(
            chip, 
            output_dir=f"{output_dir}/chip_{chip}_channels",
            plot_type=plot_type,
            show_only_fit_region=show_only_fit_region,
            save_plots=save_plots
        )
        return plotter
    
    # Plot a single channel with the specified type
    elif channel is not None:
        save_path_base = f"{output_dir}/channel_{channel}" if save_plots else None
        
        if plot_type == 'detailed':
            fig, axs = plotter.plot_channel_detailed(
                channel, 
                chip=chip,
                save_path=f"{save_path_base}_detailed.png" if save_plots else None
            )
        elif plot_type == 'comparison':
            fig, axs = plotter.plot_fit_comparison(
                channel,
                chip=chip,
                save_path=f"{save_path_base}_comparison.png" if save_plots else None,
                show_only_fit_region=show_only_fit_region
            )
        else:  # standard
            fig, ax = plotter.plot_single_channel(
                channel, 
                chip=chip,
                save_path=f"{save_path_base}.png" if save_plots else None,
                error_bars=error_bars,
                show_only_fit_region=show_only_fit_region
            )
        
        if fig:
            plt.show()
    
    # Plot a chip summary
    elif chip is not None:
        fig, axs = plotter.plot_chip_summary(
            chip,
            save_path=f"{output_dir}/chip_{chip}_summary.png" if save_plots else None
        )
        if fig:
            plt.show()
    
    # Plot overall summary
    else:
        fig, axs = plotter.plot_mpv_summary(
            save_path=f"{output_dir}/mpv_summary.png" if save_plots else None
        )
        if fig:
            plt.show()
        
        # Print summary table
        plotter.get_summary_table()
    
    return plotter


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python plot_utils.py <data_path> [chip] [channel] [plot_type]")
        print("  plot_type options: standard, detailed, comparison")
        print("Examples:")
        print("  python plot_utils.py /path/to/results")
        print("  python plot_utils.py /path/to/results 2")
        print("  python plot_utils.py /path/to/results 2 0")
        print("  python plot_utils.py /path/to/results 2 0 detailed")
        sys.exit(1)
    
    data_path = sys.argv[1]
    chip = int(sys.argv[2]) if len(sys.argv) > 2 else None
    channel = int(sys.argv[3]) if len(sys.argv) > 3 else None
    plot_type = sys.argv[4] if len(sys.argv) > 4 else 'standard'
    
    plot_from_saved_data(data_path, chip=chip, channel=channel, plot_type=plot_type)
