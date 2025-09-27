import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as norm
import scipy as sp
import pandas as pd
from scipy.optimize import curve_fit
from landaupy import langauss
from landaupy import landau
from HistClass import HistogramClass
from iminuit import cost, Minuit
from PhyPraKit import hFit
import random
import pickle


def BootstrapMaximum(
    model, params, param_errs, numberOfIterations=100, numberOfSamples=100):
    """
    Perform bootstrap resampling to estimate the maximum value of a model.

    Parameters:
    - model: The model function to fit.
    - params: Initial parameters for the model.
    - param_errs: Errors in the parameters.
    - numberOfIterations: Number of bootstrap iterations.
    - numberOfSamples: Number of samples per iteration.

    Returns:
    - results: List of bootstrap results.
    """
    random.seed()

    bootstraprange = [
        params[0] - params[1] - params[2],
        params[0] + params[1] + params[2],
    ]
    
    param_errs[1,:]=0
    print(param_errs)

    lower_bounds = params + param_errs[:, 0]
    upper_bounds = params + param_errs[:, 1]

    print("params", params)
    print("lower bounds:", lower_bounds)
    print("upper bounds:", upper_bounds)

    # Combine them into multiple "value" arrays
    combined_array = np.column_stack((params, lower_bounds, upper_bounds)).T

    # print('combined array',combined_array)
    results = []

    for parameters in combined_array:
        # print(parameters)

        maximumSamples = []

        for i in range(numberOfIterations):
            samples = []
            rns = []
            for i in range(numberOfSamples):
                rn = random.uniform(bootstraprange[0], bootstraprange[1])

                samples.append(
                    model(np.array([rn]), parameters[0], parameters[1], parameters[2], parameters[3])
                )
                rns.append(rn)

            maximumSamples.append(rns[np.argmax(samples)])

        results.append([norm.gmean(maximumSamples), norm.sem(maximumSamples)])

    return results


def calc_bin_count(data):
    """
    Calculate optimal bin count for MIP analysis, considering:
    1. Signal resolution (typical MIP width)
    2. Statistical fluctuations
    3. Landau distribution characteristics
    
    Parameters:
    - data: The dataset for histogram
    Returns:
    - bin_count: Optimized number of bins
    """
    n_entries = len(data)
    data_range = np.ptp(data)
    
    # Get rough MIP peak location for scaling
    median = np.median(data)
    q25, q75 = np.percentile(data, [25, 75])
    iqr = q75 - q25
    
    # Physics-motivated bin width considerations:
    # 1. MIP width scale: typical width is ~15-20% of MPV
    mip_scale = 0.15 * median
    
    # 2. Statistical scale: ensure enough entries per bin
    # Want at least 5-10 entries per bin in peak region
    stat_scale = iqr / np.sqrt(n_entries / 10)
    
    # 3. Landau tail consideration: wider bins in tail region
    # Use larger of the two scales to avoid over-binning the tail
    bin_width = max(mip_scale, stat_scale)
    
    # Ensure reasonable limits
    min_bins = 20  # Minimum bins needed to resolve Landau shape
    max_bins = 100  # Maximum bins to avoid statistical fluctuations
    
    bin_count = int(data_range / bin_width)
    bin_count = np.clip(bin_count, min_bins, max_bins)
    
    return bin_count

def langauss_pdf_wrapper(x, landau_x_mpv, landau_xi, gauss_sigma, b=0):
    """
    Wrapper for the Langaus PDF function with added pedestal constant.

    Parameters:
    - x: Input data.
    - landau_x_mpv: Most probable value of the Landau distribution.
    - landau_xi: Scale parameter of the Landau distribution.
    - gauss_sigma: Standard deviation of the Gaussian distribution.
    - b: Constant pedestal offset.

    Returns:
    - PDF values.
    """
    return langauss.pdf(x, landau_x_mpv, landau_xi, gauss_sigma) + b


def gaussian(x, mu, sigma, amplitude):
    """
    Gaussian function.

    Parameters:
    - x: Input data.
    - mu: Mean of the Gaussian distribution.
    - sigma: Standard deviation of the Gaussian distribution.
    - amplitude: Amplitude of the Gaussian distribution.

    Returns:
    - Gaussian function values.
    """
    return amplitude * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def perform_gaussian_guess(hist, quantile_range=(0.025, 0.80)):
    """
    Perform an initial Gaussian guess for the histogram data with multiple fallback methods.

    Parameters:
    - hist: Histogram data.
    - quantile_range: Range of quantiles to consider for the guess.

    Returns:
    - gauss_fit: Fitted Gaussian parameters [mu, sigma, amplitude].
    """
    def estimate_peak_region(counts, edges):
        """Estimate peak region using moving average for noise reduction"""
        window = max(3, len(counts) // 10)  # Dynamic window size
        if window % 2 == 0:
            window += 1  # Ensure odd window size
        
        smoothed = sp.ndimage.gaussian_filter1d(counts, window/3)
        peak_idx = np.argmax(smoothed)
        
        # Find FWHM region
        half_max = smoothed[peak_idx] / 2
        left_idx = np.where(smoothed[:peak_idx] < half_max)[0]
        right_idx = np.where(smoothed[peak_idx:] < half_max)[0]
        
        left = left_idx[-1] if len(left_idx) > 0 else 0
        right = peak_idx + right_idx[0] if len(right_idx) > 0 else len(counts)-1
        
        return left, peak_idx, right

    try:
        # Method 1: Standard reduction and fit
        n, xe, x = hist.reduce_hist2(
            quantile_range=quantile_range, gradient_threshold=0.1, label="gauss"
        )
        bin_mids = 0.5 * (xe[1:] + xe[:-1])
        
        # Get peak region for better initial estimates
        left_idx, peak_idx, right_idx = estimate_peak_region(n, xe)
        peak_region = n[left_idx:right_idx+1]
        peak_mids = bin_mids[left_idx:right_idx+1]
        
        # Physical parameter estimation
        mu_est = bin_mids[peak_idx]  # Position of maximum
        sigma_est = (bin_mids[right_idx] - bin_mids[left_idx]) / 2.355  # FWHM to sigma
        amplitude_est = n[peak_idx]
        
        # Fallback estimates if peak finding fails
        if not (10 < mu_est < 300):
            # Method 2: Robust statistics
            q25, q75 = np.percentile(hist.bin_mids[hist.bin_counts > 0], [25, 75])
            mu_est = np.median(hist.bin_mids[hist.bin_counts > 0])
            sigma_est = (q75 - q25) / 1.349  # IQR to sigma conversion
            amplitude_est = np.max(hist.bin_counts)
        
        initial_guess = [mu_est, sigma_est, amplitude_est]
        
        # Physical constraints
        bounds = (
            [max(10, xe[0]), 0, 0],  # lower bounds
            [min(300, xe[-1]), mu_est, np.inf]  # upper bounds
        )
        
        # Try fit with constraints
        gauss_fit, pcov = curve_fit(gaussian, bin_mids, n, 
                                   p0=initial_guess, 
                                   bounds=bounds,
                                   maxfev=2000)
        
        # Validate fit results
        if not (10 < gauss_fit[0] < 300 or  # mu in valid range
                gauss_fit[1] < gauss_fit[0]/2):  # sigma < mu/2
            return initial_guess  # Return physical estimate if fit fails
        
        return gauss_fit

    except RuntimeError as e:
        print(f"An error occurred during Gaussian fitting: {e}.")
        return None


def perform_fit(hist, gauss_guess, x_fit, red_quantile_range, chan):
    """
    Perform the Langaus fit without plotting.

    Parameters:
    - hist: Histogram data.
    - gauss_guess: Initial guess for the Gaussian parameters.
    - x_fit: The x values for fitting.
    - red_quantile_range: Range of quantiles to consider for the fit.
    - chan: The channel number.

    Returns:
    - fit_params: Fitted parameters.
    - fit_errors: Errors in the fitted parameters.
    - fit_cov: Covariance of the fitted parameters.
    - gof: Goodness of fit.
    """
    try:
        LANDAU_X_MPV = gauss_guess[0]
        LANDAU_XI = gauss_guess[1] / 2
        GAUSS_SIGMA = gauss_guess[1] / 2
        B = 0  # Initial pedestal constant

        def langauss_pdf_wrapper_local(
            x, landau_x_mpv=LANDAU_X_MPV, landau_xi=LANDAU_XI, gauss_sigma=GAUSS_SIGMA, b=B
        ):
            return langauss.pdf(x, landau_x_mpv, landau_xi, gauss_sigma) + b

        initial_guess = np.array([LANDAU_X_MPV, LANDAU_XI, GAUSS_SIGMA, B])

        bounds = [
            ["landau_x_mpv", 0.0, 400],
            ["landau_xi", 0, None],
            ["gauss_sigma", 0.0, None],
            ["b", 0.0, None]  # Range for pedestal constant
        ]

        # Get reduced histogram for fitting
        n, xe, x = hist.reduce_hist2(
            quantile_range=red_quantile_range, 
            gradient_threshold=0.075, 
            iterations=5,
            label="fit"
        )

        # Perform the fit
        rdict = hFit(
            langauss_pdf_wrapper_local,
            n,
            xe,
            p0=initial_guess,
            limits=bounds,
            use_GaussApprox=False,
            fit_density=True,
            plot=False,
            plot_band=False,
            plot_cor=False,
            quiet=True,
            same_plot=True,
            axis_labels=["Signal Amplitudes [ADC]", "No. of Entries"],
            data_legend="data",
            model_legend="Landau-Gauss Convolution",
        )

        pvals, perrs, cor, gof, pnams = rdict.values()
        
        # Stricter quality checks
        if gof > 3.0 * np.sum(n):  # Adjust threshold based on number of entries
            print(f"Poor fit quality for channel {chan}. GoF: {gof}")
            return None

        # Check parameter reasonableness
        if not (10 < pvals[0] < 300):  # MPV check
            print(f"Unreasonable MPV value: {pvals[0]}")
            return None

        if pvals[1] > 0.5 * pvals[0] or pvals[2] > 0.5 * pvals[0]:  # Width checks
            print(f"Unreasonable width parameters: xi={pvals[1]}, sigma={pvals[2]}")
            return None

        return pvals, perrs, cor, gof

    except Exception as e:
        print(f"Fit failed for channel {chan}: {str(e)}")
        return None


def perform_analysis_noplot(df_plot, x_key, chan, use_tailcut=True):
    """
    Perform analysis without plotting and return comprehensive data for later plotting.

    Parameters:
    - df_plot: DataFrame containing the data to analyze.
    - x_key: The key for the x-axis data in the DataFrame.
    - chan: The channel number.
    - use_tailcut: Whether to apply gradient threshold for tail cutting (default: True)

    Returns:
    - analysis_result: Dictionary containing all analysis results and data for plotting
    """

    if df_plot.empty or x_key not in df_plot.columns:
        print(f"No data available for {x_key} in the channel. Skipping.")
        return None

    adc_values = df_plot[x_key].values

    if len(adc_values) == 0:
        print("No ADC values available for fitting. Skipping the analysis.")
        return None

    if len(adc_values) < 50:
        print(
            f"Not enough entries for fitting (requires more than 50). Channel {chan} has {len(adc_values)} entries."
        )
        return {
            'channel': chan,
            'status': 'insufficient_data',
            'n_entries': len(adc_values),
            'adc_values': adc_values
        }

    # Construct full histogram
    bin_count = calc_bin_count(adc_values)
    use_density = False
    hist = HistogramClass(
        adc_values, bins=bin_count, bin_range=(0, 400), density=use_density
    )

    # Thresholds
    fit_quantile_range = (0.05, 0.90)
    gauss_quantile_range = (0.08, 0.8)

    # Gradient thresholds - set to 0 if tail cut is disabled
    fit_gradient_threshold = 0.1 if use_tailcut else 0
    gauss_gradient_threshold = 0.5 if use_tailcut else 0

    try:
        # Initialize reduced data without plotting
        fit_data = hist.reduce_hist2(
            quantile_range=fit_quantile_range,
            gradient_threshold=fit_gradient_threshold,
            iterations=5,
            gradient=True,  # Enable gradient data collection
            label="fit",
        )

        gauss_data = hist.reduce_hist2(
            quantile_range=gauss_quantile_range,
            gradient_threshold=gauss_gradient_threshold,
            iterations=5,
            gradient=True,  # Enable gradient data collection
            label="gauss",
        )
    except Exception as e:
        print(f"Channel {chan}: Error in histogram reduction: {str(e)}")
        return {
            'channel': chan,
            'status': 'hist_reduction_failed',
            'error': str(e),
            'n_entries': len(adc_values),
            'adc_values': adc_values,
            'hist_data': {
                'bin_counts': hist.bin_counts,
                'bin_edges': hist.bin_edges,
                'bin_mids': hist.bin_mids,
                'bin_width': hist.bin_width
            }
        }

    # Try multiple initial guesses for Gaussian fit
    gauss_guess = None
    gauss_ranges = [(0.025, 0.80), (0.05, 0.75), (0.08, 0.70)]
    for g_range in gauss_ranges:
        gauss_guess = perform_gaussian_guess(hist, quantile_range=g_range)
        if gauss_guess is not None and 10 < gauss_guess[0] < 300:  # Check if guess is reasonable
            break

    if gauss_guess is None:
        print("Gaussian fitting failed. Skipping the fit.")
        return {
            'channel': chan,
            'status': 'gaussian_fit_failed',
            'n_entries': len(adc_values),
            'adc_values': adc_values,
            'hist_data': {
                'bin_counts': hist.bin_counts,
                'bin_edges': hist.bin_edges,
                'bin_mids': hist.bin_mids,
                'bin_width': hist.bin_width
            }
        }

    x_fit = np.linspace(adc_values.min(), adc_values.max(), 500)
    y_gauss = gaussian(x_fit, *gauss_guess)

    # Perform the fit with tighter bounds
    fit_dict = perform_fit(hist, gauss_guess, x_fit, fit_quantile_range, chan)
    
    if fit_dict is None:
        return {
            'channel': chan,
            'status': 'langaus_fit_failed',
            'n_entries': len(adc_values),
            'adc_values': adc_values,
            'hist_data': {
                'bin_counts': hist.bin_counts,
                'bin_edges': hist.bin_edges,
                'bin_mids': hist.bin_mids,
                'bin_width': hist.bin_width
            },
            'gauss_fit': {
                'params': gauss_guess,
                'x_fit': x_fit,
                'y_fit': y_gauss
            }
        }

    # Bootstrap
    skip_bootstrap = False
    if skip_bootstrap:
        print("Skipping the bootstrap.")
        return None

    bootstrap_res = BootstrapMaximum(
        langauss_pdf_wrapper,
        fit_dict[0],
        fit_dict[1],
        numberOfIterations=50,
        numberOfSamples=100,
    )

    mpv, mpv_err = bootstrap_res[0]
    mpv_edges, mpv_edges_err = zip(*bootstrap_res[1:])
    mpv_edges, mpv_edges_err = np.array(mpv_edges), np.array(mpv_edges_err)
    mpv_err_estimate = [[mpv - mpv_edges[0]], [mpv_edges[1] - mpv]]

    # Get reduced histogram data for plotting
    reduced_fit_data = hist.reduced_fit_data
    reduced_gauss_data = hist.reduced_gauss_data

    # Extract gradient data if available
    fit_gradient_data = reduced_fit_data[3]['gradient_data'] if len(reduced_fit_data) > 3 else None
    gauss_gradient_data = reduced_gauss_data[3]['gradient_data'] if len(reduced_gauss_data) > 3 else None

    # Calculate Langaus fit curve
    y_langaus_guess = (hist.n * hist.bin_width * 
                      langauss_pdf_wrapper(x_fit, gauss_guess[0], gauss_guess[1]/2, gauss_guess[1]/2))
    
    y_langaus_fit = (np.sum(reduced_fit_data[0]) * hist.bin_width * 
                    langauss_pdf_wrapper(x_fit, *fit_dict[0]))

    # Prepare comprehensive result
    analysis_result = {
        'channel': chan,
        'status': 'success',
        'n_entries': len(adc_values),
        'config': {
            'use_tailcut': use_tailcut,
            'fit_gradient_threshold': fit_gradient_threshold,
            'gauss_gradient_threshold': gauss_gradient_threshold,
            'fit_quantile_range': fit_quantile_range,
            'gauss_quantile_range': gauss_quantile_range
        },
        'adc_values': adc_values,
        'hist_data': {
            'bin_counts': hist.bin_counts,
            'bin_edges': hist.bin_edges,
            'bin_mids': hist.bin_mids,
            'bin_width': hist.bin_width,
            'mean': hist.mean,
            'std': hist.std,
            'entries': hist.entries,
            'underflow': hist.underflow,
            'overflow': hist.overflow
        },
        'reduced_hist_data': {
            'fit': {
                'bin_counts': reduced_fit_data[0],
                'bin_edges': reduced_fit_data[1],
                'bin_mids': reduced_fit_data[2],
                'gradient_data': fit_gradient_data
            },
            'gauss': {
                'bin_counts': reduced_gauss_data[0],
                'bin_edges': reduced_gauss_data[1],
                'bin_mids': reduced_gauss_data[2],
                'gradient_data': gauss_gradient_data
            }
        },
        'gauss_fit': {
            'params': gauss_guess,
            'param_names': ['mu', 'sigma', 'amplitude'],
            'x_fit': x_fit,
            'y_fit': y_gauss
        },
        'langaus_fit': {
            'params': fit_dict[0],
            'param_errors': fit_dict[1],
            'param_names': ['landau_x_mpv', 'landau_xi', 'gauss_sigma', 'b'],
            'covariance': fit_dict[2],
            'gof': fit_dict[3],
            'x_fit': x_fit,
            'y_guess': y_langaus_guess,
            'y_fit': y_langaus_fit
        },
        'bootstrap_results': {
            'mpv': mpv,
            'mpv_err': mpv_err,
            'mpv_edges': mpv_edges,
            'mpv_edges_err': mpv_edges_err,
            'mpv_err_estimate': mpv_err_estimate,
            'all_results': bootstrap_res
        },
        'quantile_ranges': {
            'fit': fit_quantile_range,
            'gauss': gauss_quantile_range
        }
    }

    return analysis_result


def save_analysis_results(results_list, output_path):
    """
    Save comprehensive analysis results to file.
    
    Parameters:
    - results_list: List of analysis result dictionaries
    - output_path: Path to save the results
    
    Returns:
    - df_simplified: DataFrame with simplified results
    """
    import os
    # Make sure parent directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Save as pickle for complete data preservation
    with open(os.path.join(output_path, 'complete_results.pkl'), 'wb') as f:
        pickle.dump(results_list, f)
    
    # Also create a simplified DataFrame for easy access
    simplified_results = []
    for result in results_list:
        if result is None or result['status'] != 'success':
            continue
            
        # Get MPV and errors from bootstrap analysis
        mpv = result['bootstrap_results']['mpv']
        # Get asymmetric errors if available
        mpv_err_lower = result['bootstrap_results']['mpv_err_estimate'][0][0] if 'mpv_err_estimate' in result['bootstrap_results'] else result['bootstrap_results']['mpv_err']
        mpv_err_upper = result['bootstrap_results']['mpv_err_estimate'][1][0] if 'mpv_err_estimate' in result['bootstrap_results'] else result['bootstrap_results']['mpv_err']
        
        simplified_results.append({
            'channel': result['channel'],
            'chip': result.get('chip', 0),  # Use 0 as default if chip info is missing
            'tbname': result.get('tbname', ''),  # Empty string as default if tbname is missing
            'n_entries': result['n_entries'],
            'hist_mean': result['hist_data']['mean'],
            'hist_std': result['hist_data']['std'],
            'gauss_mu': result['gauss_fit']['params'][0],
            'gauss_sigma': result['gauss_fit']['params'][1],
            'gauss_amplitude': result['gauss_fit']['params'][2],
            'landau_x_mpv': result['langaus_fit']['params'][0],
            'landau_xi': result['langaus_fit']['params'][1],
            'langaus_gauss_sigma': result['langaus_fit']['params'][2],
            'pedestal_b': result['langaus_fit']['params'][3],  # Add pedestal constant
            'landau_x_mpv_err': result['langaus_fit']['param_errors'][0],
            'landau_xi_err': result['langaus_fit']['param_errors'][1],
            'langaus_gauss_sigma_err': result['langaus_fit']['param_errors'][2],
            'pedestal_b_err': result['langaus_fit']['param_errors'][3],  # Add pedestal constant error
            'gof': result['langaus_fit']['gof'],
            # Add fields with names matching what TB_09_Muon_MIP_Comparison expects
            'mpv': mpv,  # MPV from bootstrap analysis
            'mpv_err_lower': mpv_err_lower,  # Lower error on MPV
            'mpv_err_upper': mpv_err_upper,  # Upper error on MPV
        })
    
    df_simplified = pd.DataFrame(simplified_results)
    
    # Save in multiple formats for different use cases
    df_simplified.to_hdf(os.path.join(output_path, 'simplified_results.h5'), key='fit_results', format='fixed', mode='w')
    df_simplified.to_csv(os.path.join(output_path, 'simplified_results.csv'), index=False)
    
    return df_simplified
