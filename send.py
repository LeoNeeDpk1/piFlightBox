import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sender(t, address):
    sock.sendto(bytes(t, 'utf-8'), address)
