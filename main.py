"""This module provides the graphical user interface for our remote diagnosis software"""
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import backend


class DoctorHouseApp:
    """Represent the main window of app
     Instance Attributes:
        - root: represent the main window
        - widgets: A dictionay with elements as each ui element of the root window"""

    root: tk.Tk
    widgets: dict

    def __init__(self, my_root: tk.Tk) -> None:
        self.root = my_root
        self.root.title("Doctor House")
        self.root.geometry("500x400")
        self.widgets = {}
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.toggle_fullscreen)

        # Style
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TFrame', background='#ADB2D4')
        style.configure('TLabel', background='#ADB2D4', foreground='black', font=('Lexend', 12))
        style.configure('TButton', background='#2b2b2b', foreground='white')
        style.map('TButton', background=[('active', '#FFF2F2')], foreground=[('active', '#2b2b2b')])

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.config(bg="#ADB2D4")

        # Left Panel
        self.widgets["left_frame"] = ttk.Frame(self.root, padding=15)
        self.widgets["left_frame"].grid(row=0, column=0, sticky="nsew")

        # Right Panel
        self.widgets["right_frame"] = ttk.Frame(self.root, padding=10)
        self.widgets["right_frame"].grid(row=0, column=1, sticky="nsew")

        ttk.Label(self.widgets["left_frame"], text="Search Symptoms:").pack(anchor="w")
        self.widgets["entry"] = ttk.Entry(self.widgets["left_frame"])
        self.widgets["entry"].pack(fill=tk.X, pady=5)
        self.widgets["entry"].bind("<KeyRelease>", self.update_list)
        self.widgets["entry"].bind("<FocusIn>", self.show_dropdown)

        self.widgets["dropdown frame"] = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.widgets["listbox"] = tk.Listbox(self.widgets["dropdown frame"], height=6, bg="#2b2b2b", fg="white",
                                             selectbackground="#FFF2F2", selectforeground="#2b2b2b")
        self.widgets["listbox"].pack(fill=tk.BOTH, expand=True)
        self.widgets["listbox"].bind("<ButtonRelease-1>", self.select_option)

        # Selected Symptoms List Box
        ttk.Label(self.widgets["right_frame"], text="Selected Symptoms:").pack(anchor="w", pady=5)
        self.widgets["lst_box"] = tk.Listbox(self.widgets["right_frame"], bg="#ADB2D4", font=('Lexend', 10))
        self.widgets["lst_box"].pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = ttk.Frame(self.widgets["right_frame"])
        button_frame.pack(fill=tk.X, pady=10)

        self.widgets["btn_clear"] = ttk.Button(button_frame, text="Clear", command=self.clear_lst_box)
        self.widgets["btn_clear"].pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.widgets["btn_submit"] = ttk.Button(button_frame, text="Check Diagnosis", command=self.check_diagnosis)
        self.widgets["btn_submit"].pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.widgets["label_error"] = ttk.Label(self.widgets["right_frame"], text="")
        self.widgets["label_error"].pack(pady=5)

        self.root.bind('<Button-1>', self.hide_dropdown)

    def toggle_fullscreen(self, _event: tk.Event = None) -> None:
        """Toggle fullscreen mode."""
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)

    def update_list(self, _event: tk.Event = None) -> None:
        """Update dropdown list based on user input."""
        typed = self.widgets["entry"].get().lower()
        self.widgets["listbox"].delete(0, tk.END)
        filtered = [symptom for symptom in SYMPTOM_OPTIONS if typed in symptom.lower()]
        if filtered:
            for item in filtered:
                self.widgets["listbox"].insert(tk.END, item)
            x_size = self.widgets["entry"].winfo_x()
            y_size = self.widgets["entry"].winfo_y() + self.widgets["entry"].winfo_height()
            width = self.widgets["entry"].winfo_width()
            self.widgets["dropdown frame"].place(x=x_size, y=y_size, width=width)
        else:
            self.widgets["dropdown frame"].place_forget()

    def show_dropdown(self, _event: tk.Event = None) -> None:
        """Show dropdown list when user types in entry"""
        self.update_list()

    def select_option(self, _event: tk.Event) -> None:
        """Show the selected option in selected symptoms list box and close the dropdown."""
        if not self.widgets["listbox"].curselection():
            return
        selected = self.widgets["listbox"].get(self.widgets["listbox"].curselection())
        self.widgets["entry"].delete(0, tk.END)
        self.widgets["lst_box"].insert(tk.END, selected)
        self.widgets["dropdown frame"].place_forget()

    def hide_dropdown(self, event: tk.Event) -> None:
        """Hide dropdown when clicking outside the dropdown and entry."""
        if event.widget not in (self.widgets["entry"], self.widgets["listbox"]):
            self.widgets["dropdown frame"].place_forget()

    def clear_lst_box(self) -> None:
        """Clear the list box of selected symptoms."""
        self.widgets["lst_box"].delete(0, tk.END)

    def check_diagnosis(self) -> None:
        """Calculate the potential diseases and show error if no symptom was selected."""
        patient_symptoms = self.widgets["lst_box"].get(0, tk.END)
        if patient_symptoms:
            result = backend.calculate_potential_disease(DIAGNOSIS_GRAPH, patient_symptoms)
            DiagnosisWindow(self.root, result)
            self.clear_lst_box()
        else:
            self.widgets["label_error"].config(text="Please select symptoms!!", foreground="red")
            self.root.after(1000, lambda: self.widgets["label_error"].config(text=""))


class DiagnosisWindow:
    """Representing the window that would show up after clicking the checking button in main window
         Instance Attributes:
        - pop_up: represent the main window of this top level window
        - elements: A dictionay with elements as each ui element of the pop_up window"""

    pop_up: tk.Toplevel
    elements: dict

    def __init__(self, parent: tk.Tk, data: dict) -> None:
        """Create diagnosis window after the user pressed the relative button"""
        self.pop_up = tk.Toplevel(parent)
        self.pop_up.title("Diagnosis")
        self.pop_up.geometry("600x500")
        self.elements = {}

        self.pop_up.attributes('-fullscreen', True)

        self.pop_up.bind("<Escape>", self.toggle_fullscreen)

        self.create_disease_chart(data)

        self.elements["frame_below"] = ttk.Frame(self.pop_up)
        self.elements["frame_below"].grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

        self.elements["button_frame_pop"] = ttk.Frame(self.elements["frame_below"])
        self.elements["button_frame_pop"].pack(fill=tk.X, pady=5)

        ttk.Label(self.elements["frame_below"], text="Disease's description").pack(anchor="w", pady=5)
        self.elements["lst_box_info"] = tk.Text(self.elements["frame_below"], wrap=tk.WORD, height=10, width=50,
                                                bg="#C7D9DD",
                                                fg="black",
                                                padx=10, pady=10, font=("Lexend", 10))
        self.elements["lst_box_info"].pack(fill=tk.BOTH, expand=True)

        for i, disease in enumerate(data):
            button_info = ttk.Button(self.elements["button_frame_pop"], text=f"{disease}",
                                     command=lambda disease=disease: self.show_info(disease))
            button_info.grid(row=0, column=i, sticky="ew", padx=5)

        style_diagnosis = ttk.Style(self.pop_up)
        style_diagnosis.theme_use('clam')
        style_diagnosis.configure('TFrame', background='#ADB2D4')
        style_diagnosis.configure('TLabel', background='#ADB2D4', foreground='black', font=('Lexend', 10))
        style_diagnosis.configure('TButton', background='#2b2b2b', foreground='white')
        style_diagnosis.map('TButton', background=[('active', '#FFF2F2')], foreground=[('active', '#2b2b2b')])

        self.pop_up.columnconfigure(0, weight=1)
        self.pop_up.rowconfigure(1, weight=1)
        self.pop_up.rowconfigure(0, weight=1)
        self.pop_up.config(bg="#ADB2D4")

    def toggle_fullscreen(self, _event: tk.Event = None) -> None:
        """Toggle fullscreen mode."""
        is_fullscreen = self.pop_up.attributes('-fullscreen')
        self.pop_up.attributes('-fullscreen', not is_fullscreen)

    def create_disease_chart(self, data: dict) -> None:
        """Create a chart based on the probabilities of the possible diseases"""
        self.elements["frame_chart"] = ttk.Frame(self.pop_up)
        self.elements["frame_chart"].grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
        self.elements["fig"] = Figure(figsize=(4, 4), dpi=80, facecolor="#C7D9DD")
        ax = self.elements["fig"].add_subplot(111)

        categories = list(data.keys())
        values = list(data.values())

        ax.bar(categories, values, color=['blue', 'green', 'red', 'purple'])

        ax.set_title("Disease probabilities")
        ax.set_xlabel("Disease Name")
        ax.set_ylabel("Percentage")
        ax.set_ylim(0, 100)

        self.elements["canvas"] = FigureCanvasTkAgg(self.elements["fig"], master=self.elements["frame_chart"])
        self.elements["canvas"].draw()
        self.elements["canvas"].get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

    def show_info(self, selected: str) -> None:
        """Show info related to the selected disease"""
        self.elements["lst_box_info"].delete(1.0, tk.END)
        self.elements["lst_box_info"].insert(tk.END, DISEASE_DICT[selected].description + "\n")
        self.elements["lst_box_info"].insert(tk.END, "-------------------------------------------------------------\n")
        self.elements["lst_box_info"].insert(tk.END, "Advice:\n")
        for item in DISEASE_DICT[selected].advice:
            self.elements["lst_box_info"].insert(tk.END, f"• {item}\n")


DIAGNOSIS_GRAPH, SYMPTOMS_LIST, NAME_TO_DISEASE_MAP = backend.load_diagnosis_graph(
    'Symptom-severity.csv',
    'dataset.csv',
    'symptom_Description.csv',
    'symptom_precaution.csv')
SYMPTOM_OPTIONS = sorted(SYMPTOMS_LIST.copy())
DISEASE_DICT = NAME_TO_DISEASE_MAP

if __name__ == '__main__':
    import python_ta

    root = tk.Tk()
    app = DoctorHouseApp(root)
    root.mainloop()

    python_ta.check_all(config={
        'extra-imports': ['csv', 'matplotlib', 'tkinter', 'backend', 'matplotlib.pyplot', 'matplotlib.figure',
                          'matplotlib.backends.backend_tkagg'],
        'allowed-io': ['print'],
        'max-line-length': 120
    })
