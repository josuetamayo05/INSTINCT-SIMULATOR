import matplotlib.pyplot as plt
import numpy as np


# Parámetros
def f(t, A):
    if t < 5:
        return 0.03 * A
    else:
        return 0.03 * A - 600


dt = 0.1
t_max = 15
pasos = int(t_max / dt)

t_num = np.linspace(0, t_max, pasos + 1)
A_num = np.zeros(pasos + 1)
A_num[0] = 8000

# Método de Euler
for n in range(pasos):
    A_num[n + 1] = A_num[n] + f(t_num[n], A_num[n]) * dt

# Solución Analítica
A_exacta = np.where(
    t_num <= 5,
    8000 * np.exp(0.03 * t_num),
    20000 - 10705.33 * np.exp(0.03 * (t_num - 5)),
)

# Gráfica
plt.figure(figsize=(9, 5))
plt.plot(t_num, A_exacta, "b-", label="Solución Analítica", linewidth=2)
plt.plot(
    t_num, A_num, "r--", label="Método de Euler (Δt = 0.1)", linewidth=1.5
)
plt.axvline(
    x=5,
    color="gray",
    linestyle=":",
    label="Inicio de retiros ($600/año en t=5)",
)
plt.title(
    "Evolución del Saldo de la Cuenta A(t): Analítico vs Numérico", fontsize=12
)
plt.xlabel("Tiempo (Años)", fontsize=11)
plt.ylabel("Saldo ($)", fontsize=11)
plt.grid(True)
plt.legend()
plt.show()