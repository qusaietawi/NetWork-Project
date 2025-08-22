import socket
import time

# Initialize UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('0.0.0.0', 5012))
print(" UDP Server started and listening on port 5012...")

# Data structures
clients = {}  # active players: address -> username
pending_clients = {}  # new players waiting to join next round
used_numbers = set()
game_started = False
round_active = False
submitted_this_round = set()
round_end_time = 0.0
game_over = False  

def broadcast(message):
    to_remove = []
    for addr in clients:
        try:
            server_socket.sendto(message.encode(), addr)
        except Exception as e:
            print(f" Error broadcasting to {clients[addr]} at {addr}: {e}")
            to_remove.append(addr)
    for addr in to_remove:
        if addr in clients:
            print(f" Removing disconnected client: {clients[addr]} at {addr}")
            del clients[addr]

def eliminate_client(address, reason):
    if address in clients:
        try:
            server_socket.sendto(f"ELIMINATED: {reason}".encode(), address)
        except:
            pass
        print(f" Player '{clients[address]}' at {address} eliminated ({reason}).")
        del clients[address]

def start_game():
    global game_started
    game_started = True
    print(" Game starting now!")
    broadcast(" Game starting now!")
    start_round()

def start_round():
    global round_active, round_end_time, submitted_this_round

    # Move pending players to active clients
    for addr, name in pending_clients.items():
        clients[addr] = name
        print(f" Player '{name}' at {addr} is now active for this round.")
        try:
            server_socket.sendto(" Round starting! You can now participate.".encode(), addr)
        except:
            pass
    pending_clients.clear()

    round_active = True
    submitted_this_round = set()
    round_end_time = time.time() + 60
    remaining_numbers = 100 - len(used_numbers)
    broadcast(f" New round started! Submit a unique number (1-100). {remaining_numbers} numbers remain.")
    print(f" New round started. Waiting for players to submit their numbers... ({remaining_numbers} numbers remain)")

def process_submission(address, message):
    if address not in clients:
        return
    if address in submitted_this_round:
        server_socket.sendto(" You already submitted for this round.".encode(), address)
        return
    try:
        number = int(message)
        if number < 1 or number > 100:
            raise ValueError
        if number in used_numbers:
            eliminate_client(address, f"Number {number} already used")
        else:
            used_numbers.add(number)
            submitted_this_round.add(address)
            server_socket.sendto("OK".encode(), address)
            print(f" Player '{clients[address]}' at {address} chose number {number}")
    except ValueError:
        server_socket.sendto("INVALID NUMBER".encode(), address)
        print(f" Player '{clients[address]}' at {address} submitted invalid input: {message}")

def end_round():
    global round_active, game_over
    round_active = False

    # Eliminate clients who didn't submit
    to_eliminate = [addr for addr in clients if addr not in submitted_this_round]
    for addr in to_eliminate:
        eliminate_client(addr, "Did not submit in time")

    # Game end logic
    if len(clients) == 0:
        print(" No players left. Game over.")
        broadcast(" No players left. Game over.")
        game_over = True
        notify_pending_game_over()
        shutdown_server()
    elif len(clients) == 1:
        winner_addr = list(clients.keys())[0]
        winner = clients[winner_addr]
        try:
            server_socket.sendto(f" WINNER: {winner}".encode(), winner_addr)
        except:
            pass
        broadcast(f" WINNER: {winner}")
        print(f" Game Over! Winner: {winner} at {winner_addr}")
        game_over = True
        notify_pending_game_over()
        shutdown_server()
    elif len(used_numbers) >= 100:
        winners = ", ".join(clients.values())
        broadcast(f" GAME OVER: All numbers used. Winners: {winners}")
        print(f" Game Over! All numbers used. Winners: {winners}")
        game_over = True
        notify_pending_game_over()
        shutdown_server()
    else:
        remaining_numbers = 100 - len(used_numbers)
        broadcast(f" Round completed! {len(clients)} players left, {remaining_numbers} numbers remain.")
        print(f" Round completed! {len(clients)} players left, {remaining_numbers} numbers remain.")
        time.sleep(1)
        start_round()

def notify_pending_game_over():
    global pending_clients
    for addr, name in list(pending_clients.items()):
        try:
            server_socket.sendto(" GAME OVER: The game has ended before you could join.".encode(), addr)
            print(f"ℹ Notified pending player '{name}' at {addr} about game over.")
        except:
            pass
        del pending_clients[addr]

def shutdown_server():
    print(" Server is shutting down now.")
    broadcast(" Server shutting down. Thank you for playing!")
    try:
        server_socket.close()
    except:
        pass
    exit(0)

# Main loop
while True:
    try:
        server_socket.settimeout(1.0)
        data, address = server_socket.recvfrom(1024)
        message = data.decode()

        if message == "EXIT":
            if address in clients:
                print(f" Player '{clients[address]}' at {address} left the game.")
                del clients[address]
            elif address in pending_clients:
                print(f" Pending player '{pending_clients[address]}' at {address} left before joining.")
                del pending_clients[address]
            continue

        if address not in clients and address not in pending_clients:
            if game_started and round_active:
                if game_over:
                    try:
                        server_socket.sendto(" GAME OVER: The game has already ended.".encode(), address)
                        print(f"ℹ Rejected new player '{message}' at {address} - game already over.")
                    except:
                        pass
                else:
                    pending_clients[address] = message
                    print(f" New player '{message}' joined mid-round from {address}, will join next round.")
                    server_socket.sendto(" You joined mid-round. Please wait for the next round.".encode(), address)
            else:
                clients[address] = message
                print(f" New player '{message}' joined from {address}")
                server_socket.sendto(" Joined! Please wait for next round.".encode(), address)
                if len(clients) >= 2 and not game_started:
                    start_game()
        else:
            if address in clients:
                if round_active:
                    process_submission(address, message)
                else:
                    if game_started:
                        server_socket.sendto(" Please wait for the next round.".encode(), address)
                    else:
                        server_socket.sendto(" Waiting for more players to start the game.".encode(), address)
            else:
                if game_over:
                    try:
                        server_socket.sendto(" GAME OVER: The game has ended before you could join.".encode(), address)
                    except:
                        pass
                else:
                    server_socket.sendto(" Please wait for the next round.".encode(), address)

    except socket.timeout:
        if game_started and round_active and time.time() > round_end_time:
            end_round()
        elif len(clients) >= 2 and not game_started:
            start_game()
    except Exception as e:
        print(f" Error in main loop: {e}")
        continue
