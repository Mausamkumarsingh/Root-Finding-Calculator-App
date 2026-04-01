# Root Finding Calculator App - Numerical Methods Solver

## 📈 Objective
A production-quality, modern, and user-friendly desktop application to calculate the roots of nonlinear equations using various numerical methods. Built primarily for educational and professional use, this application presents an intuitive layout alongside comprehensive visualizations of mathematical convergence.

---

## 🚀 Features

**1. Four Core Numerical Methods:**
*   **Bisection Method** (Requires interval `[a, b]`)
*   **Newton-Raphson Method** (Requires an initial guess `x0` and computable derivative)
*   **Secant Method** (Requires two initial guesses `x0` & `x1`)
*   **False Position (Regula Falsi) Method** (Requires interval `[a, b]`)

**2. Modern, Responsive GUI**
*   Built using `CustomTkinter` for a sleek dark/light mode adaptable interface.
*   Clean panels separating Inputs from Results.
*   Helpful dynamic UI logic that adapts input fields based on the selected method.

**3. Data Visualization & Analytics**
*   **Interactive Data Grid:** A responsive treeview that displays iteration-by-iteration progress (step, root approx, f(x), error margin).
*   **Function Plotting:** A Matplotlib integration plots the primary function `f(x)` and clearly marks the converged root.
*   **Convergence Metric:** A logarithmic error-iteration graph to visualize method convergence rate.

**4. Advanced Export & Error Handling**
*   Safely parses mathematical inputs using `SymPy` (`x**3 - x - 2`, `sin(x)`, `exp(x)`).
*   Catches common numerical errors (like generic divide by zero, or diverging solutions).
*   **Export Results:** Download the iteration table to `.csv` format for post-calculation analysis.

---

## 🛠️ Installation & Setup

Ensure you have Python 3.8+ installed on your system.

**1. Clone or Download the repository.**

**2. Install dependencies:**
Navigate to the project folder and run:
```bash
pip install -r requirements.txt
```

**3. Run the application:**
```bash
python main.py
```

---

## 📖 How to Use

1. **Equation:** Enter your equation in terms of `x` (e.g., `x**3 - x - 2`). Note: Use `**` for exponentiation, not `^`.
2. **Method:** Select a numerical method from the dropdown. 
3. **Guesses:** Input your initial bounds or guess based on the method:
   * *Bisection & False Position:* Ensure the root lies between your `a` and `b` (meaning `f(a) * f(b) < 0`).
   * *Newton-Raphson:* Provide a good initial guess `x0`.
   * *Secant:* Provide `x0` and `x1`.
4. **Settings:** Define your tolerance (e.g., `0.0001`) and the maximum allowed iterations limit.
5. **Calculate:** Hit "Calculate Root" to solve. Results, iteration tables, and plots will render on the right panel.
6. **Export:** Click `Export CSV` in the top right of the Results Panel to save a copy of the iterations table!

---

## 🧩 Project Structure
* `main.py` - Core application layout, UI management, and event loops.
* `methods.py` - Separation of logic. Handles equation parsing with `SymPy` and all underlying mathematical algorithms.
* `plotter.py` - Handles generation of `matplotlib` plots and their embedding into the tkinter canvas.
* `requirements.txt` - Project dependencies.

---

> Built with ❤️ for Numerical Methods students & enthusiasts.
