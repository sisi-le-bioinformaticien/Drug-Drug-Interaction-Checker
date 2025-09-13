# Import required libraries
import sqlite3
import csv
import tkinter as tk

############################## Dtabase Design ###########################
def initialize_database():
    try:
        conn = sqlite3.connect('medications.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS interactions (
                            Medication_1 TEXT,
                            Medication_2 TEXT
                        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS drugs (
                            name TEXT,
                            description TEXT
                        )''')

        # Read CSV and insert data into SQLite
        with open('Drugbank4-PDDIs.csv', 'r', encoding='utf-8') as csvfile:
            encountered_drugs = []
            for line in csvfile:
                medication1, medication2 = line.strip().split('$')[1], line.strip().split('$')[3]
                
                # Insert data
                cursor.execute("INSERT INTO interactions VALUES (?, ?)", (medication1, medication2))
                if medication1 not in encountered_drugs:
                    cursor.execute("INSERT INTO drugs VALUES (?, ?)", (medication1, f"Add precise drug description for {medication1} here"))
                    encountered_drugs.append(medication1)
                if medication2 not in encountered_drugs:
                    cursor.execute("INSERT INTO drugs VALUES (?, ?)", (medication2, f"Add precise drug description for {medication2} here"))
                    encountered_drugs.append(medication2)

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print("Database initialization error:", e)

def check_interaction(cursor, medicine1, medicine2): 
    try:
        # Query database to check for interaction
        cursor.execute("SELECT * FROM interactions WHERE Medication_1 = ? AND Medication_2 = ? OR Medication_1 = ? AND Medication_2 = ?", (medicine1, medicine2, medicine2, medicine1))
        interaction = cursor.fetchone()

        # Display result based on interaction
        if interaction:
            print(f"DANGER: dangerous interaction detected {medicine1} {medicine2}")
            return [medicine1,medicine2]     
        else:
            return False
    except sqlite3.Error as e:
        print( "Database error: " + str(e))
        return False

def check_all_interaction(list, cursor):
    dangerous_interactions = ""
    interaction_tab = []
    results = []
    for i in range(len(list)):
        for j in range(i + 1, len(list)):
            result = check_interaction(cursor, list[i], list[j])
            results.append(result)
    for r in results:
        if r:
            dangerous_interactions += f"DANGER: dangerous interaction detected {r[0]} - {r[1]}\n"
            interaction_tab.append(r[0])
            interaction_tab.append(r[1])
    return dangerous_interactions, interaction_tab

def fetch_best_match(prefix):
    try:
        conn = sqlite3.connect('medications.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM drugs WHERE name LIKE ?", (prefix + '%',))
        result = cursor.fetchone()
        return result[0] if result else ''
    except sqlite3.Error as e:
        print("Database connection error:", e)
        exit()
    
# Autocomplete Entry class with best match label
class AutocompleteEntry(tk.Entry):
    def __init__(self, master=None, textvariable=None, *args, **kwargs):
        if textvariable is None:
            textvariable = tk.StringVar()
        self.var = textvariable
        super().__init__(master, textvariable=self.var, *args, **kwargs)
        
        self.var.trace_add("write", self.update_best_match)
        self.bind("<Return>", self.accept_suggestion)
        self.best_match = ''
        
        self.suggestion_label = tk.Label(self.master, fg="gray", font=("Arial", 10, "italic"))
        self.suggestion_label.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height(), width=self.winfo_width())
        
    def update_best_match(self, *args):
        user_input = self.var.get()
        best_match = fetch_best_match(user_input)
        if user_input and best_match and best_match.lower().startswith(user_input.lower()):
            self.best_match = best_match
            self.show_suggestion( best_match)
        else:
            self.best_match = ''
            self.suggestion_label.place_forget()

    def show_suggestion(self,  best_match):
        self.suggestion_label.config(text=best_match)
        self.suggestion_label.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height(), width=self.winfo_width())

    def accept_suggestion(self, event):
        if self.best_match:
            self.var.set(self.best_match)
            self.suggestion_label.place_forget()
            self.icursor(tk.END)
        return 'break'