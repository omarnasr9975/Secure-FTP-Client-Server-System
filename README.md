# 📡 Enhanced FTP Client-Server

A multi-client FTP system built with Python — featuring a dark-themed GUI, user authentication, and full file management over TCP sockets.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Authentication | Username + password login before any command is allowed |
| 📋 List Files | View all files and folders on the server (recursive) |
| ⬆️ Upload | Send a local file to the server |
| ⬇️ Download | Download a file from the server with a Save As dialog |
| 🗑️ Delete | Remove a file from the server (with confirmation) |
| ✏️ Rename | Rename any file or folder on the server |
| 📁 Create Folder | Create a new directory on the server |
| 🔍 Search | Search for files/folders by name (case-insensitive) |
| 👥 Multi-client | Handles multiple clients simultaneously using threading |
| 🖥️ Dark GUI | Clean dark-themed Tkinter interface with a real-time log panel |

---

## 🗂️ Project Structure

```
ftp-client-server/
│
├── server.py          # FTP server — handles all commands + auth
├── client.py          # FTP client — GUI with login screen
└── server_files/      # Auto-created folder where server stores all files
```

---

## ▶️ How to Run

### Requirements

- Python 3.x (no external libraries needed — only standard library)

### Step 1 — Start the Server

```bash
python server.py
```

The server starts on **port 2121** and creates a `server_files/` folder automatically.

### Step 2 — Start the Client

```bash
python client.py
```

A **login window** appears. Enter:

- **Server IP:** `127.0.0.1` (same machine) or the server's actual IP (different machine)
- **Username** and **Password** (see default accounts below)

---

## 🔐 Default User Accounts

| Username | Password |
|---|---|
| `omar` | `1234` |
| `admin` | `admin123` |

To add or change users, edit the `USERS` dictionary at the top of `server.py`:

```python
USERS = {
    "omar": "1234",
    "admin": "admin123",
}
```

---

## 🔌 Authentication Protocol

```
Client  →  username
Server  →  "PASS"
Client  →  password
Server  →  "AUTH_OK"  or  "AUTH_FAIL"
```

If authentication fails, the connection is immediately closed.

---

## 📡 Command Reference

| Command | Format | Description |
|---|---|---|
| `LIST` | `LIST` | Returns all files and folders recursively |
| `UPLOAD` | `UPLOAD <filename>` | Client sends file to server |
| `DOWNLOAD` | `DOWNLOAD <filename>` | Server sends file to client |
| `DELETE` | `DELETE <filename>` | Deletes a file on the server |
| `RENAME` | `RENAME <old> <new>` | Renames a file or folder |
| `MKDIR` | `MKDIR <foldername>` | Creates a new folder |
| `SEARCH` | `SEARCH <query>` | Finds matching files/folders |

---

## 🌐 Running on Two Different Machines (LAN)

1. Find the server machine's local IP:
   - **Windows:** `ipconfig` → look for IPv4 Address
   - **Linux/Mac:** `ip a` or `ifconfig`
2. Make sure both machines are on the same network
3. On the client login screen, enter the server's IP instead of `127.0.0.1`
4. Make sure port **2121** is not blocked by a firewall

---

## 🛠️ Built With

- `socket` — TCP connection between client and server
- `threading` — concurrent handling of multiple clients
- `os` — file system operations
- `tkinter` — GUI (login screen + main window)

---

## 📌 Notes

- Files are chunked at **1024 bytes** per transfer cycle
- End-of-file is signaled with the sentinel `b"__END__"`
- All server files are isolated inside the `server_files/` directory
- The server keeps running indefinitely until manually stopped (`Ctrl+C`)
