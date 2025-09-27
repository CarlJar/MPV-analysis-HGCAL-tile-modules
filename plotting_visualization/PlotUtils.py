import numpy as np

def decode_7bit_data(data:int):
    ls3b = data & 0b00000111
    ms4b = (data >> 3) & 0b00001111
    result = 0b1000 | ls3b
    result = result << int(ms4b)
    return result


decode_7bit_data_np = np.vectorize(decode_7bit_data)


class PlotUtils:
    def __init__(self, analysisConfig):
        self.ac = analysisConfig


    def Hist1D(self, df_plot, ax, x_key, **plot_args):
        x = df_plot[x_key].values

        # Cancel plotting if data set is empty
        if x.shape[0] == 0:
            return

        # Suppress values in the bin x = 0 (and warn the user that events have been dropped)
        x_min = x.min()
        # if x_min < 1 and self.ac.histSettings()["zero_suppression"]:
        #     x_min = 1
        #     ax.text(0.05, 0.85, "Zero suppression: removed values in bin ${}<1$".format(x_key),
        #             fontsize=10, color="r", transform=ax.transAxes)
        #x_range = np.arange(x_min, x.max() + 2, self.ac.granularity(x_key))
        if "x_range" in plot_args:
            x_range = plot_args.pop("x_range")
        else:
            x_range = np.arange(x.min(), x.max()+2, self.ac.granularity(x_key))


        # Cancel plotting if all values are the same
        if x_range.shape[0] == 1:
            return

        hist, bins = np.histogram(x, x_range)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        ax.step(bin_centers, hist, where="mid", **plot_args)

        #ax.set_xlabel(self.ac.name(x_key))
        #ax.set_ylabel("Counts")
        
    

        

    def Hist2D(self, df_plot, ax, x_key, y_key, **plot_args):
        x = df_plot[x_key].values
        y = df_plot[y_key].values

        # Cancel plotting if data set is empty
        if x.shape[0] == 0 or y.shape[0] == 0:
            return

        if "x_range" in plot_args:
            x_range = plot_args.pop("x_range")
        elif x_key == "stcenergy":
            x_range = np.apply_along_axis(decode_7bit_data_np, 0, np.arange(10, 60, 1))
        else:
            x_range = np.arange(x.min(), x.max()+2, self.ac.granularity(x_key))

        if "y_range" in plot_args:
            y_range = plot_args.pop("y_range")
        elif y_key == "stcenergy":
            y_range = np.apply_along_axis(decode_7bit_data_np, 0, np.arange(10, 60, 1))
        else:
            y_range = np.arange(y.min(), y.max()+2, self.ac.granularity(y_key))

        # Cancel plotting if all values are the same
        if x_range.shape[0] == 1 or y_range.shape[0] == 1:
            return

        hist, _a, _b, img = ax.hist2d(x, y, [x_range, y_range], **plot_args) # , norm=matplotlib.colors.LogNorm())
        ax.get_figure().colorbar(img)

        ax.set_xlabel(self.ac.name(x_key))
        ax.set_ylabel(self.ac.name(y_key))

        return x_range, y_range