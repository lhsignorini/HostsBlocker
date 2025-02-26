import os
import shutil
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog

# Path to the Windows hosts file
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
# IP address to redirect blocked sites (localhost)
REDIRECT_IP = "127.0.0.1"
# Backup file path
BACKUP_PATH = HOSTS_PATH + ".bak"

# Dictionary to store checkboxes
checkboxes = {}

def backup_hosts():
    """ Backup the hosts file before modification. """
    try:
        shutil.copy(HOSTS_PATH, BACKUP_PATH)
    except Exception as e:
        messagebox.showerror("Error", f"Could not backup hosts file:\n{e}")

def read_hosts():
    """ Read the hosts file and return blocked websites. """
    blocked_sites = {}
    try:
        with open(HOSTS_PATH, "r") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == REDIRECT_IP:
                    blocked_sites[parts[1]] = True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read hosts file:\n{e}")
    return blocked_sites

def write_hosts(blocked_sites):
    """ Write the updated blocked sites list to the hosts file. """
    try:
        with open(HOSTS_PATH, "r") as file:
            lines = file.readlines()

        # Remove all old blocked sites
        lines = [line for line in lines if not any(site in line for site in blocked_sites.keys())]

        # Add only checked sites
        for site, blocked in blocked_sites.items():
            if blocked:
                lines.append(f"{REDIRECT_IP} {site}\n")

        # Backup before modifying
        backup_hosts()

        # Write the modified list back
        with open(HOSTS_PATH, "w") as file:
            file.writelines(lines)

        # Flush DNS cache
        os.system("ipconfig /flushdns")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to write to hosts file:\n{e}")

def toggle_block(site):
    """ Toggle blocking for a website. """
    blocked_sites = read_hosts()
    blocked_sites[site] = checkboxes[site].get()
    write_hosts(blocked_sites)
    update_list()

def add_block():
    """ Add a website to the block list. """
    site = site_entry.get().strip().lower()
    if not site:
        messagebox.showwarning("Warning", "Please enter a website (e.g., www.example.com).")
        return

    blocked_sites = read_hosts()
    if site in blocked_sites:
        messagebox.showinfo("Info", f"{site} is already in the list.")
        return

    blocked_sites[site] = True
    write_hosts(blocked_sites)
    update_list()
    site_entry.delete(0, ttk.END)

def update_list():
    """ Update the list of blocked sites with checkboxes. """
    for widget in sites_frame.winfo_children():
        widget.destroy()

    blocked_sites = read_hosts()
    global checkboxes
    checkboxes.clear()

    for site in blocked_sites:
        var = ttk.BooleanVar(value=blocked_sites[site])
        check = ttk.Checkbutton(sites_frame, text=site, variable=var, command=lambda s=site: toggle_block(s))
        check.pack(anchor="w", pady=2)
        checkboxes[site] = var

def on_close():
    """ Flush DNS before closing the application. """
    os.system("ipconfig /flushdns")
    root.destroy()

# --------------------------------
# 🖥️ GUI Setup (Modern UI)
# --------------------------------

root = ttk.Window(themename="superhero")
root.title("Hosts Blocker")
root.geometry("500x400")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

# Input field
ttk.Label(main_frame, text="Enter a website to block:", font=("Arial", 12)).pack(anchor="w")
site_entry = ttk.Entry(main_frame, width=40)
site_entry.pack(pady=5)

ttk.Button(main_frame, text="Block Site", command=add_block, bootstyle="primary").pack(pady=5)

# List of blocked sites with checkboxes
ttk.Label(main_frame, text="Blocked Sites:", font=("Arial", 12)).pack(anchor="w", pady=5)
sites_frame = ttk.Frame(main_frame)
sites_frame.pack(fill="both", expand=True)

update_list()

root.mainloop()
