from HistClass import HistogramClass
import scipy.optimize as opt
import pandas as pd
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy.stats import multivariate_normal
from scipy.integrate import quad
from scipy.integrate import quad_vec
from iminuit import cost, Minuit
from jacobi import jacobi

import random
import scipy.stats as scp
import numpy as np

class Fitter:
    def __init__(self, histogram=None):
        """
        Initialize the Fitter class with an empty parameters DataFrame
        and placeholders for histogram data.
        """
        # Initialize an empty DataFrame for parameters with multi-index columns
        self.parameters = pd.DataFrame(
            columns=pd.MultiIndex.from_product(
                [
                    ["widthLan", "mp", "area", "widthGaus"],
                    ["value", "error", "fixed", "min", "max"],
                ]
            )
        )

        # Placeholders for histogram data
        if histogram is not None:
            self.hist = histogram
            self.data = self.hist.bin_counts
            self.eps = self.hist.bin_errors
        else:
            self.hist = None
            self.eps = self


    def getValues(self):
        return self.parameters.xs("value", level=1, axis=1).to_numpy().flatten()

    def setHistogram(self, histogram):  # bincenters, histogram entries
        self.hist = histogram
        self.data = self.hist.bin_counts
        self.eps = self.hist.bin_errors

    def setEps(self, val):  # bincenters, histogram entries
        self.eps = val

    def setParameters(self, pardict):
        """
        Set the initial parameters and bounds in the DataFrame.
        Parameters:
            pardict (dict): A dictionary where keys are parameter names and
                            values are tuples (initial_value, min_value, max_value).
        """
        # Initialize an empty dictionary to hold the parameter data
        data = {}

        # Fill the data dictionary with the values for each parameter
        for param, (value, min_val, max_val) in pardict.items():
            data[(param, "value")] = [value]  # Initial value
            data[(param, "error")] = [None]  # Error (initially None)
            data[(param, "fixed")] = [False]  # Fixed (initially False)
            data[(param, "min")] = [min_val]  # Lower bound
            data[(param, "max")] = [max_val]  # Upper bound

        # Create the DataFrame using the data dictionary
        self.parameters = pd.DataFrame(data)

    def printParameters(self, columns_to_display=["value"], parameter_names=None):
        """
        Prints the specified parameters and their selected attributes.

        :param columns_to_display: List of attributes to display (e.g., ['value', 'error'])
        :param parameter_names: List of parameter names to filter (e.g., ['widthLan', 'mp'])
        """
        if parameter_names is None:
            parameter_names = self.parameters.columns.levels[0]

        selected_columns = [
            (param, col)
            for param in parameter_names
            for col in columns_to_display
            if (param, col) in self.parameters.columns
        ]

        if not selected_columns:
            print("No matching columns found.")
            return

        # Display the filtered DataFrame
        print(self.parameters[selected_columns])

    def fit2(self, fitmethod="curve_fit", eps=None, histogram=None):
        """
        Perform the fitting using scipy's curve_fit instead of lmfit.
        Parameters:
        fitmethod: 'curve_fit' (default)
        eps: Errors for weighted fitting (if provided)
        histogram: Optional reduced histogram to use for fitting
        Returns:
        result: Optimal parameter values
        param_errors: Standard deviations (errors) for the parameters
        """
        if histogram is not None:
            self.setHistogram(histogram)

        x, y = self.hist.bin_mids, self.hist.bin_counts

        # Extract initial parameter values and bounds from the DataFrame with multi-index columns
        p0 = [
            self.parameters.loc[0, (param, "value")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]

        # Extract parameter bounds (min and max) from the DataFrame with multi-index columns
        bounds_lower = [
            self.parameters.loc[0, (param, "min")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]
        bounds_upper = [
            self.parameters.loc[0, (param, "max")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]

        # Fit the model using curve_fit
        # popt, pcov, infodict, mesg, ier = opt.curve_fit(
        #     self.bin_residuals,  # Use residual function for fitting
        #     x,  # x data (bin centers)
        #     y,  # y data (bin counts)
        #     p0=p0,  # Initial guess for parameters
        #     method='lm',
        #     # sigma=err,  # Optional: errors for weighted fitting
        #     # bounds=(bounds_lower, bounds_upper),  # Parameter bounds
        #     # absolute_sigma=True,  # Whether to use absolute errors for weighting
        #     full_output=True,
        # )

        print(p0)
        popt, pcov, infodict, mesg, ier = opt.leastsq(self.bin_residuals, p0, full_output=True)
        print(popt)
        print("====================================")
        
        dof= len(x) - len(popt) # 4 fitted parameters
        # calculate chi^2 vlues from infodict residuals

        print(self.bin_residuals(popt))

        chisq= np.sum(self.bin_residuals(popt)**2)/dof


    
        # Calculate parameter errors from the covariance matrix
        if pcov is not None and pcov.ndim == 2:
            param_errors = np.sqrt(np.diag(pcov))
            # Update the parameter DataFrame with the optimized values and errors
            for i, param in enumerate(["widthLan", "mp", "area", "widthGaus"]):
                self.parameters.loc[0, (param, "value")] = popt[i]
                self.parameters.loc[0, (param, "error")] = param_errors[i]
        else:
            print("Covariance matrix could not be estimated.")
            for i, param in enumerate(["widthLan", "mp", "area", "widthGaus"]):
                self.parameters.loc[0, (param, "value")] = popt[i]
                self.parameters.loc[0, (param, "error")] = None

        # # Update the parameter DataFrame with the optimized values and errors
        # for i, param in enumerate(["widthLan", "mp", "area", "widthGaus"]):
        #     self.parameters.loc[0, (param, "value")] = popt[i]
        #     self.parameters.loc[0, (param, "error")] = param_errors[i]

        mean, meanError = self.BootstrapMaximum(100, 100)
        
        return popt, pcov, param_errors, mean, meanError, infodict, chisq

    def fit3(self, fitmethod="curve_fit", eps=None, histogram=None):
        """
        Perform the fitting using Minuit.
        Parameters:
        fitmethod: 'curve_fit' (default)
        eps: Errors for weighted fitting (if provided)
        histogram: Optional reduced histogram to use for fitting
        Returns:
        result: Optimal parameter values
        param_errors: Standard deviations (errors) for the parameters
        """
        if histogram is not None:
            self.setHistogram(histogram)

        xe, n = self.hist.bin_edges, self.hist.bin_counts
        
        print('xe=',xe)
        print('n=',n)
        # Extract initial parameter values and bounds from the DataFrame with multi-index columns
        p0 = [
            self.parameters.loc[0, (param, "value")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]

        # Extract parameter bounds (min and max) from the DataFrame with multi-index columns
        bounds_lower = [
            self.parameters.loc[0, (param, "min")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]
        bounds_upper = [
            self.parameters.loc[0, (param, "max")]
            for param in ["widthLan", "mp", "area", "widthGaus"]
        ]

        # Define the cost function for Minuit
        # c = cost.BinnedNLL(n, xe, self.langaufun_wrapper, use_pdf="numerical")
        c = cost.BinnedNLL(n, xe, self.langaus_cdf)

        print('1')
        # Initialize Minuit with the initial parameter values and bounds
        m = Minuit(c, widthLan=p0[0], mp=p0[1], area=p0[2], widthGaus=p0[3])
        m.limits["widthLan"] = (bounds_lower[0], bounds_upper[0])
        m.limits["mp"] = (bounds_lower[1], bounds_upper[1])
        m.limits["area"] = (bounds_lower[2], bounds_upper[2])
        m.limits["widthGaus"] = (bounds_lower[3], bounds_upper[3])

        print('2')
        # Perform the minimization
        m.migrad()

        print('3')
        # Extract the optimized parameter values and errors
        popt = m.values
        param_errors = m.errors

        # Update the parameter DataFrame with the optimized values and errors
        for i, param in enumerate(["widthLan", "mp", "area", "widthGaus"]):
            self.parameters.loc[0, (param, "value")] = popt[param]
            self.parameters.loc[0, (param, "error")] = param_errors[param]

        mean, meanError = self.BootstrapMaximum(100, 100)
        
        return popt, param_errors, mean, meanError, m.fval, m

    def langaus_cdf(self, xe, widthLan, mp, area, widthGaus):
        """
        Calculate the cumulative distribution function (CDF) of the langaufun using histogram bin approximation.

        Parameters:
        histogram: HistogramClass instance
        widthLan, mp, area, widthGaus: parameters for the PDF

        Returns:
        array-like, cumulative sum of bin-width times PDF evaluated at center
        """
        # Bin edges from the histogram
        dx = np.diff(xe)
        cx = xe[:-1] + 0.5 * dx
        print('5')
        p = np.array(self.langaufun_wrapper(cx, widthLan, mp, area, widthGaus))
        
        return np.append([0], np.cumsum(p * dx))
     
        dx = histogram.bin_width  # Bin widths
        cx = xe[:-1] + 0.5 * dx  # Bin centers
        p = np.array(self.langaufun(cx, widthLan, mp, area, widthGaus))  # Evaluate PDF at bin centers
        cdf = np.append([0], np.cumsum(p * dx))  # Cumulative sum of bin-width times PDF
        return cdf

    def bin_residuals(self, p):
        widthLan, mp, area, widthGaus = p
        x, y, err, var= self.hist.get_filtered_data()
    
        lambda_i = int(self.hist.entries) * np.array(self.langaufun(x,widthLan, mp, area, widthGaus)) / float(np.sum( self.langaufun(x,widthLan, mp, area, widthGaus) ))
        lambda_0 = np.array(self.langaufun(x,widthLan, mp, area, widthGaus))
        #print(lambda_i)
        #print(len(lambda_i))

        print([float(np.sum( self.langaufun(x,widthLan, mp, area, widthGaus))),self.hist.entries,self.hist.n])

        return (y - np.array(lambda_0)) / np.sqrt(var) / err


    def residual(self, x, *p):
        widthLan, mp, area, widthGaus = p

        mod = self.langaufun(x, widthLan, mp, area, widthGaus)

        if self.data is None:
            return mod
        if self.eps is None:
            return mod - self.data
        return (mod - self.data) / self.eps

    def BootstrapMaximum(self, numberOfIterations=100, numberOfSamples=100):
        random.seed()

        widthLan, mp, area, widthGaus = self.getValues()

        bootstraprange = [mp - widthLan - widthGaus, mp + widthLan + widthGaus]
        # Old, before correction:
        # bootstraprange = [mp - widthLan, mp + widthLan]
        print("Bootstrap range: ", bootstraprange)
        maximumSamples = []

        for i in range(numberOfIterations):
            samples = []
            rns = []
            for i in range(numberOfSamples):
                rn = random.uniform(bootstraprange[0], bootstraprange[1])

                samples.append(self.langaufun([rn], widthLan, mp, area, widthGaus))
                rns.append(rn)

            maximumSamples.append(rns[np.argmax(samples)])

        #         print(maxSamples)
        #         print(scp.gmean(maxSamples))
        #         print(scp.sem(maxSamples))

        return scp.gmean(maximumSamples), scp.sem(maximumSamples)

    def landau_pdf(self, x, xi=1, x0=0):
        #
        # LANDAU pdf : algorithm from CERNLIB G110 denlan
        # same algorithm is used in GSL

        p1 = [
            0.4259894875,
            -0.1249762550,
            0.03984243700,
            -0.006298287635,
            0.001511162253,
        ]
        q1 = [1.0, -0.3388260629, 0.09594393323, -0.01608042283, 0.003778942063]

        p2 = [
            0.1788541609,
            0.1173957403,
            0.01488850518,
            -0.001394989411,
            0.0001283617211,
        ]
        q2 = [1.0, 0.7428795082, 0.3153932961, 0.06694219548, 0.008790609714]

        p3 = [
            0.1788544503,
            0.09359161662,
            0.006325387654,
            0.00006611667319,
            -0.000002031049101,
        ]
        q3 = [1.0, 0.6097809921, 0.2560616665, 0.04746722384, 0.006957301675]

        p4 = [0.9874054407, 118.6723273, 849.2794360, -743.7792444, 427.0262186]
        q4 = [1.0, 106.8615961, 337.6496214, 2016.712389, 1597.063511]

        p5 = [1.003675074, 167.5702434, 4789.711289, 21217.86767, -22324.94910]
        q5 = [1.0, 156.9424537, 3745.310488, 9834.698876, 66924.28357]

        p6 = [1.000827619, 664.9143136, 62972.92665, 475554.6998, -5743609.109]
        q6 = [1.0, 651.4101098, 56974.73333, 165917.4725, -2815759.939]

        a1 = [0.04166666667, -0.01996527778, 0.02709538966]

        a2 = [-1.845568670, -4.284640743]

        if xi <= 0:
            return 0

        v = (x - x0) / xi

        u = 0.0
        ue = 0.0
        us = 0.0
        denlan = 0.0

        if v < -5.5:
            u = np.exp(v + 1.0)

            if u < 1e-10:
                return 0.0

            ue = np.exp(-1 / u)
            us = np.sqrt(u)
            denlan = (
                0.3989422803 * (ue / us) * (1 + (a1[0] + (a1[1] + a1[2] * u) * u) * u)
            )

        elif v < -1:
            u = np.exp(-v - 1)
            denlan = (
                np.exp(-u)
                * np.sqrt(u)
                * (p1[0] + (p1[1] + (p1[2] + (p1[3] + p1[4] * v) * v) * v) * v)
                / (q1[0] + (q1[1] + (q1[2] + (q1[3] + q1[4] * v) * v) * v) * v)
            )

        elif v < 1:
            denlan = (p2[0] + (p2[1] + (p2[2] + (p2[3] + p2[4] * v) * v) * v) * v) / (
                q2[0] + (q2[1] + (q2[2] + (q2[3] + q2[4] * v) * v) * v) * v
            )

        elif v < 5:
            denlan = (p3[0] + (p3[1] + (p3[2] + (p3[3] + p3[4] * v) * v) * v) * v) / (
                q3[0] + (q3[1] + (q3[2] + (q3[3] + q3[4] * v) * v) * v) * v
            )

        elif v < 12:
            u = 1 / v
            denlan = (
                u
                * u
                * (p4[0] + (p4[1] + (p4[2] + (p4[3] + p4[4] * u) * u) * u) * u)
                / (q4[0] + (q4[1] + (q4[2] + (q4[3] + q4[4] * u) * u) * u) * u)
            )

        elif v < 50:
            u = 1 / v
            denlan = (
                u
                * u
                * (p5[0] + (p5[1] + (p5[2] + (p5[3] + p5[4] * u) * u) * u) * u)
                / (q5[0] + (q5[1] + (q5[2] + (q5[3] + q5[4] * u) * u) * u) * u)
            )

        elif v < 300:
            u = 1 / v
            denlan = (
                u
                * u
                * (p6[0] + (p6[1] + (p6[2] + (p6[3] + p6[4] * u) * u) * u) * u)
                / (q6[0] + (q6[1] + (q6[2] + (q6[3] + q6[4] * u) * u) * u) * u)
            )

        else:
            u = 1 / (v - v * np.log(v) / (v + 1))
            denlan = u * u * (1 + (a2[0] + a2[1] * u) * u)

        return denlan / xi

    
    
    
    def Landau(self, x, mu=0, sigma=1, norm=False):  # double, double, double, bool
        if sigma <= 0:
            return 0
        den = self.landau_pdf((x - mu) / sigma)
        if not norm:
            return den
        return den / sigma


    def Gaus(self, x, mu, sig):
        return np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))



    def langaufun(self, x, widthLan, mp, area, widthGaus): #double, list[4]
        """
        Convolution of a Landau and a Gaussian function.
        
        In the Landau distribution (represented by the CERNLIB approximation),
        the maximum is located at x=-0.22278298 with the location parameter=0.
        This shift is corrected within this function, so that the actual
        maximum is identical to the MP parameter.
        
        Parameters:
        x (list): Points at which to evaluate the function.
        widthLan (float): Width (scale) parameter of the Landau distribution.
        mp (float): Most Probable (location) parameter of the Landau distribution.
        area (float): Total area (integral from -inf to inf, normalization constant).
        widthGaus (float): Width (sigma) of the convoluted Gaussian function.

        Returns:
        list: Evaluated convolution of the Landau and Gaussian functions at points x.
        """
        
        retarray = []
        for point in x:
            # Numeric constants
            invsq2pi = 0.3989422804014  # (2 pi)^(-1/2)
            mpshift = -0.22278298  # Landau maximum location

            # Control constants
            np = 100.0  # number of convolution steps
            sc = 5.0  # convolution extends to +-sc Gaussian sigmas

            # Variables
            xx = 0.0
            mpc = 0.0
            fland = 0.0
            sam = 0.0
            xlow = 0.0
            xupp = 0.0
            # MP shift correction
            mpc = mp - mpshift * widthLan

            # Range of convolution integral
            xlow = point - sc * widthGaus
            xupp = point + sc * widthGaus

            step = (xupp - xlow) / np

            # Convolution integral of Landau and Gaussian by sum
            i = 1.0
            while i <= np / 2:
                xx = xlow + (i - 0.5) * step

                fland = self.Landau(xx, mpc, widthLan) / widthLan
                sam += fland * self.Gaus(point, xx, widthGaus)

                xx = xupp - (i - 0.5) * step
                fland = self.Landau(xx, mpc, widthLan) / widthLan
                sam += fland * self.Gaus(point, xx, widthGaus)
                i += 1

            retarray.append((area * step * sam * invsq2pi / widthGaus))

        return retarray


    def langaufun_wrapper(self, x, widthLan, mp, area, widthGaus):

        if isinstance(x, list):
            return self.langaufun(x, widthLan, mp, area, widthGaus)

        if np.isscalar(x):
            return np.array(self.langaufun([x], widthLan, mp, area, widthGaus))[0]



