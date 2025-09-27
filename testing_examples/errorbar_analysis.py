import numpy as np
from landaupy import langauss as landaupy_langauss

import matplotlib.pyplot as plt

# Define the langaus function
def langaus(x, mpv, sigma_lan, sigma_gauss):
    return landaupy_langauss.pdf(x, mpv, sigma_lan, sigma_gauss)

# Define parameters
mpv = 70
sigma_gauss = 16
sigma_lan = 10

# Generate x values
x = np.linspace(0, 300, 300)

# Plot the original langaus function
y_original = langaus(x, mpv, sigma_lan, sigma_gauss)

# Create subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 15))

# Plot the original langaus function
axs[0].plot(x, y_original, label=f'Original mpv={mpv}', color='red')
axs[1].plot(x, y_original, label=f'Original sigma_gauss={sigma_gauss}', color='red')
axs[2].plot(x, y_original, label=f'Original sigma_lan={sigma_lan}', color='red')

# Change mpv and plot
mpv_new = 90
mpv_smaller = 50
y_mpv_changed = langaus(x, mpv_new, sigma_lan, sigma_gauss)
y_mpv_smaller = langaus(x, mpv_smaller, sigma_lan, sigma_gauss)
axs[0].plot(x, y_mpv_changed, label=f'mpv={mpv_new}', linestyle='--', color='blue')
axs[0].plot(x, y_mpv_smaller, label=f'mpv={mpv_smaller}', linestyle=':', color='green')
axs[0].set_title('Change in mpv')
axs[0].legend()
axs[0].grid(True)

# Change sigma_gauss and plot
sigma_gauss_new = 20
sigma_gauss_smaller = 12
y_sigma_gauss_changed = langaus(x, mpv, sigma_lan, sigma_gauss_new)
y_sigma_gauss_smaller = langaus(x, mpv, sigma_lan, sigma_gauss_smaller)
axs[1].plot(x, y_sigma_gauss_changed, label=f'sigma_gauss={sigma_gauss_new}', linestyle='--', color='blue')
axs[1].plot(x, y_sigma_gauss_smaller, label=f'sigma_gauss={sigma_gauss_smaller}', linestyle=':', color='green')
axs[1].set_title('Change in sigma_gauss')
axs[1].legend()
axs[1].grid(True)

# Change sigma_lan and plot
sigma_lan_new = 15
sigma_lan_smaller = 5
y_sigma_lan_changed = langaus(x, mpv, sigma_lan_new, sigma_gauss)
y_sigma_lan_smaller = langaus(x, mpv, sigma_lan_smaller, sigma_gauss)
axs[2].plot(x, y_sigma_lan_changed, label=f'sigma_lan={sigma_lan_new}', linestyle='--', color='blue')
axs[2].plot(x, y_sigma_lan_smaller, label=f'sigma_lan={sigma_lan_smaller}', linestyle=':', color='green')
axs[2].set_title('Change in sigma_lan')
axs[2].legend()
axs[2].grid(True)

# Add labels
for ax in axs:
    ax.set_xlabel('x')
    ax.set_ylabel('Probability Density')

plt.tight_layout()
plt.show()