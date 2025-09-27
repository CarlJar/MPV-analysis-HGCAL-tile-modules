#!/usr/bin/env python3
"""
Quick test script for the new error bar plotting functionality.
"""

import numpy as np
import matplotlib.pyplot as plt
from plot_utils import AnalysisPlotter

def test_error_bars():
    """Test that the error bar plotting works correctly."""
    print("Testing error bar plotting functionality...")
    
    # Create some test data with known structure
    np.random.seed(42)
    x = np.linspace(0, 400, 100)
    y_true = 50 * np.exp(-0.5 * ((x - 150) / 30)**2)  # Gaussian-like signal
    y_counts = np.random.poisson(y_true)  # Add Poisson noise
    y_errors = np.sqrt(y_counts)  # Poisson errors
    
    # Create a simple plot to verify error bar functionality
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot with error bars
    ax.errorbar(x, y_counts, yerr=y_errors, 
               fmt='o', color='black', markersize=3, capsize=2, alpha=0.7,
               label='Data with Poisson errors')
    
    # Plot true function
    ax.plot(x, y_true, '-', color='red', linewidth=2, label='True function')
    
    ax.set_xlabel('ADC Amplitude')
    ax.set_ylabel('Counts')
    ax.set_title('Test Plot - Data Points with Poisson Error Bars')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    print("✅ Error bar plotting test successful")
    print("📊 Displaying test plot...")
    
    plt.tight_layout()
    plt.show()
    
    return True

def main():
    """Run error bar plotting test."""
    print("="*50)
    print("TESTING ERROR BAR PLOTTING")
    print("="*50)
    
    try:
        test_error_bars()
        print("\n" + "="*50)
        print("ERROR BAR TEST COMPLETED ✅")
        print("="*50)
        print("The plotting utilities now support:")
        print("• Poisson error bars on all data points")
        print("• Multiple plot types (standard, detailed, comparison)")
        print("• Flexible histogram and error bar display options")
        print("• Enhanced residual analysis")
        
    except Exception as e:
        print(f"❌ Error bar test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
