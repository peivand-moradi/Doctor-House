import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import backend


def update_list(event):
    """Filter dropdown options while keeping focus."""
    typed = entry.get().lower()
    listbox.delete(0, tk.END)
    filtered = [item for item in symptom_options if typed in item.lower()]
    if filtered:
        for item in filtered:
            listbox.insert(tk.END, item)
        dropdown_frame.place(x=entry.winfo_x(), y=entry.winfo_y() + entry.winfo_height(),
                             width=entry.winfo_width())
    else:
        dropdown_frame.place_forget()


def select_option(event):
    """Show the selected option in selected symptoms list box and close the dropdown."""
    selected = listbox.get(listbox.curselection())
    entry.delete(0, tk.END)
    lst_box.insert(tk.END, selected)
    dropdown_frame.place_forget()


def show_dropdown(event):
    """Show dropdown list when entry user types in entry"""
    update_list(event)


def hide_dropdown(event):
    """Hide dropdown when clicking outside of the dropdown and entry."""
    if event.widget != entry and event.widget != listbox:
        dropdown_frame.place_forget()


def clear_lst_box():
    """Clear the list box of selected symptoms."""
    lst_box.delete(0, tk.END)


def check_diagnosis():
    """Calculate the potential diseases and show error if no symptom was selected."""
    patient_symptoms = lst_box.get(0, tk.END)
    if patient_symptoms:
        result = backend.calculate_potential_disease(backend.diagnosis_graph, patient_symptoms)
        create_diagnosis_window(result)
        clear_lst_box()
    else:
        label_error.config(text="Please select symptoms!!", foreground="red")
        root.after(1000, lambda : label_error.config(text=""))


def create_diagnosis_window(data: dict):
    """Create diagnosis window after the user pressed the the relative button"""

    pop_up = tk.Toplevel(root)
    pop_up.title("Diagnosis")
    pop_up.geometry("600x500")

    pop_up.attributes('-fullscreen', True)

    pop_up.bind("<Escape>", lambda event: toggle_fullscreen(pop_up))

    create_disease_chart(data, pop_up)

    frame_below = cttk.Frame(pop_up)
    frame_below.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)

    button_frame_pop = ttk.Frame(frame_below)
    button_frame_pop.pack(fill=tk.X, pady=5)

    ttk.Label(frame_below, text="Disease's description").pack(anchor="w", pady=5)
    lst_box_info = tk.Text(frame_below, wrap=tk.WORD, height=10, width=50, bg="#C7D9DD", fg="black",
                           padx=10, pady=10, font=("Lexend", 10))
    lst_box_info.pack(fill=tk.BOTH, expand=True)

    for i, disease in enumerate(data):
        button_info = ttk.Button(button_frame_pop, text=f"{disease}",
                                 command=lambda disease=disease: show_info(disease, lst_box_info))
        button_info.grid(row=0, column=i, sticky="ew", padx=5)

    style_diagnosis = ttk.Style(pop_up)
    style_diagnosis.theme_use('clam')
    style_diagnosis.configure('TFrame', background='#ADB2D4')
    style_diagnosis.configure('TLabel', background='#ADB2D4', foreground='black', font=('Lexend', 10))
    style_diagnosis.configure('TButton', background='#2b2b2b', foreground='white')
    style_diagnosis.map('TButton', background=[('active', '#FFF2F2')], foreground=[('active', '#2b2b2b')])

    pop_up.columnconfigure(0, weight=1)
    pop_up.rowconfigure(1, weight=1)
    pop_up.rowconfigure(0, weight=1)
    pop_up.config(bg="#ADB2D4")


def show_info(selected, box):
    """show info related to the selected disease"""

    box.delete(1.0, tk.END)
    box.insert(tk.END, disease_dict[selected].description + "\n")
    box.insert(tk.END, "--------------------------------------------------------------------\n")
    box.insert(tk.END, "Advice:\n")
    for item in disease_dict[selected].advice:
        box.insert(tk.END, f"• {item}\n")


def create_disease_chart(data: dict, window):
    """Create a chart based on the probabilities of the possible diseases"""
    frame_chart= ttk.Frame(window)
    frame_chart.grid(row=0, column=0, sticky="nsew", padx=20, pady=15)
    fig = Figure(figsize=(4, 4), dpi=80, facecolor="#C7D9DD")
    ax = fig.add_subplot(111)
    categories = []
    values = []
    for disease in data:
        categories.append(disease)
        values.append(data[disease])

    ax.bar(categories, values, color=['blue', 'green', 'red', 'purple'])
    ax.set_title("Disease probabilities")
    ax.set_xlabel("disease's name")
    ax.set_ylabel("percentage")

    ax.set_ylim(0, 100)

    canvas = FigureCanvasTkAgg(fig, master=frame_chart)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)


def toggle_fullscreen(window, event=None):
    is_fullscreen = window.attributes('-fullscreen')
    window.attributes('-fullscreen', not is_fullscreen)

# ------------------------------------------------


# Main window setup
root = tk.Tk()
root.title("Doctor House")
root.geometry("500x400")

root.attributes('-fullscreen', True)

# style

root.bind("<Escape>", lambda event: toggle_fullscreen(root))

style = ttk.Style(root)
style.theme_use('clam')
style.configure('TFrame', background='#ADB2D4')
style.configure('TLabel', background='#ADB2D4', foreground='black', font=('Lexend', 12))
style.configure('TButton', background='#2b2b2b', foreground='white')
style.map('TButton', background=[('active', '#FFF2F2')], foreground=[('active', '#2b2b2b')])

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.config(bg="#ADB2D4")


# Left panel

left_frame = ttk.Frame(root, padding=15)
left_frame.grid(row=0, column=0, sticky="nsew")

# Right panel

right_frame = ttk.Frame(root, padding=10)
right_frame.grid(row=0, column=1, sticky="nsew")

ttk.Label(left_frame, text="Search Symptoms:").pack(anchor="w")
entry = ttk.Entry(left_frame)
entry.pack(fill=tk.X, pady=5)
entry.bind("<KeyRelease>", update_list)
entry.bind("<FocusIn>", show_dropdown)

dropdown_frame = ttk.Frame(root, relief=tk.SUNKEN, borderwidth=1)
listbox = tk.Listbox(dropdown_frame, height=6,  bg="#2b2b2b", fg="white",
                     selectbackground="#FFF2F2", selectforeground="#2b2b2b")
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind("<ButtonRelease-1>", select_option)

# Selected symptoms list box

ttk.Label(right_frame, text="Selected Symptoms:").pack(anchor="w", pady= 5)
lst_box = tk.Listbox(right_frame, bg="#ADB2D4", font=('Lexend', 10))
lst_box.pack(fill=tk.BOTH, expand=True)

# Buttons

button_frame = ttk.Frame(right_frame)
button_frame.pack(fill=tk.X, pady=10)

btn_clear = ttk.Button(button_frame, text="Clear", command=clear_lst_box)
btn_clear.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

btn_submit = ttk.Button(button_frame, text="Check Diagnosis", command=check_diagnosis)
btn_submit.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

label_error = ttk.Label(right_frame, text="")
label_error.pack(pady=5)

root.bind('<Button-1>', hide_dropdown)
symptom_options = sorted(backend.symptoms_list.copy())
disease_dict = backend.name_to_disease_map

root.mainloop()

if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['csv', 'matplotlib', 'tkinter', 'backend', 'matplotlib.pyplot', 'matplotlib.figure', 'matplotlib.backends.backend_tkagg'],
        'allowed-io': ['print'],
        'max-line-length': 120
    })