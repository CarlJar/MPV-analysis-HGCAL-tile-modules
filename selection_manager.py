import matplotlib.pyplot as plt
import numpy as np
import itertools

def compute_plot_dim(num_channels):
        """
        Compute new plot dimensions as a square grid or a near-square grid.
        """
        rows = int(np.ceil(np.sqrt(num_channels)))
        cols = int(np.ceil(num_channels / rows))
        return (rows, cols)

def selection_manager(data, chip=None, channel=None):
    """
    Function to filter a dictionary of chips and channels based on a chip (key or number) and channel,
    dynamically updating the plot_dim based on the selected data.

    Parameters:
        data (dict): The dictionary containing chips and channel information.
        chip (str|int, optional): The chip key (str) or chip number (int) to select. If None, all chips are considered.
        channel (int, optional): The channel to select. If None, all channels are included.

    Returns:
        dict: Filtered dictionary in the same structure as the input, with updated plot_dim.
    """
    filtered_data = {}

    # Ensure chip and channel are in list form if they're not already
    if chip is not None and not isinstance(chip, list):
        chip = [chip]
    if channel is not None and not isinstance(channel, list):
        channel = [channel]

    # Check if chip is a string (chip key) or integer (chip number)
    if chip is not None:
        chip_keys_to_consider = set()
        if isinstance(chip[0], str):  # chip is a list of keys
            chip_keys_to_consider = set(chip)
        elif isinstance(chip[0], int):  # chip is a list of chip numbers
            chip_keys_to_consider = {key for key, ch_data in data.items() if ch_data['chip'] in chip}

        for key, ch_data in data.items():
            if key in chip_keys_to_consider or ch_data['chip'] in chip:
                selected_channels = ch_data['channels']

                if channel is not None:
                    # Filter channels by the specified channels
                    selected_channels = [ch for ch in selected_channels if ch in channel]

                # Update plot_dim based on selected channels
                filtered_data[key] = {
                    **ch_data,
                    'channels': selected_channels,
                    'plot_dim': compute_plot_dim(len(selected_channels))
                }

    else:  # No specific chip selected, just filter by channels
        for key, ch_data in data.items():
            if channel is not None:
                selected_channels = [ch for ch in ch_data['channels'] if ch in channel]
                if selected_channels:
                    # Update plot_dim based on selected channels
                    filtered_data[key] = {
                        **ch_data,
                        'channels': selected_channels,
                        'plot_dim': compute_plot_dim(len(selected_channels))
                    }
            else:
                # No filter on channels, return all channels and plot_dim
                filtered_data[key] = {
                    **ch_data,
                    'channels': ch_data['channels'],
                    'plot_dim': compute_plot_dim(len(ch_data['channels']))
                }

    return filtered_data
