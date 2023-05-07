import argparse
from server import Server

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="Host address to bind to")
parser.add_argument("--port", type=int, default=1423, help="Port number to bind to")
args = parser.parse_args()

if __name__ == "__main__":
        # start server & accept connections
        # start new thread for processing user request
        server = Server(args.host, args.port)
        server.start()