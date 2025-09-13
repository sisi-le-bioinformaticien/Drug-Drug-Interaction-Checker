import tkinter as tk
from tkinter import ttk
from tkinter import Text, messagebox
from PIL import Image, ImageTk
from db_utility import *
import sqlite3
import os

initialize_database()

# Connection à la database
try:
    conn = sqlite3.connect('medications.db')
    cursor = conn.cursor()
except sqlite3.Error as e:
    print("Database connection error:", e)
    exit()

# Fenêtre principale
root = tk.Tk()
root.title("Système d'information médicale")

# Affichage du logo
ico = Image.open('./Images/logo2.jpg')
resized_photo =  ico.resize((40,40))
photo = ImageTk.PhotoImage(resized_photo)
root.wm_iconphoto(False, photo)

# Configuration de la grille
frame_profil = ttk.Frame(root, padding="3 3 12 12")
frame_profil.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Initialisation des variables
current_drug_list = []
smoking = tk.BooleanVar()
coffee = tk.BooleanVar()
alcohol = tk.BooleanVar()

# Affichage vue principale
ttk.Label(frame_profil, text="Profil personnel").grid(column=0, row=0, columnspan=4)

# Mise à jour de la liste
def update_view():
    output, int_list =  check_all_interaction(current_drug_list, cursor)
    mark_interaction(int_list)
    output_interactions(output)

# Ajout/retrait nicotine
def add_smoke():
    smoke = smoking.get()
    if smoke:
        
        current_drug_list.append('Nicotine')
        listbox_drugs.insert(tk.END, 'Nicotine')
        update_view()
        print("Ajout du médicament: Nicotine")
    else:
       index = current_drug_list.index('Nicotine')
       current_drug_list.remove('Nicotine') 
       listbox_drugs.delete( index)
       update_view()
       print("Retrait du médicament: Nicotine")

# Ajout/retrait caféine
def add_coffee():
    coff = coffee.get()
    if coff:      
        current_drug_list.append('Caffeine')
        listbox_drugs.insert(tk.END, 'Caffeine')
        update_view()
        print("Ajout du médicament: Caffeine")
    else:
       index = current_drug_list.index('Caffeine')   
       current_drug_list.remove('Caffeine') 
       listbox_drugs.delete( index)
       update_view()
       print("Retrait du médicament: Caffeine")

# Ajout/retrait ethanol
def add_alcohol():
    vodka = alcohol.get()
    if vodka:
        current_drug_list.append('Ethanol')
        listbox_drugs.insert(tk.END, 'Ethanol')
        update_view()
        print("Ajout du médicament: Ethanol")

    else:
        index = current_drug_list.index('Ethanol')   
        current_drug_list.remove('Ethanol') 
        listbox_drugs.delete( index)
        update_view()
        print("Retrait du médicament: Ethanol")

    
# Ajout des boutons nicotine, ethanol, caféine
ttk.Checkbutton(frame_profil, text="Fumeur", variable=smoking, command=add_smoke).grid(column=1, row=2)
ttk.Checkbutton(frame_profil, text="Consommation de caféine", variable=coffee, command=add_coffee).grid(column=2, row=2)
ttk.Checkbutton(frame_profil, text="Consommation d'alcool", variable=alcohol, command=add_alcohol).grid(column=3, row=2)

# Ajout d'une barre de recherche pour les médicaments
drug_name = tk.StringVar()
label = ttk.Label(frame_profil).grid(column=0, row=2, sticky=tk.W, pady=(0, 5))
entry = AutocompleteEntry(frame_profil, textvariable=drug_name)
entry.grid(column=0, row=1, sticky=(tk.W, tk.E))

# Alerte erreur
def alert_oops():
    messagebox.showinfo("OOPS....", "This feature will be implemented in the following update.")

# Recherche d'un médicament
def lookup_drug(index=None):
    if index != None:
 
        drug = current_drug_list[index]
    else:
        drug = drug_name.get()
    if drug:
        top = tk.Toplevel(root)
        top.title(f"Résultats pour : {drug}")
        ttk.Label(top, text=f"Résultats pour le médicament : {drug.upper()}").pack(pady=20, padx=20)
        image_path = f'./Images/{drug}.png' 
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            ttk.Label(top, image=photo).pack(pady=20)
            top.image = photo
        else:
            ttk.Label(top, text="No image available").pack(pady=20)

        if drug in current_drug_list:
            tk.Button(top, text="Supprimer médicament", command=lambda : delete_drug()).pack(pady=10)

# Marque en rouge les interractions dangereuses
def mark_interaction(int_list):
    for i in range(listbox_drugs.size()):
        drug = listbox_drugs.get(i)
        if drug in int_list:
            listbox_drugs.itemconfig(i, {'bg': 'red'})
        else:
            listbox_drugs.itemconfig(i, {'bg': 'white'})

# Affichage texte interractions
def output_interactions(messages):
    text_output.delete(1.0, tk.END)
    text_output.insert(tk.END, messages, "red")

# Ajout médicament
def add_drug():
    drug = drug_name.get()
    if drug and drug not in current_drug_list:
        current_drug_list.append(drug)
        listbox_drugs.insert(tk.END, drug)
        drug_name.set("") 
    print("Ajout du médicament:", drug_name.get())
    output, int_list =  check_all_interaction(current_drug_list, cursor)
    mark_interaction(int_list)
    output_interactions(output)

# Retrait médicament
def delete_drug():
    try:       
        index = listbox_drugs.curselection()[0]
        drug = listbox_drugs.get(index)
        if drug == "Nicotine":
            smoking.set(False)
        if drug == "Caffeine":
            coffee.set(False)
        if drug == "Ethanol":
            coffee.set(False)
        current_drug_list.remove(drug)
        listbox_drugs.delete(index)
        print("Retrait du médicament:", drug)
        output, int_list = check_all_interaction(current_drug_list, cursor)
        mark_interaction(int_list)
        output_interactions(output)

    except IndexError:
        print("Aucun médicament sélectionné pour suppression.")

# Affichage de boutons recherche, ajout, alarme
ttk.Button(frame_profil, text="Chercher médicament", command=lookup_drug).grid(column=2, row=1)
ttk.Button(frame_profil, text="Ajouter médicament", command=add_drug).grid(column=1, row=1)
ttk.Button(frame_profil, text="Définir une alarme", command=alert_oops).grid(column=3, row=1)

# Affichage liste medicaments
ttk.Label(frame_profil, text="Liste des médicaments:").grid(column=0, row=4, columnspan=3, sticky=tk.W)
listbox_drugs = tk.Listbox(frame_profil, height=6)
listbox_drugs.grid(column=0, row=5, columnspan=2, sticky=(tk.W, tk.E))
listbox_drugs.bind('<Double-1>',  lambda x : lookup_drug(listbox_drugs.curselection()[0]))


# Affichage liste Interractions
ttk.Label(frame_profil, text="Interractions dangereuses:").grid(column=2, row=4, columnspan=3, sticky=tk.W)
text_output = Text(frame_profil, height=6, width=20, wrap=tk.WORD)
text_output.grid(column=2, row=5, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
text_output.tag_configure("red", foreground="red")

# Sauvegarde des infos dans fichier txt
def save_to_text_file():
    text = "Drug list:\n"
    for x in current_drug_list:
        text+= f"- {x}\n"
    text += "\nDangerous interactions:\n"
    text += text_output.get("1.0", tk.END)
    with open("interactions.txt", "w") as file:
        file.write(text)
    print("==> Contents saved to interactions.txt")

# Affichage de boutons save, import
save_button = ttk.Button(root, text="Save to Text File", command=save_to_text_file)
save_button.grid(column=0, row=4, pady=10)
import_button = ttk.Button(root, text="Import from Text File", command=alert_oops)
import_button.grid(column=0, row=5, pady=10)

# Affichage des elements
for child in frame_profil.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Boucle principale
root.mainloop()
