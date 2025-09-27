import os
import sys
import math
import ROOT
import random
import numpy as np


def plot_varVStrigtime(histo, **kwargs):

    canvas = ROOT.TCanvas("canvas","canvas",800, 600)
    canvas.SetFillColor(0)
    canvas.SetGrid()
    canvas.GetFrame().SetFillColor(2)
    canvas.GetFrame().SetBorderSize(12)

    histo.Draw("colz")
    histo.GetXaxis().SetTitle("TrigTime [ADC]")
    if kwargs['var']=='adc': histo.GetYaxis().SetTitle("Amplitude [ADC]")
    if kwargs['var']=='toa': histo.GetYaxis().SetTitle("TOA [ADC]")

    return canvas

def plot_langaus(histo, **kwargs):
    
    ROOT.gStyle.SetOptTitle(0)
    ROOT.gStyle.SetOptStat(0)

    canvas = ROOT.TCanvas("canvas","canvas",800, 600)
    canvas.SetFillColor(0)
    canvas.SetGrid()
    canvas.GetFrame().SetFillColor(2)
    canvas.GetFrame().SetBorderSize(12)
   
    histo.GetXaxis().SetTitle("Amplitudes [ADC]")
    histo.GetYaxis().SetTitle("No. of entries")
    histo.GetXaxis().SetLabelSize(0.05)
    histo.GetXaxis().SetTitleSize(0.05)
    histo.GetXaxis().SetNdivisions(505)
    histo.GetXaxis().SetTitleOffset(1.0)
    histo.GetYaxis().SetTitleOffset(1.0)
    histo.GetYaxis().SetLabelSize(0.05)
    histo.GetYaxis().SetTitleSize(0.05)

    histo.SetAxisRange(160, 600,"X")  #(kwargs["x_axis_range"][0], kwargs["x_axis_range"][1],"X")
    histo.SetAxisRange(kwargs["y_axis_range"][0], kwargs["y_axis_range"][1],"Y")

    histo.Draw()

    kwargs["langaus_func"].Draw("same")
    
    kwargs["legend"].SetFillStyle(0)
    #kwargs["legend"].SetHeader("For Ch:{} at ConvGain:{} and Overvoltage:{}+/-{}".format(kwargs["info_run"]['chan'], kwargs["info_run"]['convGain'],np.round(kwargs["info_run"]['SupVolt'],2), np.round(kwargs["info_run"]['SupVoltErr'],2)),"") 
    kwargs["legend"].SetTextAlign(33)
    kwargs["legend"].AddEntry(0,"fit maximum = ({}+/-{}) ADC".format(round(kwargs["fit_parameters"]['mpv_langaus'],2),round(kwargs["fit_parameters"]['mpv_langaus_err'],2)),"")
    kwargs["legend"].AddEntry(0,"pedestal = ({}+/-{})".format(round(kwargs["fit_parameters"]['pedestal'],2),round(kwargs["fit_parameters"]['pedestal_err'],2)),"")
    kwargs["legend"].AddEntry(0,"fit max. (ped subed) = ({}+/-{}) ADC".format(round(kwargs["fit_parameters"]['mpv_without_pedestal'],2),round(kwargs["fit_parameters"]['mpv_without_pedestal_err'],2)),"")
    kwargs["legend"].AddEntry(0,"fit width = ({}+/-{}) ADC".format(round(kwargs["fit_parameters"]['fit_width'],2),round(kwargs["fit_parameters"]['fit_width_err'],2)),"")
    
    if kwargs["is_irradiated"]==False: 
        kwargs["legend"].AddEntry(kwargs["langaus_func"],"Chi/NDF = {} no. of events = {}".format(round(kwargs["fit_parameters"]['chi_sq'],2),kwargs["fit_parameters"]['n_events']),"")
    if kwargs["is_irradiated"]==True: 
        kwargs["legend"].AddEntry(kwargs["langaus_func"],"Chi/NDF = {} no. of events = {} S/R = {}".format(round(kwargs["fit_parameters"]['chi_sq'],2), kwargs["fit_parameters"]['n_events'], round(kwargs["fit_parameters"]['snr'],1)))

    kwargs["legend"].SetMargin(0.1)
    kwargs["legend"].SetTextSize(0.04)
    kwargs["legend"].SetTextFont(42)
    kwargs["legend"].SetBorderSize(0)
    kwargs["legend"].Draw()
    

    #hf1 = ROOT.TFile("TB3_D8_4/fit_{}.root".format(kwargs["info_run"]['chan']), "RECREATE")
    #histo.Write()
    #kwargs["langaus_func"].Write()
    #hf1.Close()

    return canvas

def plot_pedestal(histo, **kwargs):

    ROOT.gStyle.SetOptStat(0)
    canvas = ROOT.TCanvas("canvas","canvas",800, 600)
    canvas.SetFillColor(0)
    canvas.SetGrid()
    canvas.GetFrame().SetFillColor(2)
    canvas.GetFrame().SetBorderSize(12)   

    histo.Draw()
    histo.GetXaxis().SetTitle("Pedestal Amplitude [ADC]")
    histo.GetYaxis().SetTitle("No. of entries")

    kwargs["legend"].SetHeader("For Ch:{} at ConvGain:{} and Overvoltage:{} V".format(kwargs["info_run"]['chan'], kwargs["info_run"]['convGain'],np.round(kwargs["info_run"]['SupVolt'],2)),"l") 
    kwargs["legend"].AddEntry(kwargs["func"],"Mean = ({}+/-{}) ADC".format(round(kwargs["func"].GetParameter(1),2),round(kwargs["func"].GetParError(1),2)),"l")
    kwargs["legend"].AddEntry(kwargs["func"],"Std. Dev = ({}+/-{}) ADC".format(round(kwargs["func"].GetParameter(2),2),round(kwargs["func"].GetParError(2),2)),"l")
    kwargs["legend"].SetMargin(0.1)
    kwargs["legend"].SetMargin(0.1)
    kwargs["legend"].SetTextSize(0.04)
    kwargs["legend"].SetTextFont(42)
    kwargs["legend"].SetBorderSize(0)
    kwargs["legend"].Draw()

    return canvas
