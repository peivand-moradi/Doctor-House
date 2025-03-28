import tkinter as tk
from tkinter import ttk
import main


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
        result = main.calculate_potential_disease(main.diagnosis_graph, patient_symptoms)
        print(result)
        clear_lst_box()
    else:
        label_error.config(text="Please select symptoms!!", foreground="red")
        root.after(1000, lambda : label_error.config(text=""))


# Main window setup
root = tk.Tk()
root.title("Doctor House")
root.geometry("500x400")

# style

style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background='#A9B5DF')
style.configure('TLabel', background='#A9B5DF', foreground='#2b2b2b', font=('Helvetica', 10))
style.configure('TButton', background='#2D336B', foreground='white')
style.map('TButton', background=[('active', '#FFF2F2')], foreground=[('active', '#2b2b2b')])

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.config(bg="#205781")

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
listbox = tk.Listbox(dropdown_frame, height=6,  bg="#2b2b2b", fg="white", selectbackground="#FFF2F2", selectforeground="#2b2b2b")
listbox.pack(fill=tk.BOTH, expand=True)
listbox.bind("<ButtonRelease-1>", select_option)

# Selected symptoms list box

ttk.Label(right_frame, text="Selected Symptoms:").pack(anchor="w", pady= 5)
lst_box = tk.Listbox(right_frame)
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
symptom_options = sorted(main.symptoms_list.copy())

root.mainloop()