import sys
import ssl
import socket
import json

def read_message(sock):
    try:
        data = sock.recv(4096)  # Receive data from the server
        if not data:
            print("Server closed the connection.", file=sys.stderr)
            return None
        print(f"Raw server response: {data.decode('utf-8', errors='replace')}")  # Print raw response
        return data.decode('utf-8', errors='replace')  # Return the decoded data
    except socket.timeout:
        print("Timeout: No data received from the server.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error receiving data: {e}", file=sys.stderr)
        return None

def create_socket(use_tls, hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)  # Set a 10-second timeout
    sock.connect((hostname, port))
    if use_tls:
        context = ssl.create_default_context()
        tls_sock = context.wrap_socket(sock, server_hostname=hostname)
        tls_sock.settimeout(10)  # Set timeout for TLS socket
        return tls_sock
    else:
        return sock

def send_json_message(sock, message):
    json_message = json.dumps(message)
    message_bytes = json_message.encode('utf-8')
    sock.sendall(message_bytes)

def hit_api(sock, netid):
    # Send the initial "HI" message
    hi_message = {"type": "HI", "netid": netid}
    send_json_message(sock, hi_message)

    # Wait for a response from the server
    response = read_message(sock)
    if response:
        print(f"Server response: {response}")

def main():
    netid = 'tk206'
    sock = create_socket(False, cs356-p1.colab.duke.edu, 49152)

    try:
        hit_api(sock, netid)
    except KeyboardInterrupt:
        print("\nClient interrupted by user. Closing connection...", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        sock.close()

if __name__ == "__main__":
    main()