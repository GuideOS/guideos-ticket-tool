#!/usr/bin/python3

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio
import subprocess

class TicketToolWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(500, 400)
        self.set_title("Ticket Tool")
        self.set_resizable(False)

        # Header Bar
        header_bar = Adw.HeaderBar()
        
        # Toolbox Layout mit Header Bar
        toolbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        toolbox.append(header_bar)
        
        # Clamp für responsive Zentrierung
        clamp = Adw.Clamp()
        clamp.set_maximum_size(600)
        clamp.set_tightening_threshold(400)
        
        # Main Content Box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        
        # Preferences Group für Forum
        forum_group = Adw.PreferencesGroup()
        forum_group.set_title("Bug im Forum melden")
        forum_group.set_description("Nutze unser Forum, um Bugs zu melden. Dort können auch andere Nutzer und Entwickler auf deine Meldung reagieren.")
        
        # Action Row für Forum
        forum_row = Adw.ActionRow()
        forum_row.set_title("Forum-Bereich öffnen")
        forum_row.set_subtitle("Community-Support und Diskussionen")
        forum_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        forum_row.set_activatable(True)
        forum_row.connect("activated", self.go_forum_link)
        
        forum_group.add(forum_row)
        content_box.append(forum_group)
        
        # Preferences Group für Github
        github_group = Adw.PreferencesGroup()
        github_group.set_title("Bug auf GitHub melden")
        github_group.set_description("Erstelle ein neues Ticket auf GitHub, um uns über einen Bug zu informieren. Bitte beschreibe den Fehler so genau wie möglich und füge ggf. Screenshots oder Log-Dateien hinzu.")
        
        # Action Row für Github
        github_row = Adw.ActionRow()
        github_row.set_title("GitHub Repository öffnen")
        github_row.set_subtitle("Zur Anmeldung benötigst du ein kostenloses GitHub-Konto")
        github_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        github_row.set_activatable(True)
        github_row.connect("activated", self.go_ticket_link)
        
        github_group.add(github_row)
        content_box.append(github_group)
        
        clamp.set_child(content_box)
        toolbox.append(clamp)
        
        self.set_content(toolbox)

    def go_ticket_link(self, row):
        subprocess.run(["xdg-open", "https://github.com/orgs/GuideOS/repositories"])

    def go_forum_link(self, row):
        subprocess.run(["xdg-open", "https://forum.linuxguides.de/index.php?board/54-bugtracker-fehler-melden/"])

class TicketToolApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.guideos.guideos_ticket_tool")

    def do_activate(self):
        win = TicketToolWindow(self)
        win.present()

app = TicketToolApp()
app.run(None)
