import requests
import urllib.parse

def enviar_alerta_whatsapp(numero, mensaje, api_key):
    """
    Envía un mensaje por WhatsApp usando CallMeBot
    :param numero: Número en formato internacional, ej. +51912345678
    :param mensaje: Texto del mensaje
    :param api_key: Tu API key de CallMeBot
    """
    try:
        url = (
            f"https://api.callmebot.com/whatsapp.php?"
            f"phone={numero}&"
            f"text={urllib.parse.quote(mensaje)}&"
            f"apikey={api_key}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            print("Mensaje enviado correctamente")
        else:
            print(f"Error al enviar mensaje: {response.text}")
    except Exception as e:
        print(f"Excepción al enviar mensaje: {e}")
