# main/web3_mpy/provider.py


import urequests
import json, gc

class Provider:
    def __init__(self, endpoint_uri):
        """
        Inicializa el proveedor con la URL del nodo (por ejemplo, Infura).
        """
        self.endpoint_uri = endpoint_uri

    def make_request(self, method, params):
        """
        Realiza una petición JSON‑RPC al nodo Ethereum.
        
        :param method: Nombre del método JSON‑RPC (por ejemplo, "eth_getBalance").
        :param params: Lista de parámetros para la llamada.
        :return: Diccionario con la respuesta del nodo.
        """
        gc.collect()  # Liberar memoria antes de la solicitud
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        try:
            response = urequests.post(
                self.endpoint_uri,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            # Convertir la respuesta a un diccionario
            result = response.json()
        finally:
            response.close()
        return result
