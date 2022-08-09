# Import the server module
import http.server
import webbrowser

# Set the hostname
HOST = "localhost"
# Set the port number
PORT = 4000

# Define class to display the index page of the web server
class PythonServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/GUI":
            self.path = "index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


# Declare object of the class
webServer = http.server.HTTPServer((HOST, PORT), PythonServer)
# Print the URL of the webserver, new =2 opens in a new tab
print(f"Server started at http://{HOST}:{PORT}/GUI/")
webbrowser.open(f"http://{HOST}:{PORT}/GUI/", new=2)
print("Website opened in new tab")
print("Press Ctrl+C to quit")
try:
    # Run the web server
    webServer.serve_forever()
except KeyboardInterrupt:
    # Stop the web server
    webServer.server_close()
    print("The server is stopped.")
    exit()
