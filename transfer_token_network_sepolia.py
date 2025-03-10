# main/transfer_token_network_sepolia.py

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
infura_url = "https://sepolia.infura.io/v3/Token_infura"
provider = HTTPProvider(infura_url)
w3 = Web3(provider)


print("chain_id:",w3.chain_id)
clear_memory()

# Se espera que en la inicialización de Web3 se asigne la funcionalidad de cuenta en w3.eth.account
# Ejemplo de clave privada (no la uses en producción, es solo para ejemplo)
private_key = ""

# dirección del remitente
sender_address = ""
print("sender_address:",sender_address)

# Carga del ABI del contrato token (archivo abi.json)
with open('main/abi.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

# Dirección del contrato del token y la dirección destino
CONTRACT_ADDRESS = "0x29f2D40B0605204364af54EC677bD022dA425d03"  # Reemplaza con la dirección real del contrato
TO_ADDRESS = sender_address # Dirección a la que enviarás el token

# Crea una instancia del contrato utilizando la funcionalidad de contratos de la librería
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

def transfer_token(private_key, to_address, token_amount):
    """
    Realiza la transferencia de token:
      - token_amount debe especificarse en la unidad mínima (por ejemplo, w3.to_wei(1, 'ether') para tokens con 18 decimales)
    """
    # Obtén el nonce de la cuenta del remitente
    nonce = int(w3.eth.get_transaction_count(sender_address, "latest"),16)
    print("nonce:",nonce)
    clear_memory()

    # Construye la llamada a la función transfer del contrato
    # Se codifica la función transfer(_to, _value) utilizando la lógica implementada en tu librería
    tx_payload = contract.functions.transfer(to_address, token_amount)
    #print("tx_payload:",tx_payload)

    
    # Construir el objeto de transacción para la estimación:
    tx_object = {
        "from": sender_address,    # Dirección del remitente
        "to": CONTRACT_ADDRESS,      # Dirección del contrato
        "data": "0x" + tx_payload.data.hex(),  # Datos codificados de la función
        "value": hex(0)                 # Sin enviar Ether (para tokens)
    }
    print("tx_object:",tx_object)
    clear_memory()
    
    # Estimar el gas:
    gas_estimated_hex = w3.eth.eth_estimateGas(tx_object, "latest")
    print("gas_estimated_hex:",gas_estimated_hex)

    gas_estimated = int(gas_estimated_hex, 16)
    print("Gas estimado:", gas_estimated)
    
    # Agregar un margen de seguridad (por ejemplo, 20% extra):
    gas_limit = int(gas_estimated * 1.2)


    # Arma la transacción: se envía a la dirección del contrato, sin transferir Ether (value=0)
    tx = {
        'nonce': nonce,
        'gasPrice': w3.eth.account.gas_price,  # Puedes ajustar o utilizar una estrategia para el gasPrice
        'gasLimit': gas_limit,                    # Ajusta el límite de gas según sea necesario
        'to': CONTRACT_ADDRESS,
        'value': 0,                          # No se envía Ether en la transferencia de tokens
        'data': "0x" + tx_payload.data.hex(), # Payload de la llamada a transfer
        'chain_id': w3.chain_id
    }

    # Construye la transacción sin firmar (raw transaction)
    raw_tx = construct_raw_tx(
        nonce=tx['nonce'],
        gas_price=tx['gasPrice'],
        gas_limit=tx['gasLimit'],
        to=tx['to'],
        value=tx['value'],
        data=tx['data'],
        chain_id=tx['chain_id']
    )

    # Firma la transacción usando la clave privada a través de w3.eth.account
    signed = w3.eth.account.sign_transaction(raw_tx, private_key)
    print("Transacción firmada (RLP en hexadecimal):")
    print(signed["rawTransaction"].hex())
    clear_memory()

    # Envía la transacción firmada
    tx_hash = w3.eth.account.send_raw_transaction(signed["rawTransaction"])
    print("Transaction hash:", tx_hash)

    # (Opcional) Espera la confirmación de la transacción consultando el blockNumber
    while w3.eth.eth_getTransactionByHash(tx_hash)['blockNumber'] is None:
        print("Esperando confirmación...")
        time.sleep(4)
    
    '''
    # con el tiempo de espera para mostrar mensaje de "recibo" o "no recibo"
    receipt = w3.eth.account.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt:
        print("Recibo de transacción:", receipt)
    else:
        print("No se obtuvo recibo en el tiempo especificado.")
    '''

# Ejemplo de uso: enviar 1000000 wei token (opcional considerando 18 decimales)
token_amount = 1000000
print("token_amount:",token_amount)
transfer_token(private_key, TO_ADDRESS, token_amount)

'''
OUTPUT ESPERADO:

Conectando a la red: XXX
Esperando conexión...
Esperando conexión...
Esperando conexión...
Conexión establecida. Configuración: ('192.168.1.101', '255.255.255.0', '192.168.1.1', '8.8.8.8')
sender_address: 
token_amount: 1000000
nonce: 140
tx_object: {'value': '0x0', 'data': '', 'to': '', 'from': ''}
gas_estimated_hex: 0x7593
Gas estimado: 30099
Transacción firmada (RLP en hexadecimal):

Transaction hash: 
Esperando confirmación...
Esperando confirmación...
Esperando confirmación...

'''