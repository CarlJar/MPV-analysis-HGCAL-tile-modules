"""
Configuration for thesis plotting, focused on seaborn styling.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set up seaborn style
sns.set_theme(style="whitegrid", context="paper")
sns.set_style("whitegrid", {
    'axes.grid': True,
    'grid.linestyle': ':',
    'grid.alpha': 0.5
})

# Use seaborn's color palette with high contrast and color-blind friendly colors
base_colors = sns.color_palette("colorblind")
COLORS = {
    # Basic plot elements
    'hist': base_colors[7],          # Gray for histogram background
    'data': base_colors[0],          # Blue for data points
    
    # Fitting colors
    'gauss': base_colors[2],         # Green for Gaussian fit
    'langaus': base_colors[1],       # Red for Landau-Gauss fit
    'mpv': base_colors[4],           # Orange for MPV lines
    'error_band': base_colors[3],    # Purple for error bands
    
    # General purpose colors
    'blue': base_colors[0],
    'red': base_colors[1],
    'green': base_colors[2],
    'purple': base_colors[3],
    'orange': base_colors[4],
    'yellow': base_colors[5],
    'gray': base_colors[7],
    
    # Secondary elements
    'grid': base_colors[7],          # Gray for grid lines
    'fit_langaus': base_colors[0],   # Blue for Landau-Gauss fit
    'mpv': base_colors[1],           # Red for MPV line/band
}

# Standard axis labels with LaTeX formatting
AXIS_LABELS = {
    'adc': 'ADC Value',
    'counts': 'Entries',
    'mpv': 'Most Probable Value (ADC)',
    'sigma': r'$\sigma$ (ADC)',
    'chi2': r'$\chi^2/\mathrm{ndf}$',
    'prob': 'Probability',
    'channel': 'Channel',
    'chip': 'Chip'
}

# Figure dimensions (in inches)
FIGURE_DIMENSIONS = {
    'square': (10, 10),      # For 2x2 subplots
    'wide': (12, 5),        # For 1x2 subplots
    'tall': (6, 12),        # For 2x1 subplots
    'single': (8, 6)        # For single plots
}

def format_axis_labels(ax, xlabel, ylabel, fontsize=12):
    """Format axis labels with consistent styling."""
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.tick_params(axis='both', which='major', labelsize=fontsize-2)

def add_subplot_label(ax, label, title=None, fontsize=12):
    """Add subplot label (a, b, c, etc.) and optional title in a consistent position."""
    # Add the subplot label (A, B, C, etc.)
    ax.text(-0.1, 1.1, f'({label})', transform=ax.transAxes,
            fontsize=fontsize, fontweight='bold')
    # Add the title if provided
    if title:
        ax.set_title(title, fontsize=fontsize)

def get_figure_dimensions(style):
    """Get figure dimensions based on style."""
    return FIGURE_DIMENSIONS.get(style, FIGURE_DIMENSIONS['single'])

# Helper functions for common plot elements
def add_error_band(ax, x, y, yerr, color, alpha=0.2, label=None):
    """Add an error band to a plot."""
    ax.fill_between(x, y-yerr, y+yerr, color=color, alpha=alpha, label=label)

def format_legend(ax, ncol=1, fontsize=10, framealpha=0.8):
    """Format legend with consistent styling."""
    ax.legend(ncol=ncol, fontsize=fontsize, framealpha=framealpha)

def setup_plot_style(use_tex=True):
    """Set up the global plotting style."""
    # Set seaborn context and style
    sns.set_context("paper", font_scale=1.2)
    sns.set_style("whitegrid", {
        'axes.grid': True,
        'grid.linestyle': ':',
        'grid.alpha': 0.5
    })
    
    # Try to use TeX if available and requested
    if use_tex:
        try:
            plt.rcParams.update({
                "text.usetex": True,
                "font.family": "serif",
                "font.serif": ["Computer Modern"]
            })
        except:
            print("TeX not available, using standard fonts")
    
    # General style settings
    plt.rcParams.update({
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'figure.autolayout': True,
        'axes.labelsize': 12,
        'axes.titlesize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'legend.framealpha': 0.9,
        'legend.edgecolor': '0.8',
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
        'errorbar.capsize': 3,
        # Additional customizations
        'axes.facecolor': 'white',
        'axes.edgecolor': '.8',
        'xtick.color': '.8',
        'ytick.color': '.8',
        'grid.alpha': 0.3
    })
