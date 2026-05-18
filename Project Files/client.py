# ====================== FTP Client Code  ======================
# Features:
#   - Login screen with username + password
#   - LIST, UPLOAD, DOWNLOAD, DELETE, RENAME, MKDIR, SEARCH
#   - Improved dark-themed GUI using tkinter

import socket
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, scrolledtext

# Colors & Fonts
BG       = "#1a1a2e"
PANEL    = "#16213e"
ACCENT   = "#0f3460"
BTN      = "#e94560"
BTN_HVR  = "#c73652"
FG       = "#eaeaea"
FG_DIM   = "#a0a0b0"
FONT     = ("Consolas", 10)
FONT_B   = ("Consolas", 10, "bold")
FONT_T   = ("Consolas", 16, "bold")

client = None  # global socket


# Helpers
def styled_button(parent, text, command, width=22):
    btn = tk.Button(
        parent, text=text, command=command,
        bg=BTN, fg="white", activebackground=BTN_HVR,
        activeforeground="white", relief="flat",
        font=FONT_B, cursor="hand2", width=width, pady=6
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HVR))
    btn.bind("<Leave>", lambda e: btn.config(bg=BTN))
    return btn


def log(widget, message, color=None):
    widget.config(state="normal")
    widget.insert(tk.END, message + "\n")
    widget.see(tk.END)
    widget.config(state="disabled")


# Authentication Window
def show_login():
    login_win = tk.Tk()
    login_win.title("FTP Login")
    login_win.geometry("380x320")
    login_win.configure(bg=BG)
    login_win.resizable(False, False)

    # Center window
    login_win.eval('tk::PlaceWindow . center')

    tk.Label(login_win, text="FTP CLIENT", bg=BG, fg=BTN,
             font=("Consolas", 20, "bold")).pack(pady=(30, 5))
    tk.Label(login_win, text="Connect to Server", bg=BG, fg=FG_DIM,
             font=("Consolas", 9)).pack(pady=(0, 20))

    form = tk.Frame(login_win, bg=BG)
    form.pack(padx=30, fill="x")

    # Server IP
    tk.Label(form, text="Server IP", bg=BG, fg=FG_DIM, font=FONT, anchor="w").pack(fill="x")
    ip_var = tk.StringVar(value="127.0.0.1")
    ip_entry = tk.Entry(form, textvariable=ip_var, bg=PANEL, fg=FG, insertbackground=FG,
                        font=FONT, relief="flat", bd=6)
    ip_entry.pack(fill="x", pady=(2, 10))

    # Username
    tk.Label(form, text="Username", bg=BG, fg=FG_DIM, font=FONT, anchor="w").pack(fill="x")
    user_var = tk.StringVar()
    user_entry = tk.Entry(form, textvariable=user_var, bg=PANEL, fg=FG, insertbackground=FG,
                          font=FONT, relief="flat", bd=6)
    user_entry.pack(fill="x", pady=(2, 10))

    # Password
    tk.Label(form, text="Password", bg=BG, fg=FG_DIM, font=FONT, anchor="w").pack(fill="x")
    pass_var = tk.StringVar()
    pass_entry = tk.Entry(form, textvariable=pass_var, show="●", bg=PANEL, fg=FG,
                          insertbackground=FG, font=FONT, relief="flat", bd=6)
    pass_entry.pack(fill="x", pady=(2, 16))

    status_lbl = tk.Label(login_win, text="", bg=BG, fg=BTN, font=FONT)
    status_lbl.pack()

    def try_login():
        global client
        ip = ip_var.get().strip()
        username = user_var.get().strip()
        password = pass_var.get().strip()

        if not username or not password:
            status_lbl.config(text="Fill in all fields.")
            return

        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, 2121))

            # Send username
            client.send(username.encode())
            # Wait for PASS prompt
            prompt = client.recv(1024).decode()
            if prompt != "PASS":
                status_lbl.config(text="Unexpected server response.")
                client.close()
                return

            # Send password
            client.send(password.encode())
            result = client.recv(1024).decode()

            if result == "AUTH_OK":
                login_win.destroy()
                show_main()
            else:
                status_lbl.config(text="Invalid credentials.")
                client.close()
                client = None
        except Exception as e:
            status_lbl.config(text=f"Connection failed: {e}")

    styled_button(login_win, "  Connect & Login", try_login, width=28).pack(pady=(4, 0))
    pass_entry.bind("<Return>", lambda e: try_login())
    user_entry.focus()
    login_win.mainloop()


# Main Application Window
def show_main():
    root = tk.Tk()
    root.title("FTP Client — Connected")
    root.geometry("700x540")
    root.configure(bg=BG)
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    # Header
    header = tk.Frame(root, bg=ACCENT, pady=10)
    header.pack(fill="x")
    tk.Label(header, text="⬡  FTP CLIENT", bg=ACCENT, fg=FG,
             font=("Consolas", 14, "bold")).pack(side="left", padx=20)
    tk.Label(header, text="● CONNECTED", bg=ACCENT, fg="#4ecca3",
             font=("Consolas", 9)).pack(side="right", padx=20)

    # Body 
    body = tk.Frame(root, bg=BG)
    body.pack(fill="both", expand=True, padx=16, pady=12)

    # Left: Buttons
    left = tk.Frame(body, bg=BG)
    left.pack(side="left", fill="y", padx=(0, 12))

    tk.Label(left, text="FILE OPERATIONS", bg=BG, fg=FG_DIM,
             font=("Consolas", 8)).pack(anchor="w", pady=(0, 6))

    # Right: Log output
    right = tk.Frame(body, bg=PANEL, padx=10, pady=10)
    right.pack(side="right", fill="both", expand=True)

    tk.Label(right, text="SERVER LOG", bg=PANEL, fg=FG_DIM,
             font=("Consolas", 8)).pack(anchor="w")

    log_box = scrolledtext.ScrolledText(
        right, bg=PANEL, fg="#4ecca3", font=("Consolas", 9),
        relief="flat", state="disabled", wrap="word",
        insertbackground=FG, bd=0
    )
    log_box.pack(fill="both", expand=True, pady=(4, 0))

    #Command Functions 

    def list_files():
        try:
            client.send(b"LIST")
            data = client.recv(4096).decode()
            log(log_box, "── Server Contents ──────────────────")
            log(log_box, data)
            log(log_box, "─────────────────────────────────────")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def upload_file():
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        filename = filepath.split("/")[-1]
        try:
            client.send(f"UPLOAD {filename}".encode())
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(1024)
                    if not chunk:
                        break
                    client.sendall(chunk)
            client.send(b"__END__")
            status = client.recv(1024).decode()
            log(log_box, f"[UPLOAD] {status}")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def download_file():
        filename = simpledialog.askstring("Download", "Enter filename to download:")
        if not filename:
            return
        try:
            client.send(f"DOWNLOAD {filename}".encode())
            save_path = filedialog.asksaveasfilename(initialfile=filename)
            if not save_path:
                return
            with open(save_path, 'wb') as f:
                while True:
                    data = client.recv(1024)
                    if data == b"__END__":
                        break
                    if data.startswith(b"ERROR"):
                        log(log_box, f"[ERROR] {data.decode()}")
                        return
                    f.write(data)
            log(log_box, f"[DOWNLOAD] '{filename}' saved to {save_path}")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def delete_file():
        filename = simpledialog.askstring("Delete", "Enter filename to delete:")
        if not filename:
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{filename}' from server?")
        if not confirm:
            return
        try:
            client.send(f"DELETE {filename}".encode())
            status = client.recv(1024).decode()
            log(log_box, f"[DELETE] {status}")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def rename_file():
        old_name = simpledialog.askstring("Rename", "Current filename:")
        if not old_name:
            return
        new_name = simpledialog.askstring("Rename", "New filename:")
        if not new_name:
            return
        try:
            client.send(f"RENAME {old_name} {new_name}".encode())
            status = client.recv(1024).decode()
            log(log_box, f"[RENAME] {status}")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def make_folder():
        folder_name = simpledialog.askstring("Create Folder", "Folder name:")
        if not folder_name:
            return
        try:
            client.send(f"MKDIR {folder_name}".encode())
            status = client.recv(1024).decode()
            log(log_box, f"[MKDIR] {status}")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    def search_files():
        query = simpledialog.askstring("Search", "Search keyword:")
        if not query:
            return
        try:
            client.send(f"SEARCH {query}".encode())
            data = client.recv(4096).decode()
            log(log_box, f"── Search results for '{query}' ──────")
            log(log_box, data)
            log(log_box, "─────────────────────────────────────")
        except Exception as e:
            log(log_box, f"[ERROR] {e}")

    #  Build Buttons 
    buttons = [
        ("📋  List Files",      list_files),
        ("⬆  Upload File",     upload_file),
        ("⬇  Download File",   download_file),
        ("🗑  Delete File",     delete_file),
        ("✏  Rename File",     rename_file),
        ("📁  Create Folder",  make_folder),
        ("🔍  Search Files",   search_files),
    ]

    for label, cmd in buttons:
        styled_button(left, label, cmd).pack(pady=4, fill="x")

    log(log_box, "[SYSTEM] Connected to server. Ready.\n")

    # Status Bar 
    status_bar = tk.Frame(root, bg=ACCENT, pady=4)
    status_bar.pack(fill="x", side="bottom")
    tk.Label(status_bar, text="Port: 2121  |  Protocol: TCP  |  Mode: Enhanced FTP",
             bg=ACCENT, fg=FG_DIM, font=("Consolas", 8)).pack(side="left", padx=12)

    #  Close handler
    def on_closing():
        if client:
            try:
                client.close()
            except:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


# Entry Point 
show_login()