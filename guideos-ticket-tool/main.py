#!/usr/bin/python3

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import subprocess

class TicketToolWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="GuideOS Ticket Tool")
        self.set_default_size(400, 200)

        # Vertikale Box für Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.set_child(vbox)

        bug_one_label = Gtk.Label(label="Über diesen Link kannst du direkt ein Ticket in unserem Ticket-System erstellen, um Bugs zu melden oder Features anzufragen. Wie bei einer E-Mail gibst du deinen Namen und deine Adresse ein, so können wir dir ggf. auch direkt antworten.")
        bug_one_label.set_wrap(True)
        bug_one_label.set_max_width_chars(50)
        vbox.append(bug_one_label)

        bug_one_msg = Gtk.Button(label="Zum Ticket-System")
        bug_one_msg.connect("clicked", self.go_ticket_link)
        vbox.append(bug_one_msg)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.append(separator)

        bug_two_label = Gtk.Label(label="Alternativ kannst du auch unser Forum nutzen, um Bugs zu melden. Dort können auch andere Nutzer und Entwickler auf deine Meldung reagieren.")
        bug_two_label.set_wrap(True)
        bug_two_label.set_max_width_chars(50)
        vbox.append(bug_two_label)

        bug_two_msg = Gtk.Button(label="Zum Forums-Bereich")
        bug_two_msg.connect("clicked", self.go_forum_link)
        vbox.append(bug_two_msg)


    def go_ticket_link(self, button):
        print("Button 2 wurde geklickt")

        subprocess.run(["xdg-open", "https://ticket.guideos.de/"])

    def go_forum_link(self, button):
        subprocess.run(["xdg-open", "https://forum.linuxguides.de/index.php?board/54-bugtracker-fehler-melden/"])

class TicketToolApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.guideos.guideos_ticket_tool")

    def do_activate(self):
        win = TicketToolWindow(self)
        win.present()

app = TicketToolApp()
app.run(None)
