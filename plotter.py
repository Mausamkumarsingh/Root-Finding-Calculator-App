import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np

class Plotter:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Create figure with modern dark professional style
        self.fig = Figure(figsize=(8, 10), dpi=100, facecolor='#1b1b1b')
        self.ax1 = self.fig.add_subplot(211, facecolor='#202020')
        self.ax2 = self.fig.add_subplot(212, facecolor='#202020')
        self.fig.tight_layout(pad=4.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add Toolbar for Interactive Zoom, Pan, Save
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent_frame)
        self.toolbar.update()
        self.toolbar.pack(side="bottom", fill="x")
        # Style Toolbar
        self.toolbar.config(background='#1b1b1b')
        for button in self.toolbar.winfo_children():
            button.config(background='#1b1b1b')

        self._set_axes_styles()
        self.canvas.draw()

    def plot_results(self, f_func, root, table, method_name, a, b, all_roots_intervals=None):
        self.ax1.clear()
        self.ax2.clear()
        
        self._set_axes_styles()
        
        # Function Plotting Setup
        if table:
            x_vals_in_table = [row.get('x0', row.get('a', root)) for row in table] + \
                              [row.get('x1', row.get('b', root)) for row in table] + \
                              [row.get('c', row.get('x', row.get('x2', root))) for row in table]
            x_vals_in_table = [v for v in x_vals_in_table if v is not None]
            if x_vals_in_table:
                first_x = min(x_vals_in_table)
                last_x = max(x_vals_in_table)
            else:
                first_x, last_x = a, b
        else:
            first_x, last_x = a, b
            
        if first_x is None: first_x = -10
        if last_x is None: last_x = 10
        if first_x == last_x:
            first_x -= 5
            last_x += 5
            
        margin = abs(last_x - first_x) * 0.3
        if margin == 0: margin = 2
            
        x_vals = np.linspace(first_x - margin, last_x + margin, 500)
        y_vals = []
        for x in x_vals:
            try:
                y_vals.append(f_func(x))
            except Exception:
                y_vals.append(np.nan)
                
        # 1. Plot Function
        for alpha, width in [(0.1, 6), (0.2, 4), (0.5, 2)]:
            self.ax1.plot(x_vals, y_vals, color='#4dd0e1', linewidth=width, alpha=alpha)
        self.ax1.plot(x_vals, y_vals, label='f(x)', color='#80deea', linewidth=1.5)
        
        self.ax1.axhline(0, color='#666666', linestyle='--', linewidth=1)
        self.ax1.axvline(0, color='#666666', linestyle='--', linewidth=1)

        # Plot all potential roots from auto scanner
        if all_roots_intervals:
            for (ra, rb) in all_roots_intervals:
                mid = (ra + rb) / 2
                self.ax1.plot(mid, 0, marker='x', color='orange', markersize=6, alpha=0.7)
            self.ax1.plot([], [], marker='x', color='orange', linestyle='None', label=f'Other Possible Roots ({len(all_roots_intervals)})')

        if root is not None:
            self.ax1.plot(root, 0, marker='o', color='#ff4081', markersize=8, markeredgecolor='white', label=f'Target Root: {root:.5f}', zorder=5)
            self.ax1.annotate(f'({root:.4f}, 0)', xy=(root, 0), xytext=(root, max(y_vals)*0.1 if max(y_vals) > 0 else 1),
                              textcoords='data', color='#ff4081', ha='center',
                              arrowprops=dict(arrowstyle="->", color='#ff4081'))
            
        self.ax1.set_title(f'Interactive Function Graph', color='white', fontsize=12, pad=10)
        self.ax1.set_xlabel('x', color='#aaaaaa', fontsize=10)
        self.ax1.set_ylabel('f(x)', color='#aaaaaa', fontsize=10)
        self.ax1.legend(facecolor='#1b1b1b', edgecolor='#333333', labelcolor='white')
        self.ax1.grid(True, color='#333333', linestyle=':', alpha=0.7)
        
        # 2. Plot Convergence
        if table and 'error' in table[0]:
            iters = [row['iter'] for row in table if 'error' in row]
            errors = [row['error'] for row in table if 'error' in row]
            
            self.ax2.plot(iters, errors, marker='D', markersize=5, color='#ff5252', linestyle='-', linewidth=2, label='Error per Iteration')
            self.ax2.set_title('Convergence Graph (Error vs Iteration)', color='white', fontsize=12, pad=10)
            self.ax2.set_xlabel('Iteration', color='#aaaaaa', fontsize=10)
            self.ax2.set_ylabel('Error Margin', color='#aaaaaa', fontsize=10)
            self.ax2.set_yscale('log')
            self.ax2.grid(True, which="both", ls=":", color='#333333', alpha=0.7)
            self.ax2.legend(facecolor='#1b1b1b', edgecolor='#333333', labelcolor='white')
            
        self.canvas.draw()
        
    def _set_axes_styles(self):
        for ax in [self.ax1, self.ax2]:
            ax.tick_params(colors='#aaaaaa', labelsize=9)
            for spine in ax.spines.values():
                spine.set_color('#444444')
