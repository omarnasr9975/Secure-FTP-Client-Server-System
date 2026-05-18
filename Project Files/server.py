# ====================== FTP Server Code  ======================
# Features:
#   - Authentication (username + password)
#   - LIST, UPLOAD, DOWNLOAD
#   - DELETE, RENAME, MKDIR, SEARCH
#   - Multi-client support via threading

import socket
import threading
import os

# UserNames + passwords
USERS = {
    "omar": "1234",
    "admin": "admin123",
}

#Directory where all server files are stored
SERVER_DIR = "server_files"
os.makedirs(SERVER_DIR, exist_ok=True)


def authenticate(conn):
    """
    Handles login handshake.
    Returns True if credentials are valid, False otherwise.
    Protocol:
        Client sends  -> "username"
        Server sends  -> "PASS"
        Client sends  -> "password"
        Server sends  -> "AUTH_OK" or "AUTH_FAIL"
    """
    try:
        username = conn.recv(1024).decode().strip()
        conn.send(b"PASS")
        password = conn.recv(1024).decode().strip()

        if USERS.get(username) == password:
            conn.send(b"AUTH_OK")
            print(f"[AUTH] '{username}' logged in successfully.")
            return True
        else:
            conn.send(b"AUTH_FAIL")
            print(f"[AUTH] Failed login attempt for '{username}'.")
            return False
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return False


def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")

    # Step 1: Authenticate 
    if not authenticate(conn):
        print(f"[-] Rejected unauthenticated client: {addr}")
        conn.close()
        return

    # Step 2: Command loop 
    while True:
        try:
            command = conn.recv(1024).decode().strip()

            if not command:
                break

            print(f"[{addr}] Command: {command}")

            # LIST
            if command == "LIST":
                all_entries = []
                for root, dirs, files in os.walk(SERVER_DIR):
                    rel_root = os.path.relpath(root, SERVER_DIR)
                    for d in dirs:
                        all_entries.append(f"[DIR]  {os.path.join(rel_root, d)}")
                    for f in files:
                        all_entries.append(f"[FILE] {os.path.join(rel_root, f)}")
                result = "\n".join(all_entries) if all_entries else "(empty)"
                conn.send(result.encode())

            # UPLOAD 
            elif command.startswith("UPLOAD"):
                parts = command.split(maxsplit=1)
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'wb') as f:
                    print(f"[{addr}] Receiving: {filename}")
                    while True:
                        data = conn.recv(1024)
                        if data == b"__END__":
                            break
                        f.write(data)
                print(f"[{addr}] Upload complete: {filename}")
                conn.send(b"File uploaded successfully.")

            # DOWNLOAD <filename> 
            elif command.startswith("DOWNLOAD"):
                parts = command.split(maxsplit=1)
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)

                if os.path.exists(filepath) and os.path.isfile(filepath):
                    with open(filepath, 'rb') as f:
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            conn.send(data)
                    conn.send(b"__END__")
                    print(f"[{addr}] Sent: {filename}")
                else:
                    conn.send(b"ERROR: File not found.")

            # DELETE 
            elif command.startswith("DELETE"):
                parts = command.split(maxsplit=1)
                filename = parts[1]
                filepath = os.path.join(SERVER_DIR, filename)

                if os.path.exists(filepath) and os.path.isfile(filepath):
                    os.remove(filepath)
                    conn.send(b"File deleted successfully.")
                    print(f"[{addr}] Deleted: {filename}")
                else:
                    conn.send(b"ERROR: File not found.")

            # RENAME
            elif command.startswith("RENAME"):
                parts = command.split(maxsplit=2)
                if len(parts) < 3:
                    conn.send(b"ERROR: Usage: RENAME <old_name> <new_name>")
                else:
                    old_path = os.path.join(SERVER_DIR, parts[1])
                    new_path = os.path.join(SERVER_DIR, parts[2])

                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        conn.send(b"Renamed successfully.")
                        print(f"[{addr}] Renamed: {parts[1]} -> {parts[2]}")
                    else:
                        conn.send(b"ERROR: File/folder not found.")

            # MKDIR
            elif command.startswith("MKDIR"):
                parts = command.split(maxsplit=1)
                folder = parts[1]
                folder_path = os.path.join(SERVER_DIR, folder)

                if os.path.exists(folder_path):
                    conn.send(b"ERROR: Folder already exists.")
                else:
                    os.makedirs(folder_path, exist_ok=True)
                    conn.send(b"Folder created successfully.")
                    print(f"[{addr}] Created folder: {folder}")

            # SEARCH <query>
            elif command.startswith("SEARCH"):
                parts = command.split(maxsplit=1)
                query = parts[1].lower()
                matches = []

                for root, dirs, files in os.walk(SERVER_DIR):
                    for name in dirs + files:
                        if query in name.lower():
                            rel_path = os.path.relpath(os.path.join(root, name), SERVER_DIR)
                            entry_type = "[DIR] " if name in dirs else "[FILE]"
                            matches.append(f"{entry_type} {rel_path}")

                result = "\n".join(matches) if matches else "No matches found."
                conn.send(result.encode())

            else:
                conn.send(b"ERROR: Invalid command.")

        except Exception as e:
            print(f"[ERROR] Client {addr}: {e}")
            break

    print(f"[-] Connection closed: {addr}")
    conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 2121))
    server.listen(5)
    print("[*] FTP Server running on port 2121...")
    print(f"[*] Serving files from: {os.path.abspath(SERVER_DIR)}\n")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


start_server()
