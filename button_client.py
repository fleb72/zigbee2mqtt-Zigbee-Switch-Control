import paho.mqtt.client as mqtt
import json
import asyncio
import threading
 
class ButtonSNZB01PClient:
    """
    Client MQTT pour le bouton Sonoff SNZB-01P.
    """
 
    def __init__(self, broker, port, topic, state=False):
        """
        Initialise le client MQTT.
        
        :param broker: Adresse ip du broker MQTT.
        :param port: Port du broker MQTT.
        :param topic: Topic MQTT à souscrire.
        :param state: État initial du switch.
        """
        self.broker = broker
        self.port = port
        self.topic = topic
        self.state = state
        self.client = mqtt.Client()
        self.websocket = None
 
        # fonctions de rappel
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
 
    def connect(self):
        """
        Connecte le client au broker MQTT.
        """
        print("Appel de la méthode connect du broker")
        self.client.connect(self.broker, self.port, 60)
        print("Tentative de connexion au broker...")
 
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """
        Fonction de rappel appelée lors de la connexion au broker MQTT.
        """
        if reason_code == 0:
            print("Connexion au broker réussie !")
            self.client.subscribe(self.topic)
            print(f"Abonné au topic : {self.topic}")
        else:
            print(f"Echec de la connexion au broker, code d'erreur : {reason_code}")
 
    def on_message(self, client, userdata, msg):
        """ 
        Fonction de rappel appelée lors de la réception d'un message MQTT.
        """
        key = 'action'
        try:
            message = json.loads(msg.payload.decode())
            if message.get(key) == "single":
                self.state = not self.state
                print(f"Changement d'état du switch détecté : {self.state}")
                # Envoyer l'état du switch via WebSocket
                print("Envoi de l'état du switch via WebSocket")
                if self.websocket:
                    asyncio.run(self.send_switch_state())
            else:
                print(f"Erreur de clé : {key}")
                self.disconnect()
        except json.JSONDecodeError:
            print(f"Réception de JSON non conforme sur le topic {msg.topic}")
            self.disconnect()
 
    async def send_switch_state(self):
        """
        Envoie l'état du switch via WebSocket.
        """
        if self.websocket:
            print(f"Envoi du JSON via websocket : {{'state' : {self.state}}}")
            await self.websocket.send_json({"state": self.state})
 
 
    def start_mqtt_loop(self):
        """ Démarre la boucle MQTT dans un thread séparé. """
        print("Démarrage de la boucle MQTT dans un thread séparé")
        thread = threading.Thread(target=self.client.loop_forever)
        thread.start()
 
 
    def disconnect(self):
        """
        Déconnecte le client du broker MQTT.
        """
        self.client.disconnect()
        print("Client MQTT déconnecté.")
