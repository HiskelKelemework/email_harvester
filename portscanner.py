import threading
import socket
import sys
from queue import Queue


def checkport(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((target, port))
        with print_lock:
            print('Port: ' + str(port) + ' is open')
        con.close()
    except:
        pass


def runner():
    while True:
        worker = port_queue.get()
        checkport(worker)
        port_queue.task_done()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("host arg required, use as portscanner.py <host>")
        sys.exit(1)
    try:
        target = socket.gethostbyname(sys.argv[1])
    except socket.gaierror:
        print('Could not resolve host')
        sys.exit(1)

    port_queue = Queue()
    print_lock = threading.Lock()

    for x in range(100):
        threading.Thread(target=runner, daemon=True).start()

    for port in range(1, 65535):
        port_queue.put(port)

    port_queue.join()
