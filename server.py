import math
import pickle
import socket
import threading
import numpy as np

SENDREQ = "SENDREQ"
ACK_READY = "ACK_READY"

class Server:
     
    def __init__(self):
        self.port = 4444
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(("", self.port))

    
    def start(self):
        serverSocket = self.serverSocket
        print(f"Server running on port {self.port}")
        
        # on va faire ecouter le serveur sur le port continuellement

        while True:
            # en lui passe en parametre le nombre de connexion qui peuvent echouer avant de le refuser (facultatif pour py 3.5)
            serverSocket.listen(5)
            # on va initialiser les connexion pour pouvoir les accepter
            # client_addr = adresse IP + port
            client_conn, client_addr = serverSocket.accept()
            print("A client connected to server with IP " +
                      str(client_addr[0]) + " on port " + str(client_addr[1]))
            clientThread = threading.Thread(target=self.receive_message, args=(
                    client_conn, client_addr)) 
            clientThread.start()

    def receive_message(self, client_conn, client_addr):
        try:
            while True:
                data = client_conn.recv(1024)
                if not data:
                    print(str(client_addr) + " disconnected")
                    break
                message = data.decode("utf8")
                if message == SENDREQ :
                    print(f"[INFO] Request received from {client_addr} ")
                    self.send_to(client_conn, ACK_READY)
                    print(f"[INFO] Acknowledge sent to {client_addr} ")

                else :
                    print(f"[INFO] Received from {client_addr} encoded message: {message}")
                    print (f"[INFO] Decoded {message} to : {self.decodeB8Z(message)}")
               
        except Exception as e:
            print(e)
            exit(-1)

    def send_to(self, client_socket, message):

        client_socket.send(message.encode("utf8"))



    def decodeB8Z(self,message):
        decodedMessage = ""
        i = 0
        while i < len(message):
            if message[i] == "+" or message[i] == "-" :
                decodedMessage += "1"
                i += 1
            elif message[i] == "0":
                if i + 7 < len(message) and (message[i : i + 8] == "000+-0-+" or message[i : i + 8] == "000-+0+-"):
                    decodedMessage += "00000000"
                    i +=  8
                else:
                    decodedMessage += "0"
                    i +=  1
        return decodedMessage


        
if __name__ == "__main__":

    server = Server()
    try:
        server.start()
    except Exception as e:
        print(e)
        print("\nServeur s'est arreté")
    finally:
        exit(-1)
