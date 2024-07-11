import numpy as np
import matplotlib.pyplot as plt

# Constants
delta = 3  # Replace with the appropriate value of delta

# Function definition
def psi(x):
    norm_x = np.linalg.norm(x)
    if norm_x >= delta:
        return x / np.linalg.norm(x)**3
    elif 0 < norm_x < delta:
        return x / (np.linalg.norm(x) * delta**2)
    else:
        return np.zeros_like(x)

# Generate data for plotting
x_positive = np.linspace(1e-9, 10, 400)  # Start from a very small positive value
y_positive = np.zeros_like(x_positive)
for i, xi in enumerate(x_positive):
    y_positive[i] = psi(np.array([xi]))


# Plotting
plt.figure(figsize=(8, 6))
plt.plot(x_positive, y_positive, label='$\psi(x)$ for $x > 0$ and $\delta = 3$')
plt.scatter([0], [psi(np.array([1e-9]))], color='red', label='Discontinuity at $x=0$')
# plt.scatter([0], [0], color='red', label='Discontinuity at $x=0$')
plt.xlabel('$x$', fontsize=20)
plt.ylabel('$\psi(x)$', fontsize=20)
plt.xticks([0,3,10])
plt.gca().tick_params(axis='x', labelsize=16)
plt.yticks([0,0.01, 1/9])
plt.gca().tick_params(axis='y', labelsize=16)

# plt.title('Plot of psi(x) for x > 0')
plt.grid(True)
plt.tight_layout()
plt.legend(fontsize=16, framealpha=1.0)
plt.savefig('fig.pdf')