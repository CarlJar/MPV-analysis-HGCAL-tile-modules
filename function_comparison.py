import numpy as np
from scipy.stats import norm
from landaupy import langauss as landaupy_langauss
from landaupy import landau
from LangausClass3 import Fitter
import matplotlib.pyplot as plt
from scipy.integrate import simpson
from scipy.stats import landau as landau_sp



# MAIN

# Define parameters for the comparison
mpv = 70
sigma_gauss = 16
sigma_lan = 10
area = 1
# Generate x values
x = np.linspace(0, 300, 300)
fitter = Fitter()

# Define errors for the parameters
mpv_error = 20
sigma_gauss_error = 4
sigma_lan_error = 3

# Generate parameter ranges considering errors
mpv_range = np.linspace(mpv - mpv_error, mpv + mpv_error, 20)
sigma_gauss_range = np.linspace(sigma_gauss - sigma_gauss_error, sigma_gauss + sigma_gauss_error, 20)
sigma_lan_range = np.linspace(sigma_lan - sigma_lan_error, sigma_lan + sigma_lan_error,20)

max_index = None
min_index = None
max_value = -np.inf
min_value = np.inf

max_argmax_value = -np.inf
min_argmax_value = np.inf

# Store all resulting values
results = []
indx=[]

# Iterate over all combinations of parameter values
for mpv_val in mpv_range:
    for sigma_gauss_val in sigma_gauss_range:
        for sigma_lan_val in sigma_lan_range:
            # print(mpv_val, sigma_gauss_val, sigma_lan_val)
            y_langauss = landaupy_langauss.pdf(x, mpv_val, sigma_lan_val, sigma_gauss_val)
            max_idx = np.argmax(y_langauss)
            max_val = y_langauss[max_idx]
            results.append([mpv_val, sigma_lan_val, sigma_gauss_val, x[max_idx], max_val])
            indx.append(max_idx)
            # print(max_idx)
            # print(max_val)
            

results=np.array(results)

# print(results[:,3])
i_max=np.argmax(results[:,3])
i_min=np.argmin(results[:,3])

max_x=results[i_max][3]
min_x=results[i_min][3]

print('results_min')
print(results[i_min,:])

print('results_max')
print(results[i_max,:])

print('mu range',mpv - mpv_error, mpv + mpv_error)
print('sigma_lan range',sigma_lan - sigma_lan_error, sigma_lan + sigma_lan_error)
print('sigma_gauss',sigma_gauss - sigma_gauss_error, sigma_gauss + sigma_gauss_error)


# print(i_min,i_max)
# print(min_x,max_x)
# print(results[i_max],results[i_min])

# print(f"Highest argmax value: {highest_index}, Value: {results[highest_index][3]}, Parameters: {hightest_results}")
# print(f"Lowest argmax value: {lowest_index}, Value: {results[lowest_index][3]}, Parameters: {lowest_results}")


y_langauss = landaupy_langauss.pdf(x, mpv, sigma_lan, sigma_gauss)
plt.figure(figsize=(10, 6))
plt.plot(x, y_langauss, label='Ideal landaupy langauss', marker='.', color='red', linestyle='None')

# Plot the function with the highest argmax value

y_langauss_max = landaupy_langauss.pdf(x, *results[i_max,:3])
plt.plot(x, y_langauss_max, label='Highest argmax landaupy langauss', linestyle='-', color='blue')
plt.axvline(max_x, color='blue', linestyle='-')

# Plot the function with the lowest argmax value
y_langauss_min = landaupy_langauss.pdf(x, *results[i_min,:3])
plt.plot(x, y_langauss_min, label='Lowest argmax landaupy langauss', linestyle='--', color='green')
plt.axvline(min_x, color='green', linestyle='--')

plt.xlabel('x')
plt.ylabel('Probability Density')
plt.title('Comparison of Langauss Function Implementations')
plt.legend()
plt.grid(True)


#Extra case:
res2=[]

for sigma_lan_val in sigma_lan_range:
    y_langauss = landaupy_langauss.pdf(x, mpv, sigma_lan_val, sigma_gauss)
    max_idx = np.argmax(y_langauss)
    max_val = y_langauss[max_idx]
    res2.append([mpv, sigma_lan_val, sigma_gauss, x[max_idx], max_val])

res2=np.array(res2)

print(res2[:,3], res2[:,1])


print('Variation of sigma_lan doesnt affect the argmax value:') 
print('============================================================')

print('(argmax, sigma_lan)')
for sigma_lan_val in sigma_lan_range:
    y_langauss = landaupy_langauss.pdf(x, mpv, sigma_lan_val, sigma_gauss)
    max_idx = np.argmax(y_langauss)
    max_val = y_langauss[max_idx]
    max_x = x[max_idx] 
    print((sigma_lan_val, max_x))
    

    
plt.show()
