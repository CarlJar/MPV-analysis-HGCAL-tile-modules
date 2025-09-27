"""
Generate thesis-quality plots using seaborn styling
"""
import matplotlib.pyplot as plt
import seaborn as sns
from thesis_plotting_config import setup_plot_style
from enhanced_plotter import ThesisPlotter
import os

def save_figure(figure, name, output_dir="thesis_figures"):
    """Save figure in both PDF and PNG format with proper DPI."""
    # Handle case where figure might be a tuple (fig, ax)
    fig = figure[0] if isinstance(figure, tuple) else figure
    
    # Create full output directory path including any subdirectories in the name
    full_path = os.path.join(output_dir, os.path.dirname(name))
    os.makedirs(full_path, exist_ok=True)
    
    # Save as PDF (vector format for the thesis)
    pdf_path = os.path.join(output_dir, f"{name}.pdf")
    fig.savefig(pdf_path, dpi=300, bbox_inches='tight')
    
    # Save as PNG (for presentations and quick viewing)
    png_path = os.path.join(output_dir, f"{name}.png")
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    
    print(f"Saved: {pdf_path}")
    print(f"       {png_path}")
    plt.close(fig)

def main():
    # Initialize plotter with analysis results for different runs
    base_path = "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis"
    runs = {
        "150MeV": f"{base_path}/2024-09-16_22-34-48_beamrun_muonss_150",
        "250MeV": f"{base_path}/2024-09-19_15-11-45_beamrun_muon_250",
        "250MeV_magnet": f"{base_path}/2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
    }
    
    # Representative channels for main text, showing different cases
    main_examples = {
        'A5': {'chip': 2, 'channel': 3, 'desc': 'typical'},      # Good signal
        'B12_0': {'chip': 3, 'channel': 29, 'desc': 'challenge'}, # Challenging case
        'B12_1': {'chip': 4, 'channel': 1, 'desc': 'standard'}   # Standard case
    }
    
    # === Main Text Plots (Section 4) ===
    
    # Initialize plotter with first run
    plotter = ThesisPlotter(runs["150MeV"])
    
    # 1. Initial Gaussian Fit Examples (Section 4.3.2)
    for name, info in main_examples.items():
        fig = plotter.plot_fit_procedure(
            channel=info['channel'],
            chip=info['chip']
        )
        if fig:
            save_figure(fig, f"gaussian_fit_{name}_{info['desc']}")
    
    # 2. Final Landau-Gauss Fits (Section 4.3.3)
    for name, info in main_examples.items():
        fig = plotter.plot_error_analysis(
            channel=info['channel'],
            chip=info['chip']
        )
        if fig:
            save_figure(fig, f"landau_gauss_{name}_{info['desc']}")
    
    # === Appendix Plots ===
    
    # Define all active channels
    active_channels = {
        'A5': {
            'chip': 2,
            'channels': [0, 1, 2, 3, 4, 5, 23, 24, 28, 29, 30, 31, 36, 37]
        },
        'B12_0': {
            'chip': 3,
            'channels': [9, 11, 29, 35, 38, 39, 49, 60, 66, 67]
        },
        'B12_1': {
            'chip': 4,
            'channels': [0, 1, 6, 7]
        }
    }
    
    # 1. Comprehensive Landau-Gauss Fits
    print("\nGenerating appendix plots...")
    for tile_name, info in active_channels.items():
        print(f"\nProcessing {tile_name}...")
        for channel in info['channels']:
            # For appendix: simplified plots focusing on fit quality
            fig = plotter.plot_single_channel(
                channel=channel,
                chip=info['chip'],
                error_bars=True,
                show_components=False,  # Don't show individual components
                show_only_fit_region=True  # Focus on the fit region
            )
            if fig:
                # Create appendix subdirectory for fits
                save_figure(fig, f"appendix/landau_gauss_fits/{tile_name}/channel_{channel}")
                # No need for explicit plt.close as save_figure handles it
    
    # 2. Optional: Fit Residuals
    # Will be implemented if needed
    
    # 3. Optional: Histogram Binning Study
    # Will be implemented if needed

if __name__ == "__main__":
    # Set up the plotting style
    setup_plot_style(use_tex=False)  # Using standard fonts until LaTeX is properly configured
    
    # Run the main plotting routine
    main()
