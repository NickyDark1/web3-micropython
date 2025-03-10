# main/transfer_eth.py

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
clear_memory()

# Configuración del proveedor (por ejemplo, usando Infura y la red Sepolia)
# infura_url = "https://sepolia.infura.io/v3/Token_infura"
infura_url= "https://data-seed-prebsc-1-s1.binance.org:8545/"
provider = HTTPProvider(infura_url)
w3 = Web3(provider)

print("chain_id:",w3.chain_id)
clear_memory()

# dirección del remitente
sender_address = ""
print("sender_address:",sender_address)

TO_ADDRESS = sender_address # Dirección a la que enviarás el token


balance_hex = w3.eth.get_balance(sender_address, "latest")
print("balance_hex:", balance_hex)
balance = int(balance_hex, 16)
print("Balance en wei:", balance)
clear_memory()
#time.sleep(2)

def transfer_ether(sender_address,TO_ADDRESS,value, private_key):
    
    # nonce
    nonce = int(w3.eth.get_transaction_count(sender_address, "latest"), 16)
    #print("nonce:",nonce)
    clear_memory()
    #time.sleep(2)
    
    clear_memory()
    tx_object = {
            "from": sender_address,    # Dirección del remitente
            "to": TO_ADDRESS,      # Dirección del contrato
            "data": "0x", #Datos codificados
            "value": hex(value)                 # enviar Ether
        }
    #print("tx_object",tx_object)
    clear_memory()
    gas_estimated_hex = w3.eth.eth_estimateGas(tx_object,  "latest")
    #print("gas_estimated_hex:",gas_estimated_hex)
    clear_memory()

    gas_price = w3.eth.account.gas_price
    gas_estimated = int(gas_estimated_hex, 16)
    gas_limit = int(gas_estimated * 1.2)
    #print(f"gas_estimated: {gas_estimated} | gas_limit: {gas_limit} | gas_price: {gas_price}")
    clear_memory()
    ##time.sleep(2)

    tx = construct_raw_tx(
                nonce=nonce,
                gas_price= gas_price, #30000,    # o usa gas_price
                gas_limit=gas_limit, #35000,    # o usa gas_limit
                to=TO_ADDRESS,
                value=value,
                data="0x",
                chain_id=w3.chain_id
            )

    clear_memory()
    # Firmar transacción con la Account del web3
    # Asumiendo w3.account usa ecdsa_sign internamente
    signed = w3.eth.account.sign_transaction(tx, private_key)
    #print(f"-->> signed: {signed}")
    #print("\nTransacción firmada (RLP en hexadecimal):")
    #print(signed["rawTransaction"].hex())

    clear_memory()
    tx_hash = w3.eth.account.send_raw_transaction(signed["rawTransaction"])
    
    #eth_getTransactionByHash= w3.eth.eth_getTransactionByHash( tx_hash )
    #print("antes del while eth_getTransactionByHash:",eth_getTransactionByHash)
    while w3.eth.eth_getTransactionByHash( tx_hash )['blockNumber'] == None:
        #print("espera...................")
        #time.sleep(4)
        pass
    print("Transaction hash:", tx_hash)
                
    #print("fuera del while")
    '''clear_memory()
    receipt = w3.eth.account.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt:
        print("Recibo de transacción:", receipt)
    else:
        print("No se obtuvo recibo en el tiempo especificado.")
    '''

# Prueba de estrés: ejecutar 50 transacciones y medir el tiempo total
value = 1  # Valor en wei
num_transacciones = 50

# Ejemplo de clave privada
private_key = ""


start_time = time.time()
for i in range(num_transacciones):
    try:
        print(f"\n--- Transacción {i+1} ---")
        time.sleep(1)
        transfer_ether(sender_address, TO_ADDRESS, value, private_key)
        clear_memory()
        time.sleep(1)
    except:
        print("Conexión o memoria saturada")
        clear_memory()
        
end_time = time.time()

total_time = end_time - start_time
print(f"\nTiempo total para {num_transacciones} transacciones: {total_time:.2f} segundos")
print(f"Tiempo promedio por transacción: {total_time/num_transacciones:.2f} segundos")

'''
otput final:

# Prueba 1:
Tiempo total para 50 transacciones: 945.00 segundos
Tiempo promedio por transacción: 18.90 segundos

# Prueba 2:
Tiempo total para 50 transacciones: 693.00 segundos
Tiempo promedio por transacción: 13.86 segundos

(tiempo varia segun la blockchain y numero de transacciones)
'''
