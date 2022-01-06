import config, socket, sys
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sender(t):
    sock.sendto(bytes(t, 'utf-8'), config.address)
