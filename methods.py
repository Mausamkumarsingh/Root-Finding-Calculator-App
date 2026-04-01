import sympy as sp
import numpy as np

class NumericalMethods:
    def __init__(self, equation_str):
        self.x = sp.Symbol('x')
        eq_clean = equation_str.replace('^', '**')
        try:
            self.expr = sp.sympify(eq_clean)
            self.deriv_expr = sp.diff(self.expr, self.x)
        except Exception as e:
            raise ValueError(f"Invalid math expression: {e}")

    def f(self, val):
        return float(self.expr.subs(self.x, val))

    def df(self, val):
        return float(self.deriv_expr.subs(self.x, val))

    def find_intervals(self, start=-15, end=15, num_points=200):
        # Auto Scanner to find roots by crossing points
        intervals = []
        x_vals = np.linspace(start, end, num_points)
        y_vals = []
        for x in x_vals:
            try: y_vals.append(self.f(x))
            except: y_vals.append(0)
            
        for i in range(len(x_vals) - 1):
            if np.sign(y_vals[i]) * np.sign(y_vals[i+1]) < 0:
                intervals.append((round(x_vals[i], 2), round(x_vals[i+1], 2)))
        return intervals

    def bisection(self, a, b, tol, max_iter):
        table = []
        steps = "--- Bisection Method Steps ---\n"
        if self.f(a) * self.f(b) >= 0:
            return None, 0, 0, [], "Failure: f(a) and f(b) must have opposite signs.", steps
            
        c = a
        for i in range(1, max_iter + 1):
            c_old = c
            fa, fb = self.f(a), self.f(b)
            c = (a + b) / 2
            fc = self.f(c)
            error = abs(c - c_old) if i > 1 else abs(b - a) / 2
            
            steps += f"Iter {i}: c = ({a:.4f} + {b:.4f}) / 2 = {c:.6f} | f(c) = {fc:.6f}\n"
            table.append({'iter': i, 'a': a, 'b': b, 'c': c, 'f(c)': fc, 'error': error})
            
            if fc == 0.0 or error < tol:
                return c, i, error, table, "Success: Converged to root.", steps
            
            if fa * fc < 0:
                steps += f"       f(a)*f(c) < 0 -> b becomes {c:.4f}\n"
                b = c
            else:
                steps += f"       f(a)*f(c) > 0 -> a becomes {c:.4f}\n"
                a = c
        return c, max_iter, error, table, "Failure: Maximum iterations reached.", steps

    def newton_raphson(self, x0, tol, max_iter):
        table = []
        steps = "--- Newton-Raphson Method Steps ---\nFormula: x_{n+1} = x_n - f(x_n)/f'(x_n)\n\n"
        x = x0
        for i in range(1, max_iter + 1):
            fx = self.f(x)
            dfx = self.df(x)
            
            if dfx == 0:
                return x, i, 0, table, "Failure: Derivative is zero.", steps
            
            x_new = x - fx / dfx
            error = abs(x_new - x)
            
            steps += f"Iter {i}: x{i} = {x:.4f} - ({fx:.4f} / {dfx:.4f}) = {x_new:.6f}\n"
            table.append({'iter': i, 'x': x, 'f(x)': fx, "f'(x)": dfx, 'x_new': x_new, 'error': error})
            
            if error < tol:
                return x_new, i, error, table, "Success: Converged to root.", steps
            if error > 1e10:
                return x_new, i, error, table, "Warning: Divergence detected (error rapidly growing).", steps
                
            x = x_new
        return x, max_iter, error, table, "Failure: Max iterations reached.", steps
        
    def secant(self, x0, x1, tol, max_iter):
        table = []
        steps = "--- Secant Method Steps ---\n"
        for i in range(1, max_iter + 1):
            fx0 = self.f(x0)
            fx1 = self.f(x1)
            if fx1 - fx0 == 0:
                return x1, i, 0, table, "Failure: Division by zero.", steps
            
            x2 = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
            error = abs(x2 - x1)
            
            steps += f"Iter {i}: x2 = {x1:.4f} - {fx1:.4f}*({x1:.4f} - {x0:.4f}) / ({fx1:.4f} - {fx0:.4f}) = {x2:.6f}\n"
            table.append({'iter': i, 'x0': x0, 'x1': x1, 'x2': x2, 'f(x2)': self.f(x2), 'error': error})
            
            if error < tol:
                return x2, i, error, table, "Success: Converged to root.", steps
            if error > 1e10:
                return x2, i, error, table, "Warning: Divergence detected (error rapidly growing).", steps
            x0, x1 = x1, x2
        return x1, max_iter, error, table, "Failure: Max iterations reached.", steps

    def false_position(self, a, b, tol, max_iter):
        table = []
        steps = "--- False Position Steps ---\n"
        if self.f(a) * self.f(b) >= 0:
            return None, 0, 0, [], "Failure: f(a) and f(b) must have opposite signs.", steps
            
        c = a
        for i in range(1, max_iter + 1):
            c_old = c
            fa, fb = self.f(a), self.f(b)
            c = (a * fb - b * fa) / (fb - fa)
            fc = self.f(c)
            error = abs(c - c_old) if i > 1 else abs(b - a)
            
            steps += f"Iter {i}: c = ({a:.2f}*{fb:.2f} - {b:.2f}*{fa:.2f}) / ({fb:.2f} - {fa:.2f}) = {c:.6f}\n"
            table.append({'iter': i, 'a': a, 'b': b, 'c': c, 'f(c)': fc, 'error': error})
            
            if fc == 0.0 or error < tol:
                return c, i, error, table, "Success: Converged to root.", steps
            if fa * fc < 0: b = c
            else: a = c
        return c, max_iter, error, table, "Failure: Max iterations reached.", steps
        
    def fixed_point(self, x0, tol, max_iter):
        table = []
        steps = "--- Fixed Point Iteration ---\ng(x) = x + f(x)\n"
        x = x0
        for i in range(1, max_iter + 1):
            gx = x + self.f(x)
            error = abs(gx - x)
            table.append({'iter': i, 'x': x, 'g(x)': gx, 'error': error})
            steps += f"Iter {i}: g({x:.4f}) = {x:.4f} + f({x:.4f}) = {gx:.6f}\n"
            if error < tol:
                return gx, i, error, table, "Success: Converged to root.", steps
            if error > 1e10:
                return gx, i, error, table, "Warning: Method diverges.", steps
            x = gx
        return x, max_iter, error, table, "Failure: Max iterations reached.", steps

    def brent(self, a, b, tol, max_iter):
        table = []
        steps = "--- Brent's Method (Pure Python Native) ---\n"
        fa = self.f(a)
        fb = self.f(b)
        
        if fa * fb >= 0:
            return None, 0, 0, [], "Failure: f(a) and f(b) must have opposite signs.", steps
            
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa
            
        c = a
        fc = fa
        mflag = True
        d = 0.0
        
        for i in range(1, max_iter + 1):
            if fa != fc and fb != fc:
                # Inverse quadratic interpolation
                s = (a * fb * fc) / ((fa - fb) * (fa - fc)) + \
                    (b * fa * fc) / ((fb - fa) * (fb - fc)) + \
                    (c * fa * fb) / ((fc - fa) * (fc - fb))
                steps += f"Iter {i}: Used Inverse Quadratic. s = {s:.6f}\n"
            else:
                # Secant method
                s = b - fb * (b - a) / (fb - fa)
                steps += f"Iter {i}: Used Secant Method. s = {s:.6f}\n"
                
            cond1 = (s < (3 * a + b) / 4) or (s > b) if a < b else (s > (3 * a + b) / 4) or (s < b)
            cond2 = mflag and (abs(s - b) >= abs(b - c) / 2)
            cond3 = not mflag and (abs(s - b) >= abs(c - d) / 2)
            cond4 = mflag and (abs(b - c) < tol)
            cond5 = not mflag and (abs(c - d) < tol)
            
            if cond1 or cond2 or cond3 or cond4 or cond5:
                s = (a + b) / 2
                mflag = True
                steps += f"       -> Setup failed, falling back to Bisection: s = {s:.6f}\n"
            else:
                mflag = False
                
            fs = self.f(s)
            d = c; c = b; fc = fb
            
            if fa * fs < 0:
                b = s; fb = fs
            else:
                a = s; fa = fs
                
            if abs(fa) < abs(fb):
                a, b = b, a; fa, fb = fb, fa
                
            error = abs(b - a) / 2
            table.append({'iter': i, 'a': a, 'b': b, 'root': b, 'f(root)': fb, 'error': error})
            
            if fb == 0.0 or error < tol:
                steps += f"\nFound Root: {b:.8f} in {i} iterations.\n"
                return b, i, error, table, "Success: Brent's Method converged.", steps
                
        return b, max_iter, error, table, "Failure: Max iterations reached.", steps
