import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import threading
import time
import json
import os
from fpdf import FPDF
from methods import NumericalMethods
from plotter import Plotter

# Setup global theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Numerical Analysis Pro | Premium Root Finder")
        self.geometry("1300x850")
        self.minsize(1200, 700)
        
        # Color Palette inspired by glassmorphism & dark UI
        self.colors = {
            "bg": "#121212",
            "sidebar": "#1e1e24",
            "card_bg": "#25252b",
            "card_hover": "#2e2e36",
            "accent1": "#4dd0e1", # Cyan
            "accent2": "#ff4081", # Pink 
            "accent3": "#7c4dff", # Purple
            "text": "#e0e0e0",
            "text_muted": "#888888",
            "success": "#00e676",
            "error": "#ff5252"
        }
        self.configure(fg_color=self.colors["bg"])

        # Main Layout: 1x2 Grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=400) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Results Panel

        self.method_var = ctk.StringVar(value="Bisection Method")
        self.current_table = []
        self.current_result_text = ""
        self.current_eq_img = ""
        
        self._create_input_panel()
        self._create_results_panel()
        self._toggle_inputs()
        
    def _create_input_panel(self):
        self.sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color=self.colors["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Header + Theme Toggle
        top_bar = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        top_bar.pack(fill="x", pady=(20, 10), padx=20)
        
        ctk.CTkLabel(top_bar, text="⚡", font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(top_bar, text=" Numerical Pro", 
                     font=ctk.CTkFont(size=24, weight="bold", family="Roboto"), 
                     text_color=self.colors["accent1"]).pack(side="left", padx=5)
                     
        self.theme_btn = ctk.CTkButton(top_bar, text="🌞", width=30, height=30, fg_color="transparent",
                                       hover_color=self.colors["card_hover"], command=self._toggle_theme)
        self.theme_btn.pack(side="right")
                     
        ctk.CTkLabel(self.sidebar, text="Equation & Settings", text_color=self.colors["text_muted"], 
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=30, pady=(5, 5))

        # Equation Input
        eq_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        eq_frame.pack(fill="x", padx=30, pady=5)
        self.entry_eq = ctk.CTkEntry(eq_frame, placeholder_text="e.g. x**3 - x - 2", 
                                     height=40, font=ctk.CTkFont(size=14, family="Consolas"), 
                                     border_color=self.colors["accent1"], border_width=1)
        self.entry_eq.pack(side="left", fill="x", expand=True)
        self.entry_eq.insert(0, "x**3 - x - 2")
        
        self.btn_mic = ctk.CTkButton(eq_frame, text="🎤", width=40, height=40, 
                                     fg_color=self.colors["card_hover"], hover_color=self.colors["accent2"],
                                     command=self._on_voice_input)
        self.btn_mic.pack(side="right", padx=(5, 0))

        # Method Selection
        methods = ["Bisection Method", "Newton-Raphson Method", "Secant Method", 
                   "False Position Method", "Fixed Point Iteration", "Brent's Method"]
        self.opt_method = ctk.CTkOptionMenu(self.sidebar, values=methods, variable=self.method_var, 
                                            command=self._toggle_inputs, height=40, 
                                            fg_color=self.colors["card_bg"], button_color=self.colors["card_hover"],
                                            button_hover_color=self.colors["accent1"])
        self.opt_method.pack(pady=10, padx=30, fill="x")
        
        # Two Column Frame for Inputs
        self.input_grid = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.input_grid.pack(fill="x", padx=30, pady=5)
        self.input_grid.columnconfigure((0, 1), weight=1)
        
        # Guesses
        g1_frame = ctk.CTkFrame(self.input_grid, fg_color="transparent")
        g1_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.lbl_g1 = ctk.CTkLabel(g1_frame, text="x0 / a:", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.colors["text_muted"])
        self.lbl_g1.pack(anchor="w")
        self.entry_g1 = ctk.CTkEntry(g1_frame, height=35)
        self.entry_g1.pack(fill="x", pady=(2, 5))
        self.entry_g1.insert(0, "1.0")
        
        self.g2_frame = ctk.CTkFrame(self.input_grid, fg_color="transparent")
        self.g2_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        self.lbl_g2 = ctk.CTkLabel(self.g2_frame, text="x1 / b:", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.colors["text_muted"])
        self.lbl_g2.pack(anchor="w")
        self.entry_g2 = ctk.CTkEntry(self.g2_frame, height=35)
        self.entry_g2.pack(fill="x", pady=(2, 5))
        self.entry_g2.insert(0, "2.0")
        
        # Smart Suggestion Feature
        self.btn_suggest = ctk.CTkButton(self.input_grid, text="🔍 Auto-Suggest Interval", 
                                        fg_color=self.colors["card_hover"], hover_color="#3a3a44",
                                        command=self._auto_suggest_interval)
        self.btn_suggest.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 15))
        
        # Tolerance & Iterations
        t_frame = ctk.CTkFrame(self.input_grid, fg_color="transparent")
        t_frame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(t_frame, text="Tolerance:", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.colors["text_muted"]).pack(anchor="w")
        self.entry_tol = ctk.CTkEntry(t_frame, height=35)
        self.entry_tol.pack(fill="x", pady=(2, 5))
        self.entry_tol.insert(0, "0.0001")
        
        i_frame = ctk.CTkFrame(self.input_grid, fg_color="transparent")
        i_frame.grid(row=2, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkLabel(i_frame, text="Max Iterations:", font=ctk.CTkFont(size=13, weight="bold"), text_color=self.colors["text_muted"]).pack(anchor="w")
        self.entry_iter = ctk.CTkEntry(i_frame, height=35)
        self.entry_iter.pack(fill="x", pady=(2, 5))
        self.entry_iter.insert(0, "50")
        
        # Progress Bar for loading
        self.progressbar = ctk.CTkProgressBar(self.sidebar, mode="indeterminate", height=3, progress_color=self.colors["accent1"])
        self.progressbar.pack(padx=30, pady=(15, 0), fill="x")
        self.progressbar.set(0) # Hide visually initially 

        # Primary Actions
        self.btn_calc = ctk.CTkButton(self.sidebar, text="▶ Calculate Method", font=ctk.CTkFont(size=16, weight="bold"),
                                      height=45, fg_color=self.colors["accent1"], hover_color="#2b99de", 
                                      text_color="black", command=self._on_calculate)
        self.btn_calc.pack(pady=(20, 10), padx=30, fill="x")
        
        self.btn_comp = ctk.CTkButton(self.sidebar, text="📊 Run Comparison", font=ctk.CTkFont(size=15, weight="bold"),
                                      height=45, fg_color=self.colors["accent3"], hover_color="#5e35b1", 
                                      command=self._on_compare)
        self.btn_comp.pack(pady=5, padx=30, fill="x")
        
        # Status Label
        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Ready", text_color=self.colors["text_muted"], font=ctk.CTkFont(size=13))
        self.lbl_status.pack(pady=(5, 10), padx=30)
        
        # Bottom Utility Actions 
        utility_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        utility_frame.pack(side="bottom", fill="x", padx=30, pady=20)
        
        self.btn_save_sess = ctk.CTkButton(utility_frame, text="💾 Save", width=80, fg_color="transparent", 
                                       border_width=1, border_color=self.colors["card_hover"], command=self._save_session)
        self.btn_save_sess.pack(side="left", padx=(0, 5))
        
        self.btn_load_sess = ctk.CTkButton(utility_frame, text="📂 Load", width=80, fg_color="transparent", 
                                       border_width=1, border_color=self.colors["card_hover"], command=self._load_session)
        self.btn_load_sess.pack(side="left")
        
        self.btn_reset = ctk.CTkButton(utility_frame, text="🔄 Reset", width=80, fg_color="transparent", 
                                       border_width=1, border_color=self.colors["error"], hover_color="#441111", command=self._on_reset)
        self.btn_reset.pack(side="right")

    def _create_results_panel(self):
        self.results_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.results_frame.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Top Metrics Section (Glassmorphism Cards)
        self.metrics_grid = ctk.CTkFrame(self.results_frame, height=120, fg_color="transparent")
        self.metrics_grid.grid(row=0, column=0, sticky="new", pady=(0, 20))
        self.metrics_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._create_metric_card(self.metrics_grid, 0, "🎯 Final Root", "lbl_res_root", "--", self.colors["accent1"])
        self._create_metric_card(self.metrics_grid, 1, "🔄 Iterations", "lbl_res_iter", "--", self.colors["accent2"])
        self._create_metric_card(self.metrics_grid, 2, "📉 Error Margin", "lbl_res_err", "--", self.colors["accent3"])
        
        # Central Tab View
        self.tabview = ctk.CTkTabview(self.results_frame, corner_radius=12, fg_color=self.colors["card_bg"],
                                      segmented_button_selected_color=self.colors["accent1"], 
                                      segmented_button_selected_hover_color="#2b99de",
                                      segmented_button_fg_color=self.colors["sidebar"])
        self.tabview.grid(row=1, column=0, sticky="nsew")
        
        self.tabview.add("📊 Data Table")
        self.tabview.add("📉 Visual Graphs")
        self.tabview.add("📝 Step-by-Step")
        self.tabview.add("📈 Method Comparison")
        
        self._setup_table_tab()
        self._setup_graph_tab()
        self._setup_step_tab()
        self._setup_comparison_tab()

    def _create_metric_card(self, parent, col, title, attr_name, default_val, accent_color):
        card = ctk.CTkFrame(parent, corner_radius=12, fg_color=self.colors["card_bg"], 
                            border_width=1, border_color=self.colors["card_hover"])
        card.grid(row=0, column=col, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text_muted"]).pack(pady=(15, 5))
        lbl = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont(size=26, weight="bold"), text_color=accent_color)
        lbl.pack(pady=(0, 15))
        setattr(self, attr_name, lbl)

    def _setup_table_tab(self):
        tab = self.tabview.tab("📊 Data Table")
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        # Export Actions Area
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        btn_pdf = ctk.CTkButton(top, text="📄 PDF Report", width=120, fg_color="#d32f2f", 
                                   hover_color="#9a0007", command=self._export_pdf)
        btn_pdf.pack(side="right", padx=10)
        btn_csv = ctk.CTkButton(top, text="💾 CSV Export", width=120, fg_color="#2da44e", 
                                   hover_color="#2c974b", command=self._export_csv)
        btn_csv.pack(side="right")
        
        tv_frame = ctk.CTkFrame(tab, corner_radius=10, fg_color=self.colors["sidebar"])
        tv_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tv_frame.grid_rowconfigure(0, weight=1)
        tv_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = self._create_treeview(tv_frame, ("iter", "value", "error"))
        
        # Tags for smart highlighting
        self.tree.tag_configure('highlight', background='#175124', foreground='#e0e0e0') # Dark Green target
        self.tree.tag_configure('unstable', background='#601111', foreground='#e0e0e0') # Dark Red divergence

    def _setup_comparison_tab(self):
        tab = self.tabview.tab("📈 Method Comparison")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        
        tv_frame = ctk.CTkFrame(tab, corner_radius=10, fg_color=self.colors["sidebar"])
        tv_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=20)
        tv_frame.grid_rowconfigure(0, weight=1)
        tv_frame.grid_columnconfigure(0, weight=1)
        
        self.comp_tree = self._create_treeview(tv_frame, ("Method", "Root", "Iterations", "Error", "Status"))
        self.comp_tree.column("Method", width=220, anchor="w")
        self.comp_tree.column("Status", width=260, anchor="w")
        
    def _create_treeview(self, parent, columns):
        style = ttk.Style()
        style.theme_use("default")
        
        bg_col = self.colors["sidebar"]
        selected = self.colors["card_hover"]
        
        style.configure("Custom.Treeview",
                        background=bg_col, foreground="white",
                        fieldbackground=bg_col, rowheight=35,
                        borderwidth=0, bordercolor=bg_col,
                        font=('Roboto', 11))
                        
        style.map('Custom.Treeview', background=[('selected', selected)])
        style.configure("Custom.Treeview.Heading",
                        background=self.colors["card_bg"], foreground=self.colors["text_muted"],
                        relief="flat", font=('Roboto', 11, 'bold'))
        style.map("Custom.Treeview.Heading", background=[('active', selected)])
        
        tree = ttk.Treeview(parent, columns=columns, show="headings", style="Custom.Treeview")
        for col in columns:
            tree.heading(col, text=col.upper())
            tree.column(col, anchor="center")
            
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        return tree

    def _setup_graph_tab(self):
        tab = self.tabview.tab("📉 Visual Graphs")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.plotter = Plotter(tab)

    def _setup_step_tab(self):
        tab = self.tabview.tab("📝 Step-by-Step")
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.txt_steps = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=13),
                                        fg_color=self.colors["sidebar"], text_color="#d6deeb")
        self.txt_steps.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text="🌙")
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text="🌞")

    def _toggle_inputs(self, *args):
        method = self.method_var.get()
        if method in ["Newton-Raphson Method", "Fixed Point Iteration"]:
            self.lbl_g1.configure(text="Initial x0:")
            self.g2_frame.grid_remove() # hide entirely
        else:
            if method in ["Bisection Method", "False Position Method", "Brent's Method"]:
                self.lbl_g1.configure(text="Bound a:")
                self.lbl_g2.configure(text="Bound b:")
            elif method == "Secant Method":
                self.lbl_g1.configure(text="Initial x0:")
                self.lbl_g2.configure(text="Initial x1:")
                
            self.g2_frame.grid()

    def _translate_spoken_math(self, text):
        import re
        text = text.lower()
        replacements = [
            ("cubed", "**3"), ("cube", "**3"), ("squared", "**2"), ("square", "**2"),
            ("minus", "-"), ("plus", "+"), ("times", "*"), ("multiplied by", "*"),
            ("divided by", "/"), ("over", "/"), ("to the power of", "**"), ("power", "**"),
            ("equal to zero", ""), ("equals zero", ""), ("is zero", ""),
            ("one", "1"), ("two", "2"), ("three", "3"), ("four", "4"), ("five", "5"),
            ("six", "6"), ("seven", "7"), ("eight", "8"), ("nine", "9"), ("zero", "0"),
            ("y equals", ""), ("f of x equals", "")
        ]
        for word, symbol in replacements:
            text = text.replace(word, symbol)
            
        text = " ".join(text.split())
        return text

    def _on_voice_input(self):
        self._initiate_loading("Listening to voice... Speak now!")
        
        def _listen():
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio)
                parsed_eq = self._translate_spoken_math(text)
                self.after(0, self._apply_voice_result, text, parsed_eq)
            except ImportError:
                self.after(0, self._stop_loading, "Microphone package missing.", False)
                self.after(0, self._fallback_nlp_dialog)
            except Exception as e:
                self.after(0, self._stop_loading, f"Voice error. Fallback to NLP.", False)
                self.after(0, self._fallback_nlp_dialog)

        threading.Thread(target=_listen, daemon=True).start()
        
    def _fallback_nlp_dialog(self):
        dialog = ctk.CTkInputDialog(text="Type spoken math naturally:\n(e.g. 'x cube minus x minus 2')", title="NLP Math Parser")
        text = dialog.get_input()
        if text:
            parsed = self._translate_spoken_math(text)
            self._apply_voice_result(text, parsed)

    def _apply_voice_result(self, raw_text, parsed_eq):
        self._stop_loading(f"Parsed: '{parsed_eq}'", True)
        self.entry_eq.delete(0, 'end')
        self.entry_eq.insert(0, parsed_eq)

    def _auto_suggest_interval(self):
        eq = self.entry_eq.get().strip()
        if not eq:
            messagebox.showwarning("Empty Equation", "Please enter an equation first.")
            return
        
        self._initiate_loading("Scanning limits for root crossovers...")
        
        def _scan():
            try:
                solver = NumericalMethods(eq)
                intervals = solver.find_intervals(-20, 20, 400)
                if not intervals:
                    self.after(0, self._stop_loading, "No valid crossover intervals found in [-20, 20].", False)
                    return
                # Take first interval
                best = intervals[0]
                self.after(0, self._apply_suggestion, best)
            except Exception as e:
                self.after(0, self._handle_error, str(e))
                
        threading.Thread(target=_scan, daemon=True).start()
        
    def _apply_suggestion(self, interval):
        self._stop_loading(f"Suggestion applied: [{interval[0]}, {interval[1]}]", True)
        if self.method_var.get() not in ["Newton-Raphson Method", "Fixed Point Iteration"]:
            self.entry_g1.delete(0, 'end'); self.entry_g1.insert(0, str(interval[0]))
            self.entry_g2.delete(0, 'end'); self.entry_g2.insert(0, str(interval[1]))
        else:
            self.entry_g1.delete(0, 'end'); self.entry_g1.insert(0, str(interval[0]))
            
        # Temporarily flash the entries
        self.entry_g1.configure(border_color=self.colors["success"])
        if getattr(self, "g2_frame").winfo_ismapped():
            self.entry_g2.configure(border_color=self.colors["success"])
        self.after(1000, lambda: self.entry_g1.configure(border_color=self.colors["text_muted"]))
        self.after(1000, lambda: self.entry_g2.configure(border_color=self.colors["text_muted"]))

    def _on_reset(self):
        self.entry_eq.delete(0, 'end')
        self.entry_g1.delete(0, 'end')
        self.entry_g2.delete(0, 'end')
        self.entry_tol.delete(0, 'end')
        self.entry_iter.delete(0, 'end')
        
        self.entry_eq.insert(0, "")
        self.entry_tol.insert(0, "0.0001")
        self.entry_iter.insert(0, "50")
        
        self.lbl_res_root.configure(text="--")
        self.lbl_res_iter.configure(text="--")
        self.lbl_res_err.configure(text="--")
        
        for item in self.tree.get_children(): self.tree.delete(item)
        for item in self.comp_tree.get_children(): self.comp_tree.delete(item)
            
        self.txt_steps.delete("1.0", "end")
        self.lbl_status.configure(text="Ready", text_color=self.colors["text_muted"])
        
        self.plotter.ax1.clear()
        self.plotter.ax2.clear()
        self.plotter._set_axes_styles()
        self.plotter.canvas.draw()
        
    def _save_session(self):
        data = {
            "eq": self.entry_eq.get(), "method": self.method_var.get(),
            "g1": self.entry_g1.get(), "g2": self.entry_g2.get(),
            "tol": self.entry_tol.get(), "iter": self.entry_iter.get()
        }
        fpath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if fpath:
            with open(fpath, 'w') as f: json.dump(data, f)
            messagebox.showinfo("Success", "Session Configuration Saved!")
            
    def _load_session(self):
        fpath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if fpath:
            with open(fpath, 'r') as f: data = json.load(f)
            self.entry_eq.delete(0, 'end'); self.entry_eq.insert(0, data.get("eq", ""))
            self.method_var.set(data.get("method", "Bisection Method"))
            self._toggle_inputs()
            self.entry_g1.delete(0, 'end'); self.entry_g1.insert(0, data.get("g1", ""))
            self.entry_g2.delete(0, 'end'); self.entry_g2.insert(0, data.get("g2", ""))
            self.entry_tol.delete(0, 'end'); self.entry_tol.insert(0, data.get("tol", ""))
            self.entry_iter.delete(0, 'end'); self.entry_iter.insert(0, data.get("iter", ""))
            messagebox.showinfo("Success", "Session Configuration Loaded!")

    def _export_csv(self):
        if not self.current_table:
            messagebox.showwarning("Export Error", "No data to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            pd.DataFrame(self.current_table).to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"CSV Exported:\n{file_path}")

    def _export_pdf(self):
        if not self.current_table:
            messagebox.showwarning("Export Error", "No data to export.")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path: return
        
        try:
            pdf = FPDF()
            pdf.add_page()
            # Title
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 15, "Numerical Analysis - Professional Report", ln=True, align="C")
            pdf.line(10, 25, 200, 25)
            
            # Data Summary
            pdf.set_font("Helvetica", "", 12)
            pdf.ln(10)
            pdf.cell(0, 8, f"Equation Analyzed: {self.entry_eq.get()}", ln=True)
            pdf.cell(0, 8, f"Method Utilized: {self.method_var.get()}", ln=True)
            pdf.cell(0, 8, f"Final Approximated Root: {self.lbl_res_root.cget('text')}", ln=True)
            pdf.cell(0, 8, f"Total Iterations: {self.lbl_res_iter.cget('text')}", ln=True)
            pdf.cell(0, 8, f"Final Error Margin: {self.lbl_res_err.cget('text')}", ln=True)
            
            # Embed Graph Image
            img_path = "temp_plot.png"
            self.plotter.fig.savefig(img_path, format="png", facecolor="#ffffff", bbox_inches='tight')
            pdf.ln(10)
            pdf.image(img_path, w=170)
            os.remove(img_path)
            
            # Table Export
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Iterations Table Data", ln=True)
            pdf.set_font("Helvetica", "", 10)
            
            # Generate table header based on keys
            keys = list(self.current_table[0].keys())
            cell_w = 180 / len(keys)
            for k in keys: pdf.cell(cell_w, 8, str(k).upper(), border=1, align="C")
            pdf.ln()
            
            for row in self.current_table:
                for k in keys:
                    v = row[k]
                    v_str = f"{v:.6f}" if isinstance(v, float) else str(v)
                    pdf.cell(cell_w, 8, v_str, border=1, align="C")
                pdf.ln()

            pdf.output(file_path)
            messagebox.showinfo("Success", f"Professional PDF Report Generated!\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to generate PDF: {e}")

    def _initiate_loading(self, text):
        self.progressbar.start()
        self.lbl_status.configure(text=text, text_color=self.colors["accent1"])
        self.btn_calc.configure(state="disabled")
        self.btn_comp.configure(state="disabled")
        self.btn_suggest.configure(state="disabled")

    def _stop_loading(self, msg, is_success):
        self.progressbar.stop()
        self.progressbar.set(0) # hide track
        self.btn_calc.configure(state="normal")
        self.btn_comp.configure(state="normal")
        self.btn_suggest.configure(state="normal")
        col = self.colors["success"] if is_success else self.colors["error"]
        self.lbl_status.configure(text=msg, text_color=col)

    def _parse_inputs(self):
        eq = self.entry_eq.get().strip()
        if not eq: raise ValueError("Equation cannot be empty.")
            
        method = self.method_var.get()
        g1_str = self.entry_g1.get().strip()
        g1_label = self.lbl_g1.cget("text").replace(":", "").strip()
        if not g1_str: raise ValueError(f"Please enter a value for {g1_label}.")
        try: v1 = float(g1_str)
        except ValueError: raise ValueError(f"{g1_label} must be a valid number.")
            
        v2 = None
        if getattr(self, "g2_frame").winfo_ismapped():
            g2_str = self.entry_g2.get().strip()
            g2_label = self.lbl_g2.cget("text").replace(":", "").strip()
            if not g2_str: raise ValueError(f"Please enter a value for {g2_label}.")
            try: v2 = float(g2_str)
            except ValueError: raise ValueError(f"{g2_label} must be a valid number.")
                
        tol_str = self.entry_tol.get().strip()
        if not tol_str: raise ValueError("Please enter a Tolerance value.")
        try: tol = float(tol_str)
        except ValueError: raise ValueError("Tolerance must be a numeric value.")
            
        it_str = self.entry_iter.get().strip()
        if not it_str: raise ValueError("Please enter Max Iterations.")
        try: it = int(it_str)
        except ValueError: raise ValueError("Max Iterations must be a valid integer.")
            
        return (eq, method, v1, v2, tol, it)

    def _on_calculate(self):
        try:
            eq, meth, v1, v2, tol, it = self._parse_inputs()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return
            
        self._initiate_loading("Computing logic & steps...")
        self.tabview.set("📊 Data Table")
        self.txt_steps.delete("1.0", "end")
        threading.Thread(target=self._run_calc_thread, args=(eq, meth, v1, v2, tol, it), daemon=True).start()

    def _run_calc_thread(self, eq, meth, v1, v2, tol, it):
        try:
            solver = NumericalMethods(eq)
            res = self._execute_method(solver, meth, v1, v2, tol, it)
            # Find all possible intervals for visualization mapping
            all_intervals = solver.find_intervals()
            self.after(0, self._render_results, res, solver, meth, v1, v2, all_intervals)
        except Exception as e:
            self.after(0, self._handle_error, str(e))

    def _execute_method(self, solver, meth, v1, v2, tol, it):
        if meth == "Bisection Method": return solver.bisection(v1, v2, tol, it)
        if meth == "Newton-Raphson Method": return solver.newton_raphson(v1, tol, it)
        if meth == "Secant Method": return solver.secant(v1, v2, tol, it)
        if meth == "False Position Method": return solver.false_position(v1, v2, tol, it)
        if meth == "Fixed Point Iteration": return solver.fixed_point(v1, tol, it)
        if meth == "Brent's Method": return solver.brent(v1, v2, tol, it)
        return None

    def _animated_count_up(self, label, final_val, is_float, is_err=False):
        steps = 15
        delay = 30
        
        def update(step):
            if step <= steps:
                if is_float and not is_err:
                    v = final_val * (step/steps)
                    label.configure(text=f"{v:.7f}")
                elif is_err:
                    # Exponential scale to target for scientific
                    v = final_val * (step/steps) if final_val > 0 else 0
                    label.configure(text=f"{v:.2e}")
                else: 
                    v = int(final_val * (step/steps))
                    label.configure(text=str(v))
                self.after(delay, update, step + 1)
            else:
                label.configure(text=(f"{final_val:.7f}" if is_float and not is_err else f"{final_val:.2e}" if is_err else str(final_val)))
                
        if final_val is not None:
            update(1)
        else:
            label.configure(text="N/A")

    def _render_results(self, res, solver, method, val1, val2, all_intervals):
        if res is None or len(res) < 6:
            self._handle_error("Method returned invalid response.")
            return
            
        root, iters, error, table, msg, steps_text = res
        self.current_table = table
        success_bool = "Success" in msg or "Found Root" in msg
        self._stop_loading(msg.split(":")[0] if ":" in msg else msg, success_bool)
        
        # Animate Metrics Cards updates!
        if success_bool:
            self._animated_count_up(self.lbl_res_root, root, True)
        else:
            self.lbl_res_root.configure(text="N/A")
            
        self._animated_count_up(self.lbl_res_iter, iters, False)
        self._animated_count_up(self.lbl_res_err, error, True, True)
        
        # Populate Step-By-Step text
        self.txt_steps.insert("end", steps_text + "\n" + msg)
        
        # Update Tree
        for item in self.tree.get_children(): self.tree.delete(item)
        if table:
            keys = list(table[0].keys())
            self.tree.configure(columns=keys)
            for col in keys:
                self.tree.heading(col, text=col.upper())
                self.tree.column(col, anchor="center")
            
            for i, row in enumerate(table):
                vals = [f"{v:.6f}" if isinstance(v, float) else v for v in row.values()]
                
                # Smart Table Highlighting Logic
                tags = ()
                if i == len(table)-1 and success_bool:
                    tags = ('highlight',)
                elif i > 0 and 'error' in row and 'error' in table[i-1] and row['error'] > table[i-1]['error']:
                    tags = ('unstable',)
                    
                self.tree.insert("", "end", values=vals, tags=tags)
                
        # Update Interactive Graph
        self.plotter.plot_results(solver.f, root, table, method, val1, val2, all_roots_intervals=all_intervals)

    def _on_compare(self):
        try:
            eq = self.entry_eq.get().strip()
            if not eq: raise ValueError("Equation cannot be empty.")
            
            v1_str = self.entry_g1.get().strip()
            if not v1_str: raise ValueError("Please enter a numeric value for bound/initial guess.")
            v1 = float(v1_str)
            
            if getattr(self, "g2_frame").winfo_exists() and self.entry_g2.get().strip():
                v2 = float(self.entry_g2.get().strip())
            else:
                v2 = v1 + 1.0  
                
            tol = float(self.entry_tol.get().strip())
            it = int(self.entry_iter.get().strip())
        except ValueError as e:
            if "empty" in str(e) or "Please enter" in str(e): messagebox.showerror("Validation Error", str(e))
            else: messagebox.showerror("Validation Error", "Need valid numeric inputs for comparison.")
            return
            
        self._initiate_loading("Running multi-threaded comparisons...")
        self.tabview.set("📈 Method Comparison")
        threading.Thread(target=self._run_compare_thread, args=(eq, v1, v2, tol, it), daemon=True).start()
        
    def _run_compare_thread(self, eq, v1, v2, tol, it):
        try:
            solver = NumericalMethods(eq)
            results = []
            tasks = [("Bisection Method", v1, v2), ("Newton-Raphson Method", v1, None),
                     ("Secant Method", v1, v2), ("False Position Method", v1, v2),
                     ("Fixed Point Iteration", v1, None), ("Brent's Method", v1, v2)]
            for name, arg1, arg2 in tasks:
                res = self._execute_method(solver, name, arg1, arg2, tol, it)
                stat = res[4].split(":")[0] if res and len(res) > 4 and ":" in res[4] else "Error"
                results.append((name, res[0], res[1], res[2], stat) if res else (name, None, 0, 0.0, "Skipped"))
                
            self.after(0, self._render_comparison, results)
        except Exception as e:
            self.after(0, self._handle_error, str(e))
            
    def _render_comparison(self, results):
        self._stop_loading("Comparison Benchmarking Complete", True)
        for item in self.comp_tree.get_children(): self.comp_tree.delete(item)
        
        for name, root, iters, err, stat in results:
            root_s = f"{root:.6f}" if root is not None else "N/A"
            err_s = f"{err:.2e}" if err else "0.0"
            self.comp_tree.insert("", "end", values=[name, root_s, str(iters), err_s, stat])

    def _handle_error(self, err_msg):
        self._stop_loading("System Interruption", False)
        messagebox.showerror("System Error", err_msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()
