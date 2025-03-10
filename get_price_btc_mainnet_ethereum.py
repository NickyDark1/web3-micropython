# main/get_price_btc_mainnet_ethereum.py

import json, time, sys, gc

def clear_memory():
    gc.collect()

# Agrega el directorio actual (donde se encuentran main.py, network_iot.py y web3_mpy) a sys.path
if "/my_modules" not in sys.path:
    sys.path.insert(0, "/main")

from web3_mpy.web3 import Web3, HTTPProvider
from web3_mpy.tx import construct_raw_tx
from web3_mpy.contract import Contract
from network_iot import Network


# Configuración de red Wi-Fi
ssid = ""
password = ""
static_ip_config = None
net = Network(ssid, password, static_ip_config)
if not net.conectar():
    print("Error al conectar la red. Saliendo...")


# Configuración del proveedor (por ejemplo, usando Infura y la red Sepolia)
infura_url = "https://mainnet.infura.io/v3/Token_infura"
provider = HTTPProvider(infura_url)
w3 = Web3(provider)


# Carga del ABI del contrato token (archivo abi.json)
with open('main/abi_oracle_Btc_Usd.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Dirección del contrato del token y la dirección destino
CONTRACT_ADDRESS = "0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"  # Reemplaza con la dirección real del contrato

# Crea una instancia del contrato utilizando la funcionalidad de contratos de la librería
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# Ejemplo de uso con variables de contrato:
#
# Supongamos que has obtenido los siguientes valores con .call():
# - description: una cadena dinámica codificada.
# - decimals: un entero (codificado en 32 bytes).
# - latestAnswer: un entero.
# - latestRoundData: una concatenación de 5 valores (por ejemplo, [roundId, answer, startedAt, updatedAt, answeredInRound]).

# Valores obtenidos (ejemplo):
clear_memory()
description = contract.functions.description().call()
print("Resultado decodificado:", description)

latest_round_data = contract.functions.latestRoundData().call()
print("Resultado decodificado:", latest_round_data)

decimals = contract.functions.decimals().call()
print("Resultado decodificado:", decimals)

latestAnswer = contract.functions.latestAnswer().call()
print("Resultado decodificado:", latestAnswer)
precio_normalizado = latestAnswer / (10 ** decimals)
print("Resultado normalizado:", precio_normalizado)
