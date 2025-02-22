#!/usr/bin/env python3
import sys
import ssl
import socket
import json
import argparse
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ParsedArguments:
    use_tls: bool
    port: int
    hostname: str
    netid: str

class ArgumentParserCustom:
    # ARGUMENT PARSER CLASS
    def __init__(self, args: List[str]):
        self.args = args
        self.parsed_args = self.parse_arguments()

    def parse_arguments(self) -> ParsedArguments:
        parser = argparse.ArgumentParser(
            description="Number Guessing Game Client",
            usage="%(prog)s [-p port] [-s] <hostname> <NetID>"
        )
        parser.add_argument('-s', action='store_true', help='Use TLS for the connection')
        parser.add_argument('-p', type=int, help='Specify the port number')
        parser.add_argument('hostname', type=str, help='Server hostname')
        parser.add_argument('netid', type=str, help='Your NetID')

        args = parser.parse_args(self.args[1:])

        if args.p is None:
            args.p = 49513 if args.s else 49152

        # print(f"Using TLS: {args.s}")
        # print(f"Port: {args.p}")
        # print(f"Hostname: {self.args[-2]}")
        # print(f"NetID: {self.args[-1]}")

        return ParsedArguments(
            use_tls=args.s,
            port=args.p,
            hostname=args.hostname,
            netid=args.netid
        )

    def get_args(self) -> ParsedArguments:
        return self.parsed_args


class NumberGuessingGameClient:
    # CLIENT
    def __init__(self, args: List[str]):
        self.args = ArgumentParserCustom(args).get_args()
        self.sock = None
        self.buffer = ""

    def run(self):
        try:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5) 
                sock.connect((self.args.hostname, self.args.port))
                # print(f"Connected to {self.args.hostname}:{self.args.port}")
            except socket.error as e:
                # print(f"Error connecting to {self.args.hostname}:{self.args.port}: {e}", file=sys.stderr)
                sys.exit(1)
            if self.args.use_tls:
                try:
                    context = ssl.create_default_context()
                    sock = context.wrap_socket(sock, server_hostname=self.args.hostname)
                    # print("TLS connection established.")
                except Error as e:
                    sys.exit(1)

            self.sock = sock

            hi_message = {"type": "HI", "netid": self.args.netid}
            try:
                self.sock.sendall((json.dumps(hi_message) + "\n").encode('utf-8'))
                # print(f"Sent HI message: {hi_message}")
            except socket.error as e:
                # print(f"Error sending HI message: {e}", file=sys.stderr)
                sys.exit(1)

            low_val = None
            high_val = None

            while True:
                
                try:
                    data = self.sock.recv(4096)
                except socket.timeout:
                    # print("Timeout receiving data from server.", file=sys.stderr)
                
                    try:
                        wry_message = {"type": "WRY"}
                        self.sock.sendall((json.dumps(wry_message) + "\n").encode('utf-8'))
                        # print(f"Sent message: {wry_message}")
                    except socket.error as e:
                        # print(f"Error sending message {wry_message}: {e}", file=sys.stderr)
                        sys.exit(1)
                    continue
                except socket.error as e:
                    # print(f"Error receiving data: {e}", file=sys.stderr)
                    sys.exit(1)

                if not data:
                    # print("Error: Server closed connection unexpectedly.", file=sys.stderr)
                    sys.exit(1)

                self.buffer += data.decode('utf-8', errors='replace')
                lines = self.buffer.split('\n')
                self.buffer = lines[-1]  
                messages = lines[:-1] 

                parsed_messages = []
                for line in messages:
                    if not line.sdt():
                        continue  
                    try:
                        msg = json.loads(line)
                        parsed_messages.append(msg)
                        # print(f"Received message: {msg}")
                    except json.JSONDecodeError:
                        # print(f"Failed to parse message: {line}", file=sys.stderr)
                        # envoyer({"type": "WRY"})
                        try:
                            wry_message = {"type": "WRY"}
                            self.sock.sendall((json.dumps(wry_message) + "\n").encode('utf-8'))
                            # print(f"Sent message: {wry_message}")
                        except socket.error as e:
                            # print(f"Error sending message {wry_message}: {e}", file=sys.stderr)
                            sys.exit(1)
                

                for msg in parsed_messages:
                    mtype = msg.get("type", "")
                    if mtype == "AYE":
                        low_val = msg.get("min")
                        high_val = msg.get("max")
                        if not isinstance(low_val, int) or not isinstance(high_val, int):
                            # print("Error: Invalid AYE message format. 'min' and 'max' must be integers.", file=sys.stderr)
                            sys.exit(1)
                        # print(f"Received AYE message: min={low_val}, max={high_val}")
                        break
                    elif mtype == "BYE":
                        flag = msg.get("flag", "")
                        print(flag)
                        self.sock.close()
                        return
                if low_val is not None and high_val is not None:
                    break 

            lo, hi = low_val, high_val
            attempt = 1  
            while lo <= hi:
                guess = lo + (hi - lo) // 2
                # print(f"Attempt {attempt}: Guessing {guess}")
                # envoyer({"type": "TRY", "guess": guess})
                try:
                    try_message = {"type": "TRY", "guess": guess}
                    self.sock.sendall((json.dumps(try_message) + "\n").encode('utf-8'))
                    # print(f"Sent message: {try_message}")
                except socket.error as e:
                    # print(f"Error sending message {try_message}: {e}", file=sys.stderr)
                    sys.exit(1)

                while True:
                    # Ingest logic starts here
                    try:
                        data = self.sock.recv(4096)
                    except socket.timeout:
                        # print("Timeout receiving data from server.", file=sys.stderr)
                        # envoyer({"type": "WRY"})
                        try:
                            wry_message = {"type": "WRY"}
                            self.sock.sendall((json.dumps(wry_message) + "\n").encode('utf-8'))
                            # print(f"Sent message: {wry_message}")
                        except socket.error as e:
                            # print(f"Error sending message {wry_message}: {e}", file=sys.stderr)
                            sys.exit(1)
                        continue
                    except socket.error as e:
                        # print(f"Error receiving data: {e}", file=sys.stderr)
                        sys.exit(1)

                    if not data:
                        # print("Error: Server closed connection unexpectedly.", file=sys.stderr)
                        sys.exit(1)

                    self.buffer += data.decode('utf-8', errors='replace')
                    lines = self.buffer.split('\n')
                    self.buffer = lines[-1]  
                    messages = lines[:-1] 

                    parsed_messages = []
                    for line in messages:
                        if not line.sdt():
                            continue  
                        try:
                            msg = json.loads(line)
                            parsed_messages.append(msg)
                            # print(f"Received message: {msg}")
                        except json.JSONDecodeError:
                            # print(f"Failed to parse message: {line}", file=sys.stderr)
                            # envoyer({"type": "WRY"})
                            try:
                                wry_message = {"type": "WRY"}
                                self.sock.sendall((json.dumps(wry_message) + "\n").encode('utf-8'))
                                # print(f"Sent message: {wry_message}")
                            except socket.error as e:
                                # print(f"Error sending message {wry_message}: {e}", file=sys.stderr)
                                sys.exit(1)
                    # Ingest logic ends here

                    for msg in parsed_messages:
                        mtype = msg.get("type", "")
                        if mtype == "NIGH":
                            hint = msg.get("hint", "").lower()  
                            # print(f"Received NIGH message: {hint}")

                            if hint == "too low":
                                lo = (lo + (hi - lo) // 2) + 1
                                # print(f"Updating lo to {lo}")
                            elif hint == "too high":
                                hi = (lo + (hi - lo) // 2) - 1
                                # print(f"Updating hi to {hi}")
                            else:
                                # print(f"Unknown hint received: '{hint}'", file=sys.stderr)
                                self.sock.close()
                                sys.exit(1)
                            break  
                        elif mtype == "BYE":
                            flag = msg.get("flag", "")
                            print(flag)
                            self.sock.close()
                            return
                    else:
                        continue  
                    break 
                attempt += 1  

            # print("Exited guessing loop without receiving BYE message.", file=sys.stderr)

        except Exception as e:
            # print(f"Error: {e}", file=sys.stderr)
            pass
        finally:
            if self.sock:
                self.sock.close()
                # print("Socket closed.")


def main():
    client = NumberGuessingGameClient(sys.argv)
    client.run()


if __name__ == "__main__":
    main()
