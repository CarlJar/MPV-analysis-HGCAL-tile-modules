import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, find_peaks


def find_tail_cut(
    hist,
    bin_edges,
    window_length=20,
    polyorder=3,
    iterations=10,
    gradient_threshold=0.2,
    gradient=False,
):
    """
    Find the physics-motivated cut point for MIP analysis, considering:
    1. Landau distribution characteristics
    2. Signal-to-noise ratio
    3. Physical energy deposition limits
    
    Parameters:
    - hist: array - Histogram count data
    - bin_edges: array - Bin edges
    - window_length: int - Window size for smoothing
    - polyorder: int - Polynomial order for trend estimation
    - gradient_threshold: float - Threshold for the gradient
    - gradient: bool - Whether to plot the gradient analysis

    Returns:
    - tail_cut_index: int - Index where the tail should be cut
    """
    bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2
    hist_smoothed = hist.copy()
    
    # 1. Apply adaptive smoothing based on statistics
    counts_scale = np.sqrt(np.mean(hist[hist > 0]))  # Statistical scale
    window_length = max(5, min(window_length, int(len(hist) / 5)))
    if window_length % 2 == 0:
        window_length += 1
        
    for i in range(iterations):
        hist_smoothed = savgol_filter(
            hist_smoothed, window_length=window_length, polyorder=polyorder
        )

    # 2. Find MPV and characteristic width
    mpv_idx = np.argmax(hist_smoothed)
    mpv = bin_centers[mpv_idx]
    mpv_height = hist_smoothed[mpv_idx]
    
    # 3. Estimate FWHM for width scale
    half_max = mpv_height / 2
    above_half = hist_smoothed >= half_max
    left_idx = np.where(above_half[:mpv_idx])[0][0] if np.any(above_half[:mpv_idx]) else 0
    right_idx = mpv_idx + np.where(above_half[mpv_idx:][::-1])[0][-1] if np.any(above_half[mpv_idx:]) else len(hist)-1
    fwhm = bin_centers[right_idx] - bin_centers[left_idx]
    
    # 4. Calculate first derivative for tail analysis
    first_derivative = np.gradient(hist_smoothed, bin_centers)
    
    # 5. Physics-motivated tail cut criteria:
    # a) Maximum allowed energy deposition (typically 3-4 times MPV for MIPs)
    max_deposit_idx = np.where(bin_centers > min(4.0 * mpv, 300))[0]
    if len(max_deposit_idx) > 0:
        physics_cut = max_deposit_idx[0]
    else:
        physics_cut = len(hist) - 1
        
    # b) Signal-to-noise criterion (require significant signal)
    noise_level = np.mean(hist_smoothed[int(0.8*len(hist)):]) if len(hist) > 5 else 0
    snr_cut = np.where(hist_smoothed < 2*noise_level)[0]
    snr_cut = snr_cut[snr_cut > mpv_idx][0] if len(snr_cut[snr_cut > mpv_idx]) > 0 else len(hist)-1
    
    # 6. Find gradient-based cut point after MPV
    min_after_peak = np.argmin(first_derivative[mpv_idx:]) + mpv_idx
    boundary = find_peaks(first_derivative[min_after_peak:], distance=1)[0]
    
    gradient_cut = None
    if len(boundary) > 0:
        gradient_cut = min_after_peak + boundary[0]
        # Validate cut point using physics criteria
        if hist_smoothed[gradient_cut] > mpv_height/3:  # Require significant drop from peak
            gradient_cut = None
        
        # 7. Combine criteria and select most conservative valid cut
        valid_cuts = []
        if gradient_cut is not None:
            valid_cuts.append(gradient_cut)
        valid_cuts.extend([physics_cut, snr_cut])
        
        tail_cut_index = min(valid_cuts) if valid_cuts else None
        
        if gradient:
            fig2, ax2 = plt.subplots(2, 1, figsize=(10, 8))
            
            ax2[0].hist(
                (bin_edges[:-1] + bin_edges[1:]) / 2,
                bins=bin_edges,
                weights=hist,
                facecolor="none",
                edgecolor='b',
                alpha=1,
                label='data',
                histtype="stepfilled",
            )
            ax2[0].plot(
                bin_centers, hist_smoothed, label="Smoothed", linestyle="--"
            )
            if tail_cut_index is not None:
                ax2[0].axvline(
                    x=bin_edges[tail_cut_index],
                    color="red",
                    linestyle="--",
                    label="Tail Cut",
                )
            ax2[0].axvline(x=mpv, color="green", linestyle=":", label="MPV")
            ax2[0].legend()
            ax2[0].grid(True)
            
            ax2[1].plot(bin_centers, first_derivative, label="Derivative")
            if tail_cut_index is not None:
                ax2[1].axvline(x=bin_edges[tail_cut_index], color="red", linestyle="--")
            ax2[1].grid(True)
            ax2[1].legend()
            plt.close()

    if gradient:
        fig2, ax2 = plt.subplots(2, 1, figsize=(10, 8))

        ax2[0].hist(
                (bin_edges[:-1] + bin_edges[1:]) / 2,
                bins=bin_edges,
                weights=hist,
                facecolor="none",
                edgecolor='b',
                alpha=1,
                label='data',
                histtype="stepfilled",
                )
             
        ax2[0].plot(
            bin_edges[:-1], hist_smoothed, label="Smoothed Histogram", linestyle="--"
        )
        if tail_cut_index is not None:
            ax2[0].axvline(
                x=bin_edges[tail_cut_index],
                color="red",
                linestyle="--",
                label="Tail Cut",
            )

        ax2[0].legend()
        ax2[0].grid(True)

        ax2[1].plot(bin_edges[:-1], first_derivative, label="Derivative")
        if gradient_threshold is not None:
            ax2[1].axhline(y=gradient_threshold, color="red", linestyle="--")
        if tail_cut_index is not None:
            ax2[1].axvline(x=bin_edges[tail_cut_index], color="red", linestyle="--")
        ax2[1].grid(True)
        ax2[1].legend()
        plt.close()
        #plt.show()

    return tail_cut_index


class HistogramClass:
    def __init__(self, data, bins=20, bin_range=None, density=False):
        """
        Initialize the HistogramClass.

        Parameters:
        - data: Input data for the histogram.
        - bins: Number of bins.
        - bin_range: Range of the bins.
        - density: Whether to normalize the histogram.
        """
        self._n = len(data)
        self._dmin = min(data)
        self._dmax = max(data)
        self._density = density
        self._bins = bins
        bin_counts, bin_edges = np.histogram(
            data, bins=bins, range=bin_range, density=density
        )
        self._bin_counts = bin_counts
        self._bin_edges = bin_edges
        self._bin_mids = (self._bin_edges[1:] + self._bin_edges[:-1]) / 2
        self._bin_width = self._bin_edges[1] - self._bin_edges[0]

        if bin_range is not None:
            bounds = (data >= bin_range[0]) & (data <= bin_range[1])
        else:
            bounds = np.full(shape=data.shape, fill_value=True)

        self._mean = np.mean(data[bounds])
        self._std = np.std(data[bounds])
        self._entries = len(data[bounds])

        self._underflow = 0 if bin_range is None else len(data[data < bin_range[0]])
        self._overflow = 0 if bin_range is None else len(data[data > bin_range[1]])
        self._poisson_errors = np.sqrt(self._bin_counts)

        self.reduced_fit_data = None
        self.reduced_gauss_data = None

    def reduce_hist2(
        self,
        quantile_range=(0.05, 0.8),
        window_length=11,
        polyorder=3,
        iterations=5,
        gradient_threshold=0.2,
        gradient=False,
        label=None,
    ):
        """
        Reduce the histogram data based on quantile range and tail cut.

        Parameters:
        - quantile_range: Range of quantiles to consider.
        - window_length: Window size for Savitzky-Golay smoothing.
        - polyorder: Polynomial order for Savitzky-Golay.
        - iterations: Number of iterations for smoothing.
        - gradient_threshold: Threshold for the gradient.
        - gradient: Whether to plot the gradient analysis.
        - label: Label for the reduced data.

        Returns:
        - reduced_data: Tuple containing (bin_counts, bin_edges, bin_mids)
        """
        if label == "fit" and self.reduced_fit_data is not None:
            return self.reduced_fit_data
        elif label == "gauss" and self.reduced_gauss_data is not None:
            return self.reduced_gauss_data

        print("Calculation done for", label)

        if not (0 <= quantile_range[0] < quantile_range[1] <= 1):
            raise ValueError("Quantile range must be within [0, 1] and valid.")

        cumulative_counts = np.cumsum(self.bin_counts)
        cumulative_area = cumulative_counts / cumulative_counts[-1]

        lower_bound = np.argwhere(cumulative_area >= quantile_range[0])[0][0]
        upper_bound = np.argwhere(cumulative_area <= quantile_range[1])[-1][0]

        tail_cut_index = find_tail_cut(
            self._bin_counts,
            self._bin_edges,
            window_length,
            polyorder,
            iterations,
            gradient_threshold,
            gradient,
        )
        
        # If tail_cut_index is None, use upper_bound as a fallback
        if tail_cut_index is None:
            print(f"Using fallback upper bound at quantile {quantile_range[1]}")
            tail_cut_index = upper_bound

        if tail_cut_index is not None and tail_cut_index: #< upper_bound:
            upper_bound = tail_cut_index

        reduced_bin_edges = self.bin_edges[lower_bound : upper_bound + 1]
        reduced_bin_counts = self.bin_counts[lower_bound:upper_bound]
        reduced_bin_mids = (reduced_bin_edges[1:] + reduced_bin_edges[:-1]) / 2
        
        reduced_data = (
            reduced_bin_counts,
            reduced_bin_edges,
            reduced_bin_mids,
        )
        
        if label == "fit":
            self.reduced_fit_data = reduced_data
        elif label == "gauss":
            self.reduced_gauss_data = reduced_data
            
        return reduced_data

    def init_reduced_data(
        self,
        color="red",
        alpha=0.3,
        label="reduced histogram",
        quantile_range=(0.05, 0.8),
        window_length=11,
        polyorder=3,
        ax=None,
        iterations=5,
        gradient_threshold=0.2,
        gradient=False,
        data_label=None,
    ):
        """
        Initialize and plot the reduced histogram data.

        Parameters:
        - color: Color of the histogram.
        - alpha: Transparency of the histogram.
        - label: Label for the histogram.
        - quantile_range: Range of quantiles to consider.
        - window_length: Window size for Savitzky-Golay smoothing.
        - polyorder: Polynomial order for Savitzky-Golay.
        - ax: Matplotlib axis to plot on.
        - iterations: Number of iterations for smoothing.
        - gradient_threshold: Threshold for the gradient.
        - gradient: Whether to plot the gradient.
        - data_label: Label for the reduced data.
        """
        reduced_bin_counts, reduced_bin_edges, reduced_bin_mids = self.reduce_hist2(
            quantile_range,
            window_length,
            polyorder,
            iterations,
            gradient_threshold,
            gradient,
            data_label,
        )

        if ax is not None:
            n, bins, patches = ax.hist(
                reduced_bin_mids,
                bins=reduced_bin_edges,
                weights=reduced_bin_counts,
                facecolor="none",
                edgecolor=color,
                alpha=alpha,
                label=label,
                histtype="stepfilled",
            )
            ax.axvline(
                x=reduced_bin_edges[-1],
                color="blue",
                linestyle="--",
                label="Upper Bound",
            )
        else:
            n, bins, patches = plt.hist(
                reduced_bin_mids,
                bins=reduced_bin_edges,
                weights=reduced_bin_counts,
                facecolor="none",
                edgecolor=color,
                alpha=alpha,
                label=label,
                histtype="stepfilled",
            )
            plt.axvline(
                x=reduced_bin_edges[-1],
                color="blue",
                linestyle="--",
                label="Upper Bound",
            )

    def plot(self, color="black", alpha=0.3, label="data histogramm", ax=None):
        """
        Plot the histogram data.

        Parameters:
        - color: Color of the histogram.
        - alpha: Transparency of the histogram.
        - label: Label for the histogram.
        - ax: Matplotlib axis to plot on.
        """
        if ax is not None:
            n, bins, patches = ax.hist(
                self.bin_mids,
                bins=self.bin_edges,
                weights=self.bin_counts,
                facecolor="none",
                edgecolor=color,
                alpha=alpha,
                label=label,
                histtype="stepfilled",
            )
        else:
            n, bins, patches = plt.hist(
                self.bin_mids,
                bins=self.bin_edges,
                weights=self.bin_counts,
                facecolor="none",
                edgecolor=color,
                alpha=alpha,
                label=label,
                histtype="stepfilled",
            )



    @property
    def n(self):
        """Return the number of entries in the histogram."""
        return self._n

    @property
    def dmin(self):
        """Return the minimum value of the data."""
        return self._dmin

    @property
    def dmax(self):
        """Return the maximum value of the data."""
        return self._dmax

    @property
    def density(self):
        """Return whether the histogram is normalized."""
        return self._density

    @property
    def bins(self):
        """Return the number of bins in the histogram."""
        return self._bins

    @property
    def bin_counts(self):
        """Return the bin counts of the histogram."""
        return np.array(self._bin_counts)

    @property
    def bin_edges(self):
        """Return the bin edges of the histogram."""
        return np.array(self._bin_edges)

    @property
    def mean(self):
        """Return the mean of the data."""
        return self._mean

    @property
    def std(self):
        """Return the standard deviation of the data."""
        return self._std

    @property
    def entries(self):
        """Return the number of entries in the histogram."""
        return self._entries

    @property
    def underflow(self):
        """Return the number of underflow entries."""
        return self._underflow

    @property
    def overflow(self):
        """Return the number of overflow entries."""
        return self._overflow

    @property
    def poisson_errors(self):
        """Return the Poisson errors of the bin counts."""
        return np.array(self._poisson_errors)

    @property
    def bin_mids(self):
        """Return the midpoints of the bins."""
        return np.array(self._bin_mids)

    @property
    def bin_width(self):
        """Return the width of the bins."""
        return self._bin_width
