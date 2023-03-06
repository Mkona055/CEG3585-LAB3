import socket
import threading

SENDREQ = "SENDREQ"
ACK_READY = "ACK_READY"

class Client:

    isServerReady = False

    def __init__(self, socket, address):
        self.socket = socket
        self.address = address

    def encodeB8Z(self,message):
        pulse = "+"
        encodedMessage = ""
        i = 0
        while i < len(message):
            if message[i] == "1":
                if i != 0 :   
                    pulse = self.togglePulse(pulse)
                encodedMessage += pulse
                i += 1
            elif message[i] == "0":
                if i + 7 < len(message) and message[i:i+8] == "00000000":
                    encodedMessage += "000"+ pulse 
                    pulse = self.togglePulse(pulse)
                    encodedMessage += pulse + "0" + pulse 
                    pulse = self.togglePulse(pulse)
                    encodedMessage += pulse
                    i  = i + 8
                else:
                    encodedMessage += "0"
                    i += 1
            else:
                #An invalid character was detected we abort the encoding
                encodedMessage = None
                break
        return encodedMessage
    
    def togglePulse(self,pulse):
        if pulse == "+" :
            return "-"
        else :
            return "+"
            
    def receive_acknowledge(self):
        try:
            while True:
                data = self.socket.recv(1024)
                if not data:
                    print("Deconnecté du serveur")
                    break
                if data.decode('utf-8') == ACK_READY:
                    print("[INFO] ACK_READY received")
                    self.isServerReady = True
        except Exception as e:
            print(e)
            exit(-1)

    def write_message(self):

        try:
            while True:
                message = ""
                while len(message) == 0:
                    message = input("> ")
                    encodedMessage = self.encodeB8Z(message)
                    if (encodedMessage == None):
                        print("[ERROR] An invalid character has been detected in the input. Please only enter 0s and 1s")
                        continue
                    else:
                        encodedMessage = encodedMessage.encode("utf-8")

                    # SEND REQUEST TO SERVER
                    send_req = SENDREQ.encode("utf-8")
                    self.socket.send(send_req)
                    print("[INFO] Request sent to server")

                    # WAIT FOR SERVER ACKNOWLEDGE
                    while True :
                        if self.isServerReady:
                            break
                    
                    # SEND REQUEST TO SERVER
                    self.socket.send(encodedMessage)
                    print("[INFO] Message sent to server")
                    self.isServerReady = False

        except Exception as e:
            print(e)
            self.socket.close()
            exit(-1)


if __name__ == "__main__":

    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 4444  # The port used by the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # on connect le client au serveur
        client_socket.connect((HOST, PORT))
        print("Connecté au serveur sur le port " + str(PORT))

    except ConnectionRefusedError:
        print("La connexion au serveur a echoue ")
        client_socket.close()
        exit(-1)

    try:
        client = Client(client_socket, HOST)
        thread_write_msg = threading.Thread(target=client.write_message)        
        thread_rcv_msg = threading.Thread(target=client.receive_acknowledge)
        thread_write_msg.start()         
        thread_rcv_msg.start()
        thread_write_msg.join()
        thread_rcv_msg.join()
    
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, exiting")
    finally:
        client_socket.close()
