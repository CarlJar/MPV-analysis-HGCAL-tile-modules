import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from plotting_visualization.plot_utils import plot_from_saved_data, AnalysisPlotter
import argparse
import sys
import os
import matplotlib.pyplot as plt

# Define run mapping dictionary
RUN_MAP = {
    1: "2024-09-16_22-34-48_beamrun_muonss_150",
    2: "2024-09-19_15-11-45_beamrun_muon_250",
    3: "2024-09-21_12-29-11_beamrun_muon_250_magnetOn"
}

# Set up argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(description='Plot analysis results for selected runs')
    parser.add_argument('--runs', nargs='+', type=int, default=[1],
                        help='Run numbers to process (1=150MeV, 2=250MeV, 3=250MeV+magnet)')
    parser.add_argument('--chips', nargs='+', type=int, default=[2, 3, 4],
                        help='Chip numbers to plot (default: 2 3 4)')
    parser.add_argument('--plot-type', choices=['standard', 'comparison'], default='both',
                        help='Type of plot to generate (standard, comparison, or both)')
    parser.add_argument('--fit-region-only', action='store_true',
                        help='Show only fit region in plots')
    parser.add_argument('--list-runs', action='store_true',
                        help='List available runs and exit')
    parser.add_argument('--summary', action='store_true',
                        help='Generate chip summary plots showing all channels in one figure')
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

# Base path for data
base_path_template = '/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis/{}/analysis_results'

# Process each selected run
for run_number in args.runs:
    run = RUN_MAP[run_number]
    base_path = base_path_template.format(run)
    
    print(f"\n{'='*60}")
    print(f"Plotting for run {run_number}: {run}")
    print(f"{'='*60}\n")
    
    # Process each selected chip
    for chip in args.chips:
        print(f"Processing chip {chip}...")
        
        # Generate chip summary plot if requested
        if args.summary:
            print(f"  Generating chip summary plot...")
            plotter = AnalysisPlotter(base_path)
            fig, axs = plotter.plot_chip_summary(chip)
            if fig:
                summary_dir = f"{base_path}/summary_plots"
                os.makedirs(summary_dir, exist_ok=True)
                save_path = f"{summary_dir}/chip{chip}_summary.png"
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                print(f"  Saved chip summary plot to: {save_path}")
        
        # Determine which plot types to generate
        plot_types = []
        if args.plot_type == 'both':
            plot_types = ['standard', 'comparison']
        else:
            plot_types = [args.plot_type]
        
        # Generate plots for each type
        for plot_type in plot_types:
            print(f"  Generating {plot_type} plots...")
            plot_from_saved_data(
                base_path, 
                chip=chip, 
                plot_all_channels=True, 
                plot_type=plot_type, 
                show_only_fit_region=args.fit_region_only
            )
        
        # Generate summary plot if requested
        if args.summary:
            print("  Generating summary plot...")
            plot_from_saved_data(
                base_path, 
                chip=chip, 
                plot_all_channels=True, 
                plot_type='summary', 
                show_only_fit_region=args.fit_region_only
            )

print("\nAll plotting complete!")
