
import socket
import threading
import time

# Initialize UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 5012)

username = input("Please Enter your username: ").strip()
if not username:
    username = "Guest"
client_socket.sendto(username.encode(), server_address)
print(" Connected to server. Waiting for game to start...")

running = True
can_submit = False

def listen_to_server():
    global running, can_submit
    while running:
        try:
            data, _ = client_socket.recvfrom(1024)
            message = data.decode()

            if message == "OK":
                print(" Number accepted. Waiting for next round...\n")
                can_submit = False
            elif message == "LOSE":
                print(" You lost! Number was repeated or invalid.")
                running = False
            elif message == "INVALID NUMBER":
                print(" Invalid input. Please enter a number between 1 and 100.\n")
                can_submit = True
            elif "New round started!" in message:
                print(f" {message}")
                can_submit = True
            elif "Waiting for at least one more player" in message:
                print(" Waiting for others to join... please be patient.")
            elif "already submitted" in message:
                print(" You already submitted for this round.")
            elif "next round" in message:
                print(f" {message}")
            elif message.startswith("ELIMINATED"):
                print(f" {message}")
                running = False
            elif "WINNER" in message or "GAME OVER" in message:
                print(f" {message}")
                running = False
            elif "Server shutting down" in message:
                print(" Server has shut down. Exiting game.")
                running = False
            elif "GAME OVER: The game has ended before you could join." in message:
                print(" The game ended before you could join. Please try again later.")
                running = False
            else:
                print(f" {message}")
        except Exception as e:
            if running:
                print(f" Error receiving message: {e}")
            break

    if running:
        client_socket.close()
        print(" Connection closed. Thank you for playing!")

threading.Thread(target=listen_to_server, daemon=True).start()

while running:
    try:
        if can_submit:
            number = input(" Enter your number (1-100) or 'q' to quit: ").strip()
            if number.lower() == 'q':
                client_socket.sendto("EXIT".encode(), server_address)
                print(" You left the game.")
                running = False
                break
            if number:
                client_socket.sendto(number.encode(), server_address)
                can_submit = False
    except KeyboardInterrupt:
        try:
            client_socket.sendto("EXIT".encode(), server_address)
        except:
            pass
        print("\n Exiting game with Ctrl+C.")
        running = False
        break
    except Exception as e:
        print(f" Error sending number: {e}")
        running = False
        break

can_submit = False
time.sleep(0.5)
client_socket.close()


