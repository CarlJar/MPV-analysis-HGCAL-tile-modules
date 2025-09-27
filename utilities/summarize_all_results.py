#!/usr/bin/env python3
import os
import glob
import pandas as pd
import numpy as np

def collect_all_results():
    """
    Collect all analysis results from the CERN Test Beam 2024 runs.
    
    Returns:
    - Combined DataFrame with all results
    """
    # Define the base path and run folders
    base_path = "/home/carlj/BA_local_data/CERN_TB_2024_09_Analysis"
    runs = {
        'muon_250_magnetOn': '2024-09-21_12-29-11_beamrun_muon_250_magnetOn',
        'muon_250_magnetOff': '2024-09-19_15-11-45_beamrun_muon_250',
        'muon_150_magnetOff': '2024-09-16_22-34-48_beamrun_muonss_150'
    }
    
    
    # Read and combine all results
    dfs = []
    for run_name, folder_name in runs.items():
        # Try HDF5 first, fall back to CSV if not found
        h5_path = os.path.join(base_path, folder_name, 'analysis_results', 'simplified_results.h5')
        csv_path = os.path.join(base_path, folder_name, 'analysis_results', 'simplified_results.csv')
        
        try:
            if os.path.exists(h5_path):
                df = pd.read_hdf(h5_path, key='fit_results')
                print(f"Reading HDF5 file for {run_name}")
            elif os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                print(f"Reading CSV file for {run_name}")
            else:
                print(f"No results file found for {run_name}")
                continue
            
            # Add run information with a more readable name
            df['run'] = run_name
            
            print(f"Successfully read {run_name} with {len(df)} entries")
            dfs.append(df)
        except Exception as e:
            print(f"Error reading {run_name} from {file_path}: {e}")
            continue
    
    if not dfs:
        print("No valid data found in any files!")
        return None
    
    # Combine all DataFrames
    combined_df = pd.concat(dfs, ignore_index=True)
    
    return combined_df

def create_summary_tables(df):
    """
    Create a detailed channel-by-channel summary table.
    
    Parameters:
    - df: Combined DataFrame with all results
    
    Returns:
    - Dictionary with single detailed summary table
    """
    # Sort the data by run, chip, and channel
    df_sorted = df.sort_values(['run', 'chip', 'channel'])
    
    # Select only essential columns
    summary = df_sorted[[
        'run', 
        'chip', 
        'channel',
        'mpv',
        'mpv_err_lower',
        'mpv_err_upper',
        'gof',
        'n_entries'
    ]].copy()
    
    # Rename columns for clarity
    summary.columns = [
        'Run',
        'Chip',
        'Channel',
        'MPV',
        'MPV_err_low',
        'MPV_err_high',
        'GoF',
        'N_entries'
    ]
    
    # Round numeric columns for better readability
    numeric_cols = ['MPV', 'MPV_err_low', 'MPV_err_high', 'GoF']
    summary[numeric_cols] = summary[numeric_cols].round(2)
    
    return {'detailed_summary': summary}

def save_summaries(summaries, output_path):
    """
    Save all summary tables to CSV files.
    
    Parameters:
    - summaries: Dictionary of summary DataFrames
    - output_path: Path to save the summary files
    """
    os.makedirs(output_path, exist_ok=True)
    
    # Save each summary to CSV
    for name, df in summaries.items():
        output_file = os.path.join(output_path, f'{name}.csv')
        df.to_csv(output_file)
        print(f"Saved {name} to {output_file}")

def main():
    # Output directory for summaries
    output_path = "thesis_summary_tables"
    
    print("Collecting results from CERN Test Beam 2024...")
    combined_results = collect_all_results()
    
    if combined_results is None:
        print("No results to analyze!")
        return
    
    print("Creating summary tables...")
    summaries = create_summary_tables(combined_results)
    
    print("Saving results...")
    save_summaries(summaries, output_path)
    
    # Print a sample of the results
    print("\nFirst few rows of the summary:")
    print("-" * 40)
    list(summaries.values())[0].head().to_string()

if __name__ == "__main__":
    main()
