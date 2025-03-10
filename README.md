# Web3_mpy - Micropython IOT

![image](https://github.com/user-attachments/assets/00054a92-fb6b-4e2e-b927-e65561d5a015)

# Web3_mpy

`web3_mpy` is a minified version of `web3.py` adapted for use in MicroPython, enabling interaction with the Ethereum blockchain on resource-constrained IoT devices.

## Features
- Compatible with MicroPython.
- Communication with Ethereum nodes via HTTPProvider.
- Support for raw transactions.
- Interaction with smart contracts using ABI.
- Optimized for devices with limited memory.
- Ability to sign transactions and send them to the blockchain.
- Creation of wallets with public and private keys.
- Access to smart contracts for sending tokens, reading methods, and performing advanced interactions.
- Compatibility with any Ethereum Virtual Machine (EVM)-based node.

## Testing and Limitations
This project has been tested on different devices:
- **ESP32**: Successfully used.
- **ESP8266**: memory is the main limitation. It cannot process signatures due to low internal RAM.
- **Raspberry Pi**: Successfully used, but required modifications to some specific libraries due to differences in the execution environment.

It has also interacted with multiple EVM-compatible blockchain networks, including:
- Ethereum (Mainnet and Sepolia)
- Binance Smart Chain (BSC) and BSC Testnet
- Polygon
- Arbitrum

The main security firewall is based on MicroPython.

## Installation
Since MicroPython does not natively support `pip`, you must manually copy the `web3_mpy` files to your IoT device.

1. Clone or download this repository.
2. Import the modules into your MicroPython code.

## Usage
Below is an example of how to connect an IoT device to the Ethereum blockchain and retrieve the BTC/USD price from a Chainlink smart contract.

```python
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

```

## Dependencies
- MicroPython with support for `ujson` and `urequests`.
- An Ethereum RPC provider such as Infura or Alchemy.
- An IoT device with WiFi connectivity.

## Contributions
Contributions are welcome. If you want to improve the library, fork the repository and submit a Pull Request with your changes.

## License
This project is licensed under the MIT License.

## Donations
If you like this project and want to support it, you can donate:

- **Buy me a coffee ☕**
  - Ethereum Wallet: `0x06701723194aF926f01D8480fA559642c425f077`

- **Get to work and improve the library 💪**
  - Ethereum Wallet: `0x1461039624C4461C1b2a9805DCa9bdf97AD81538`

