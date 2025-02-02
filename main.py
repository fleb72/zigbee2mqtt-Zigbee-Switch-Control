from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import asyncio
from button_client import ButtonSNZB01PClient
 
 
 
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
 
# instanciation client MQTT : @IP du broker, port et topic
mqtt_client = ButtonSNZB01PClient("raspberrypi.local", 1883, "zigbee2mqtt/fleb-SNZB-01P-switch")
 
@app.on_event("startup")
def startup_event():
    """ 
    Fonction appelée au démarrage de l'application.
    Connecte le client MQTT et démarre la boucle MQTT.
    """
    print("Appel de la fonction startup")
    mqtt_client.connect()
    print("Connexion MQTT effectuée")
    mqtt_client.start_mqtt_loop()
    print("Boucle MQTT démarrée")
 
 
 
@app.get("/", response_class=HTMLResponse)
async def get():
    """
    Endpoint GET pour la racine de l'application.
    Lit et renvoie le contenu du fichier index.html.
    """
    print("Lecture du fichier index.html")
    with open("index.html", "r") as file: 
        html_content = file.read() 
    print("index.html lu, envoi du contenu au client")
    return HTMLResponse(content=html_content)
 
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket pour gérer les connexions WebSocket.
    Accepte la connexion WebSocket et maintient la connexion ouverte.
    """
    print("connexion WebSocket établie à l'URL /ws")
    await websocket.accept()
    print("Connexion Websocket acceptée")
    mqtt_client.websocket = websocket
    print("Maintien de la connexion Websocket ouverte")
    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Erreur de connexion WebSocket : {e}")
    finally:
        mqtt_client.websocket = None
