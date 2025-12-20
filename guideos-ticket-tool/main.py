#!/usr/bin/python3

import os
import requests
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import webbrowser
import mimetypes


# API-Token
api_token = ""

if not api_token:
    raise ValueError("API-Token nicht gefunden. Bitte stelle sicher, dass der Token gesetzt ist.")

redmine_url = ""
project_identifier = "guideos"

class TicketToolWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="GuideOS Bug melden")
        self.set_border_width(10)
        self.set_default_size(500, 600)
        self.set_icon_name("guideos-ticket-tool-logo")

        # Popup beim Start anzeigen
        self.show_startup_popup()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Tracker-Typ Dropdown
        tracker_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(tracker_box, False, False, 0)
        tracker_label = Gtk.Label(label="Art der Meldung:")
        tracker_box.pack_start(tracker_label, False, False, 0)
        self.tracker_dropdown = Gtk.ComboBoxText()
        self.tracker_dropdown.append_text("Bug")
        self.tracker_dropdown.append_text("Feature")
        self.tracker_dropdown.set_active(0)
        tracker_box.pack_start(self.tracker_dropdown, True, True, 0)

        # Systemdaten Checkbox
        self.systemdaten_checkbox = Gtk.CheckButton(label="Systemdaten senden (Optional)")
        self.systemdaten_checkbox.set_active(True)  # Standardmäßig aktiviert
        vbox.pack_start(self.systemdaten_checkbox, False, False, 0)

        # Betreff (mit Placeholder)
        betreff_label = Gtk.Label(label="Betreff:")
        betreff_label.set_halign(Gtk.Align.START)
        vbox.pack_start(betreff_label, False, False, 0)
        self.betreff_entry = Gtk.Entry()
        self.betreff_entry.set_placeholder_text("Gib einen Titel ein")
        vbox.pack_start(self.betreff_entry, False, False, 0)

        # Beschreibung (mit Placeholder-Overlay)
        beschreibung_label = Gtk.Label(label="Fehlerbeschreibung:")
        beschreibung_label.set_halign(Gtk.Align.START)
        vbox.pack_start(beschreibung_label, False, False, 0)

        beschreibung_overlay = Gtk.Overlay()
        self.beschreibung_text = Gtk.TextView()
        self.beschreibung_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.beschreibung_text.set_left_margin(5)
        self.beschreibung_text.set_right_margin(5)
        beschreibung_overlay.add(self.beschreibung_text)

        self.beschreibung_placeholder = Gtk.Label(label="Schreibe einen Text ...")
        self.beschreibung_placeholder.set_halign(Gtk.Align.START)
        self.beschreibung_placeholder.set_valign(Gtk.Align.START)
        self.beschreibung_placeholder.set_margin_start(4)
        self.beschreibung_placeholder.set_margin_top(4)
        self.beschreibung_placeholder.get_style_context().add_class("dim-label")  # grau
        beschreibung_overlay.add_overlay(self.beschreibung_placeholder)

        buffer = self.beschreibung_text.get_buffer()
        buffer.connect("changed", self.toggle_placeholder)

        beschreibung_scroll = Gtk.ScrolledWindow()
        beschreibung_scroll.set_vexpand(True)
        beschreibung_scroll.add(beschreibung_overlay)
        vbox.pack_start(beschreibung_scroll, True, True, 0)

        # Screenshot
        screenshot_label = Gtk.Label(label="Screenshot (optional):")
        screenshot_label.set_halign(Gtk.Align.START)
        vbox.pack_start(screenshot_label, False, False, 0)
        screenshot_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(screenshot_box, False, False, 0)
        self.screenshot_entry = Gtk.Entry()
        screenshot_box.pack_start(self.screenshot_entry, True, True, 0)
        screenshot_button = Gtk.Button(label="Durchsuchen")
        screenshot_button.connect("clicked", self.screenshot_waehlen)
        screenshot_box.pack_start(screenshot_button, False, False, 0)
        take_screenshot = Gtk.Button(label="Mach' einen Screenshot")
        take_screenshot.connect("clicked", self.create_screenshot)
        vbox.pack_start(take_screenshot, False, False, 0)

        # Buttons
        submit_button = Gtk.Button(label="Ticket erstellen")
        submit_button.connect("clicked", self.ticket_erstellen)
        vbox.pack_start(submit_button, False, False, 0)
        web_button = Gtk.Button(label="Alle Meldungen einsehen")
        web_button.connect("clicked", self.open_bug_page)
        vbox.pack_start(web_button, False, False, 0)

    def toggle_placeholder(self, buffer):
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, True)
        if text.strip():
            self.beschreibung_placeholder.hide()
        else:
            self.beschreibung_placeholder.show()

    def show_popup(self, title, message):
        dialog = Gtk.MessageDialog(parent=self, flags=0, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text=title)
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def get_inxi_info(self):
        try:
            result = subprocess.run(["inxi", "-F", "-c", "0"], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return "Fehler: 'inxi' konnte nicht ausgeführt werden."

    def ticket_erstellen(self, widget):
        betreff = self.betreff_entry.get_text()
        buf = self.beschreibung_text.get_buffer()
        start, end = buf.get_bounds()
        beschreibung = buf.get_text(start, end, True)
        screenshot_path = self.screenshot_entry.get_text()
        ticket_typ = self.tracker_dropdown.get_active_text()
        tracker_id = 1 if ticket_typ == "Bug" else 2

        if not betreff.strip() or not beschreibung.strip():
            self.show_popup("Fehler", "Betreff und Beschreibung dürfen nicht leer sein.")
            return

        # Systemdaten nur hinzufügen, wenn Checkbox aktiviert ist
        if self.systemdaten_checkbox.get_active():
            system_info = self.get_inxi_info()
            full_description = f"{beschreibung}\n\nSysteminformationen:\n{system_info}"
        else:
            full_description = beschreibung

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
                    upload_response = self.upload_attachment(ticket_id, screenshot_path)
                    if upload_response:
                        success_message += f"\nAnhang {screenshot_path} erfolgreich hinzugefügt."
                self.show_popup("Erfolg", success_message)
                self.betreff_entry.set_text("")
                buf.set_text("")
                self.screenshot_entry.set_text("")
                self.beschreibung_placeholder.show()
                return True
            else:
                self.show_popup("Fehler", f"Fehler beim Erstellen des Tickets. Statuscode: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.show_popup("Anfragefehler", f"Fehler bei der API-Anfrage: {e}")
            return False

    def upload_attachment(self, ticket_id, file_path):
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
            response.raise_for_status()
            upload_token = response.json().get("upload", {}).get("token")

            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = "application/octet-stream"

            issue_update_url = f"{redmine_url}/issues/{ticket_id}.json"
            issue_data = {
                "issue": {
                    "notes": "Screenshot hinzugefügt",
                    "uploads": [
                        {
                            "token": upload_token,
                            "filename": os.path.basename(file_path),
                            "content_type": mime_type,
                            "description": "Screenshot oder Anhang",
                        }
                    ]
                }
            }
            headers["Content-Type"] = "application/json"
            response = requests.put(issue_update_url, json=issue_data, headers=headers)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            self.show_popup("Fehler", f"Fehler beim Hochladen des Anhangs: {e}")
            return False

    def create_screenshot(self, widget):
        subprocess.run(["gnome-screenshot", "--interactive"])

    def screenshot_waehlen(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Wähle einen Screenshot aus",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Bilddateien")
        filter_img.add_mime_type("image/png")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/gif")
        dialog.add_filter(filter_img)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.screenshot_entry.set_text(dialog.get_filename())
        dialog.destroy()

    def open_bug_page(self, widget):
        webbrowser.open("https://redmine.guideos.net/projects/guideos/issues")

    def show_startup_popup(self):
        message = (
            "Bevor du einen Bug oder ein Feature meldest, "
            "schau bitte nach, ob es zu deinem Thema bereits eine Meldung gibt. "
            "Doppelte Meldungen werden vom Dev-Team in der Regel ignoriert."
            "\n\nBitte melde nur Bugs, die du auch nachvollziehen kannst und gib so viele Details wie möglich an."
            "\n\nBitte verfasse auch für jedes Thema einen eigenen Report."

        )
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Wichtiger Hinweis",
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

win = TicketToolWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
