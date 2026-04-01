from fpdf import FPDF

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'Comprehensive Project Report', align='C', ln=True)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 8, 'Numerical Analysis Pro: Premium Root Finder', align='C', ln=True)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def add_section(self, title, body):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 80, 160) # Blue colored section headers
        self.cell(0, 10, title, ln=True)
        self.ln(2)
        
        self.set_font('Helvetica', '', 11)
        self.set_text_color(0, 0, 0)
        # multi_cell automatically handles word wrap
        self.multi_cell(0, 6, body)
        self.ln(4)

pdf = PDFReport()
pdf.add_page()

intro = """The "Numerical Analysis Pro" is an advanced, production-grade desktop application designed for solving complex mathematical equations and finding their roots. Transitioning from a basic script to a professional software tool, it focuses on high-performance numerical algorithms, an interactive visual interface, and robust data presentation. This project serves as an exceptional academic tool, replacing tedious manual calculations with smart, automated, and mathematically verifiable processes."""
pdf.add_section("1. Project Introduction", intro)

tech = """The application was constructed using a powerful stack of modern Python technologies:
- Python 3.14 (Beta): Ensuring robust core processing.
- CustomTkinter: Replaced standard Tkinter to provide a glassmorphism-inspired, dark-themed modern UI.
- SymPy: Used for strict mathematical validation, equation parsing, and symbolic differentiation natively.
- Matplotlib: Powers the interactive plotting canvas (NavigationToolbar2Tk) for zooming, panning, and convergence analysis.
- NumPy: Handles fast array manipulations, specifically for scanning large computational intervals.
- Pandas: Handles backend data-tabulation for exporting clean iteration histories to CSV.
- FPDF2: Generates customized, on-the-fly PDF reports combining graphs and iterative tables.
- SpeechRecognition & Regular Expressions (RE): Backs the Natural Language Processing (NLP) integration for voice-to-math parsing."""
pdf.add_section("2. Core Technologies Used", tech)

methods = """The core engine integrates six highly robust root-finding algorithms, each completely abstracted to handle divergence safely:
1. Bisection Method: A reliable bracketing method mapping limits safely.
2. Newton-Raphson Method: Uses Sympy for exact derivatives to find extremely rapid convergence.
3. Secant Method: A finite-difference approximation replacing derivative logic.
4. False Position (Regula Falsi): An optimized bracketing interpolation method.
5. Fixed Point Iteration: Iterative looping manually rewritten for native g(x) logic.
6. Brent's Method: A hand-coded, pure Python implementation combining Secant, Bisection, and Inverse Quadratic Interpolation for ultimate speed without relying on external Fortran bins (scipy)."""
pdf.add_section("3. Implemented Algorithms", methods)

uiux = """A significant portion of development focused on producing a 'premium' User Experience (UX):
- Dark / Light Theme engine to reduce eye-strain.
- Animated Metric Cards: Variables smoothly 'count-up' to their target values via linear interpolation.
- Interactivity: Users can visualize zero-crossings natively with crosshairs plotted automatically.
- Smart Tables: Iteration grids highlight in Green (Success) or Red (Divergence/Instability) to guide the eyes.
- Multi-threading: Complex functions parse in the background without causing the UI context to freeze. Progress bars show computing states visually."""
pdf.add_section("4. UI/UX Design & Architecture", uiux)

smart = """The software deviates from standard calculators by integrating cutting-edge 'Smart Features':
- Auto-Suggest Interval: Background scanners check limits globally (-20, 20), predicting optimal Bracket setups instantly.
- Step-by-step Generator: The mathematical operations update dynamically into a 'Textbook format', explaining EXACTLY how values like x1 or c are calculated per iteration.
- NLP Voice Parser: An inclusive fallback dialog translates English ("x cube minus x") into computable Sympy algebraic representations ("x**3 - x").
- Save/Load JSON Sessions: Workspace environments can be frozen to disk and retrieved at a later date.
- PDF Exporting: Seamless one-click printing of full mathematical operations."""
pdf.add_section("5. Advanced Intelligent Features", smart)

conc = """This root-finding calculator application proves itself as a comprehensive engineering simulation toolkit. By focusing strictly on avoiding generic failure points (e.g., divergence timeouts, un-parsed equation crashing) and prioritizing human-readability alongside heavy mathematical accuracy, Numerical Analysis Pro sets an elite standard for academic programming projects."""
pdf.add_section("6. Conclusion", conc)

pdf.output("Numerical_Analysis_Project_Report.pdf")
print("PDF generation complete!")
