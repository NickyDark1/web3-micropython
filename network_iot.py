# main/network_iot.py
import network
import socket
import json
import time

class Network:
    def __init__(self, ssid, password, static_ip_config=None):
        """
        Inicializa la conexión Wi-Fi.
        ssid: Nombre de la red Wi-Fi.
        password: Contraseña de la red.
        static_ip_config: Tupla con la configuración estática 
            (ip, máscara, gateway, DNS) (opcional).
        """
        self.ssid = ssid
        self.password = password
        self.static_ip_config = static_ip_config
        self.wlan = network.WLAN(network.STA_IF)

    def conectar(self):
        """
        Activa la interfaz Wi-Fi y se conecta a la red.
        Si se proporciona static_ip_config, configura la IP estática.
        Espera hasta 30 segundos para lograr la conexión.
        """
        self.wlan.active(True)
        # Configurar IP estática si se proporciona
        if self.static_ip_config:
            print("Configurando IP estática:", self.static_ip_config)
            self.wlan.ifconfig(self.static_ip_config)
        if not self.wlan.isconnected():
            print("Conectando a la red:", self.ssid)
            self.wlan.connect(self.ssid, self.password)
            timeout = 30  # segundos de espera
            start_time = time.time()
            while not self.wlan.isconnected() and time.time() - start_time < timeout:
                print("Esperando conexión...")
                time.sleep(1)
        if self.wlan.isconnected():
            print("Conexión establecida. Configuración:", self.wlan.ifconfig())
            return True
        else:
            print("No se pudo conectar a la red.")
            return False