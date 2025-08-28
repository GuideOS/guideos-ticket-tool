#!/usr/bin/python3

import os
import requests
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from azure_ttk import *
from tkfilebrowser import askopendirname, askopenfilenames, asksaveasfilename

# API-Token
api_token = "991c757492f78675cbbe6d887e63051e058fe40a"

if not api_token:
    raise ValueError("API-Token nicht gefunden. Bitte stelle sicher, dass der Token gesetzt ist.")

# Redmine-URL und Projekt-Identifier
redmine_url = "https://bugs.guideos.net"
project_identifier = "guideos"

# Funktion zum Senden der Daten an Redmine
def ticket_erstellen():
    betreff = betreff_entry.get()
    beschreibung = beschreibung_text.get("1.0", tk.END)
    screenshot_path = screenshot_entry.get()
    ticket_typ = tracker_dropdown.get()
    tracker_id = 1 if ticket_typ == "Bug" else 2

    if betreff.strip() == "Gibt einen Titel ein:" or beschreibung.strip() == "Schreibe einen Text:":
        messagebox.showerror("Fehler", "Betreff und Beschreibung dürfen nicht leer sein.")
        return

    elif not betreff.strip() or not beschreibung.strip():
        messagebox.showerror("Fehler", "Betreff und Beschreibung dürfen nicht leer sein.")
        return

    system_info = get_inxi_info()
    full_description = f"{beschreibung}\n\nSysteminformationen:\n{system_info}"

    headers = {
        "X-Redmine-API-Key": api_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "issue": {
            "project_id": project_identifier,
            "subject": betreff,
            "description": full_description,
            "tracker_id": tracker_id
        }
    }

    try:
        response = requests.post(f"{redmine_url}/issues.json", json=payload, headers=headers)
        response.raise_for_status()

        if response.status_code == 201:
            ticket_id = response.json().get("issue", {}).get("id", "unbekannt")
            success_message = f"Ticket erfolgreich erstellt. Ticket-ID: {ticket_id}"

            if screenshot_path:
                upload_response = upload_attachment(ticket_id, screenshot_path)
                if upload_response:
                    success_message += f"\nAnhang {screenshot_path} erfolgreich hinzugefügt."

            show_popup("Erfolg", success_message)

            betreff_entry.delete(0, tk.END)
            betreff_entry.insert("end", "Gibt einen Titel ein:")

            beschreibung_text.delete("1.0", tk.END)
            beschreibung_text.insert("end", "Schreibe einen Text:")

            screenshot_entry.delete(0, tk.END)
            return True
        else:
            show_popup("Fehler", f"Fehler beim Erstellen des Tickets. Statuscode: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        show_popup("Anfragefehler", f"Fehler bei der API-Anfrage: {e}")
        return False

def upload_attachment(ticket_id, file_path):
    try:
        with open(file_path, "rb") as file:
            file_content = file.read()

        url = f"{redmine_url}/uploads.json"
        headers = {
            "X-Redmine-API-Key": api_token,
            "Content-Type": "application/octet-stream",
            "Accept": "application/json",
        }

        response = requests.post(url, headers=headers, data=file_content)
        print("Upload Status Code:", response.status_code)
        print("Upload Response Text:", response.text)
        response.raise_for_status()

        upload_token = response.json().get("upload", {}).get("token")

        issue_update_url = f"{redmine_url}/issues/{ticket_id}.json"
        issue_data = {
            "issue": {
                "uploads": [
                    {
                        "token": upload_token,
                        "filename": os.path.basename(file_path),
                        "description": "Screenshot oder Anhang",
                    }
                ]
            }
        }
        headers["Content-Type"] = "application/json"
        response = requests.put(issue_update_url, json=issue_data, headers=headers)
        print("Attachment Update Status Code:", response.status_code)
        print("Attachment Update Response Text:", response.text)
        response.raise_for_status()
        return True

    except requests.exceptions.RequestException as e:
        show_popup("Fehler", f"Fehler beim Hochladen des Anhangs: {e}")
        return False

def get_inxi_info():
    try:
        result = subprocess.run(["inxi", "-F", "-c", "0"], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return "Fehler: 'inxi' konnte nicht ausgeführt werden."

def show_popup(title, message):
    messagebox.showinfo(title, message)

def create_screenshot():
    subprocess.run(["gnome-screenshot", "--interactive"])

def screenshot_waehlen():
    file_paths = askopenfilenames(
        initialdir=os.path.expanduser("~"),
        title="Wähle einen Screenshot aus",
        filetypes=[("Alle Dateien", "*.*"), ("Bilddateien", "*.png;*.jpg;*.jpeg;*.gif")],
    )
    if file_paths:
        screenshot_entry.delete(0, tk.END)
        file_path_str = ', '.join(file_paths)
        screenshot_entry.insert(0, file_path_str)

def open_bug_page():
    webbrowser.open("https://bugs.guideos.net/projects/guideos-bugtracking/issues?set_filter=1&tracker_id=1")

def del_betreff(event):
    if betreff_entry.get() == "Gibt einen Titel ein:":
        betreff_entry.delete(0, tk.END)

def del_beschreibung_text(event):
    if beschreibung_text.get("1.0", tk.END).strip() == "Schreibe einen Text:":
        beschreibung_text.delete("1.0", tk.END)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

def paste_text():
    try:
        clipboard_text = root.clipboard_get()
        beschreibung_text.insert(tk.INSERT, clipboard_text)
    except tk.TclError:
        pass

# GUI
root = tk.Tk()
root.title("GuideOS Bug melden")
home = os.path.expanduser("~")
script_dir = os.path.dirname(os.path.abspath(__file__))
application_path = os.path.dirname(script_dir)

root.tk.call("source", TCL_THEME_FILE_PATH)

if "dark" in theme_name or "Dark" in theme_name:
    root.tk.call("set_theme", "dark")
else:
    root.tk.call("set_theme", "light")

root.columnconfigure(0, weight=1)

# Tracker-Typ Dropdown
tracker_frame = ttk.LabelFrame(root, text="Art der Meldung", padding=20)
tracker_frame.grid(row=0, column=0, pady=5, padx=20, sticky="ew")
tracker_frame.columnconfigure(0, weight=1)

tracker_dropdown = ttk.Combobox(tracker_frame, values=["Bug", "Feature"], state="readonly")
tracker_dropdown.grid(row=0, column=0, sticky="ew")
tracker_dropdown.set("Bug")

# Betreff
titel_frame = ttk.LabelFrame(root, text="Betreff", padding=20)
titel_frame.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
titel_frame.columnconfigure(0, weight=1)

betreff_entry = ttk.Entry(titel_frame, width=50)
betreff_entry.grid(row=0, column=0, pady=5, sticky="ew")
betreff_entry.insert("end", "Gibt einen Titel ein:")
betreff_entry.bind("<Button-1>", del_betreff)

# Beschreibung
issue_text_frame = ttk.LabelFrame(root, text="Fehlerbeschreibung", padding=20)
issue_text_frame.grid(row=2, column=0, pady=5, padx=20, sticky="ew")
issue_text_frame.columnconfigure(0, weight=1)
issue_text_frame.rowconfigure(0, weight=1)

beschreibung_text = tk.Text(issue_text_frame, borderwidth=0, highlightthickness=1, height=5)
beschreibung_text.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
beschreibung_text.insert("end", "Schreibe einen Text:")
beschreibung_text.bind("<Button-1>", del_beschreibung_text)

# Scrollbar hinzufügen
beschreibung_scrollbar = ttk.Scrollbar(issue_text_frame, orient="vertical", command=beschreibung_text.yview)
beschreibung_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
beschreibung_text.configure(yscrollcommand=beschreibung_scrollbar.set)

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Einfügen", command=paste_text)
beschreibung_text.bind("<Button-3>", show_context_menu)

# Screenshot-Bereich
opt_frame = ttk.LabelFrame(root, text="Screenshot (optional)", padding=20)
opt_frame.grid(row=3, column=0, pady=5, padx=20, sticky="ew")
opt_frame.columnconfigure(0, weight=1)
opt_frame.columnconfigure(1, weight=1)
opt_frame.columnconfigure(2, weight=0)

take_screenshot = ttk.Button(opt_frame, text="Mach' einen Screenshot", command=create_screenshot)
take_screenshot.grid(row=0, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

screenshot_entry = ttk.Entry(opt_frame)
screenshot_entry.grid(row=1, column=0, columnspan=2, padx=5, sticky="ew")

screenshot_button = ttk.Button(opt_frame, text="Durchsuchen", command=screenshot_waehlen)
screenshot_button.grid(row=1, column=2, padx=5, sticky="e")

# Buttons
submit_button = ttk.Button(root, text="Ticket erstellen", command=ticket_erstellen, style="Accent.TButton")
submit_button.grid(row=4, column=0, pady=20, padx=20, sticky="ew")

web_button = ttk.Button(root, text="Alle Meldungen einsehen", command=open_bug_page)
web_button.grid(row=5, column=0, pady=20, padx=20, sticky="ew")

root.mainloop()
