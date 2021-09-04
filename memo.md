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

        


Avec louan, on à débuggé le roque, il fonctionne, il faut vérifier pourquoi les vérifications des attaques des pions ne se font pas correctement, et vérifier uen dernière fois piur les autres pièces. 