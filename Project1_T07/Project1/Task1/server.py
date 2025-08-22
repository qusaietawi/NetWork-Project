import socket
import os
from urllib.parse import unquote

HOST = 'localhost'
PORT = 5012
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_mime_type(file_path):
    if file_path.endswith(".html"):
        return "text/html"
    elif file_path.endswith(".css"):
        return "text/css"
    elif file_path.endswith(".png"):
        return "image/png"
    elif file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    elif file_path.endswith(".mp4"):
        return "video/mp4"
    else:
        return "application/octet-stream"

def handle_request(conn, addr):
    request = conn.recv(2048).decode(errors='ignore')
    if not request:
        conn.close()
        return

    print(f"\n📥 HTTP Request from {addr}:\n{request.strip()}")

    lines = request.split('\r\n')
    if len(lines) < 1:
        conn.close()
        return

    request_line = lines[0]
    try:
        method, path, _ = request_line.split()
    except ValueError:
        conn.close()
        return

    path = unquote(path)

    if path in ['/', '/index.html', '/main_en.html', '/en']:
        file_path = os.path.join(BASE_DIR, 'html', 'main_en.html')
    elif path in ['/ar', '/main_ar.html']:
        file_path = os.path.join(BASE_DIR, 'html', 'main_ar.html')
    elif path.startswith('/event?'):
        keyword = unquote(path.split('=')[-1]).lower()

        if keyword == "hospital":
            file_path = os.path.join(BASE_DIR, 'html', 'event_details.html')
        elif keyword == "مجزرة":
            file_path = os.path.join(BASE_DIR, 'html', 'event_details_ar.html')
        else:
            video_keywords = ["video", "youtube", "فيديو", "يوتيوب"]
            image_keywords = ["image", "jpg", "png", "صورة", "صور"]

            if any(kw in keyword for kw in video_keywords):
                redirect_url = f"https://www.youtube.com/results?search_query={keyword}"
            elif any(kw in keyword for kw in image_keywords):
                redirect_url = f"https://www.google.com/search?q={keyword}&udm=2"
            else:
                redirect_url = f"https://www.aljazeera.com/search/{keyword}"

            response = (
                "HTTP/1.1 307 Temporary Redirect\r\n"
                f"Location: {redirect_url}\r\n\r\n"
            )
            conn.send(response.encode())
            conn.close()
            return
    else:
        file_path = os.path.join(BASE_DIR, path.lstrip("/"))

    if not os.path.exists(file_path):
        error_body = (
            "<html><head><title>Error 404</title></head>"
            "<body><h1 style='color:red'>The file is not found</h1>"
            f"<p>Client: {addr[0]}:{addr[1]}</p></body></html>"
        )
        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(error_body)}\r\n\r\n"
            f"{error_body}"
        )
        conn.send(response.encode())
        conn.close()
        return

    mime_type = get_mime_type(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()

    response_headers = (
        "HTTP/1.1 200 OK\r\n"
        f"Content-Type: {mime_type}\r\n"
        f"Content-Length: {len(content)}\r\n\r\n"
    )

    conn.send(response_headers.encode() + content)
    conn.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(10)
        print(f"🚀 Web server is running at http://{HOST}:{PORT}/")

        while True:
            conn, addr = s.accept()
            handle_request(conn, addr)

if __name__ == '__main__':
    run_server()
