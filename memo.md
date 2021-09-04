socket :
    connection P2P
        https://info.blaisepascal.fr/nsi-sockets-python

    send:
        sendall(f"{chr(len(msg)+1)}{msg}")
        chr(len(msg))
        for i in range(len(msg)):
            if 2**i > len(msg):
                return 2**i
    recv:    
        ord(msg[0])

        