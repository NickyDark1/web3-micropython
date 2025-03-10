# main/web3_mpy/web3.py

import urequests
import json
import ubinascii
from web3_mpy.eth_utils import to_checksum_address  # Para validación
from web3_mpy.account import Account

'''
import gc

clear_memory():
    gc.collect()
'''

import gc
import _thread
import time

def memory_cleaner():
    while True:
        gc.collect()
        free = gc.mem_free()
        total = free + gc.mem_alloc()
        #print("GC: {} bytes libres de {} totales".format(free, total))
        time.sleep(120)  # Espera 60 segundos antes de la siguiente recolección

# Inicia el hilo de limpieza de memoria
#_thread.start_new_thread(memory_cleaner, ())



class HTTPProvider:
    def __init__(self, endpoint_uri):
        self.endpoint_uri = endpoint_uri

    def make_request(self, method, params):
        """
        Realiza una petición JSON‑RPC al nodo Ethereum.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        response = urequests.post(
            self.endpoint_uri,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        result = response.json()
        response.close()
        return result

class Eth:
    def __init__(self, web3):
        self.web3 = web3
    
    def eth_avgGasLimit(self, block_identifier="latest"):
        """
        Obtiene el bloque más reciente (sin transacciones completas) y calcula el gas limit promedio
        dividiendo el gasLimit total entre el número de transacciones (si existen).  
        Retorna una tupla (total_gas_limit, avg_gas_limit) en entero.
        """
        response = self.web3.provider.make_request("eth_getBlockByNumber", [block_identifier, False])
        block = response.get("result")
        if block is None:
            raise Exception("No se pudo obtener el bloque")
        total_gas_limit = int(block["gasLimit"], 16)
        tx_hashes = block.get("transactions", [])
        num_txs = len(tx_hashes)
        if num_txs > 0:
            avg = total_gas_limit // num_txs
        else:
            avg = total_gas_limit
        return total_gas_limit, avg

    def eth_gasPrice(self):
        """
        Retorna el precio del gas actual en hexadecimal (cadena) consultando "eth_gasPrice".
        """
        response = self.web3.provider.make_request("eth_gasPrice", [])
        return response.get("result")

    def contract(self, address, abi):
        """
        Crea una instancia de contrato a partir de su dirección y ABI.
        """
        from web3_mpy.contract import Contract
        return Contract(address, abi, self.web3)

    def get_balance(self, address, block_identifier="latest"):
        result = self.web3.provider.make_request("eth_getBalance", [address, block_identifier])
        return result.get("result")

    def get_transaction_count(self, address, block_identifier="latest"):
        result = self.web3.provider.make_request("eth_getTransactionCount", [address, block_identifier])
        #print(f"result: {result}")
        return result.get("result")

    def get_block(self, block_identifier="latest", full_transactions=False):
        result = self.web3.provider.make_request("eth_getBlockByNumber", [block_identifier, full_transactions])
        return result.get("result")

    def get_transaction_by_block_number_and_index(self, block_identifier, index):
        result = self.web3.provider.make_request("eth_getTransactionByBlockNumberAndIndex", [block_identifier, index])
        return result.get("result")
    
    # Métodos adicionales (basados en tu snippet):
    def eth_accounts(self):
        return self.web3.provider.make_request("eth_accounts", [])["result"]

    def eth_blobBaseFee(self):
        return self.web3.provider.make_request("eth_blobBaseFee", [])["result"]

    def eth_blockNumber(self):
        return self.web3.provider.make_request("eth_blockNumber", [])["result"]

    def eth_call(self, transaction_object, block_identifier="latest"):
        return self.web3.provider.make_request("eth_call", [transaction_object, block_identifier])["result"]

    def eth_chainId(self):
        return self.web3.provider.make_request("eth_chainId", [])["result"]

    def eth_coinbase(self):
        return self.web3.provider.make_request("eth_coinbase", [])["result"]

    def eth_createAccessList(self, transaction_object, block_identifier="latest"):
        return self.web3.provider.make_request("eth_createAccessList", [transaction_object, block_identifier])["result"]

    def eth_estimateGas(self, transaction_object, block_identifier="latest"):
        response = self.web3.provider.make_request("eth_estimateGas", [transaction_object, block_identifier])
        #print("eth_estimateGas:", response)
        if "error" in response:
            # Puedes elegir lanzar una excepción o simplemente retornar el mensaje de error.
            raise Exception("Error en eth_estimateGas: " + response["error"]["message"])
        return response["result"]

    def eth_feeHistory(self, block_count, newest_block, reward_percentiles):
        return self.web3.provider.make_request("eth_feeHistory", [block_count, newest_block, reward_percentiles])["result"]

    '''def eth_gasPrice(self):
        return self.web3.provider.make_request("eth_gasPrice", [])["result"]'''

    def eth_getBalance(self, address, block_identifier="latest"):
        return self.web3.provider.make_request("eth_getBalance", [address, block_identifier])["result"]

    def eth_getBlockByHash(self, block_hash, full_tx=False):
        return self.web3.provider.make_request("eth_getBlockByHash", [block_hash, full_tx])["result"]

    def eth_getBlockByNumber(self, block_identifier="latest", full_tx=False):
        return self.web3.provider.make_request("eth_getBlockByNumber", [block_identifier, full_tx])["result"]

    def eth_getBlockReceipts(self, block_hash):
        return self.web3.provider.make_request("eth_getBlockReceipts", [block_hash])["result"]

    def eth_getBlockTransactionCountByBlockHash(self, block_hash):
        return self.web3.provider.make_request("eth_getBlockTransactionCountByBlockHash", [block_hash])["result"]

    def eth_getBlockTransactionCountByBlockNumber(self, block_identifier="latest"):
        return self.web3.provider.make_request("eth_getBlockTransactionCountByBlockNumber", [block_identifier])["result"]

    def eth_getCode(self, address, block_identifier="latest"):
        return self.web3.provider.make_request("eth_getCode", [address, block_identifier])["result"]

    def eth_getLogs(self, filter_object):
        return self.web3.provider.make_request("eth_getLogs", [filter_object])["result"]

    def eth_getProof(self, address, storage_keys, block_identifier="latest"):
        return self.web3.provider.make_request("eth_getProof", [address, storage_keys, block_identifier])["result"]

    def eth_getStorageAt(self, address, position, block_identifier="latest"):
        return self.web3.provider.make_request("eth_getStorageAt", [address, position, block_identifier])["result"]

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, transaction_index):
        return self.web3.provider.make_request("eth_getTransactionByBlockHashAndIndex", [block_hash, transaction_index])["result"]

    def eth_getTransactionByHash(self, transaction_hash):
        return self.web3.provider.make_request("eth_getTransactionByHash", [transaction_hash])["result"]

    def eth_getTransactionReceipt(self, transaction_hash):
        return self.web3.provider.make_request("eth_getTransactionReceipt", [transaction_hash])["result"]


class Web3:
    def __init__(self, provider):
        """
        Inicializa la instancia de Web3 con un proveedor.
        Se crea el submódulo Eth y se inicializa el submódulo Account.
        """
        self.provider = provider  # Por ejemplo, una instancia de HTTPProvider o Provider
        self.eth = Eth(self)
        #from web3_mpy.account import Account
        #self._account = Account(self)
        
        # Inicializa la funcionalidad de cuentas y la asigna a w3.eth.account
        self.eth.account = Account(self)

    @property
    def account(self):
        return self._account

    @property
    def chain_id(self):
        """
        Obtiene el chain_id consultándolo al nodo mediante "eth_chainId".
        Retorna el valor como entero.
        """
        result = self.provider.make_request("eth_chainId", [])
        return int(result.get("result", "0x0"), 16)

    def is_connected(self):
        try:
            version = self.client_version()
            return bool(version)
        except Exception:
            return False

    def client_version(self):
        result = self.provider.make_request("web3_clientVersion", [])
        return result.get("result")

    def is_address(self, address):
        if not isinstance(address, str):
            return False
        if not address.startswith("0x") or len(address) != 42:
            return False
        try:
            int(address[2:], 16)
        except ValueError:
            return False
        return True

    def to_checksum_address(self, address):
        return to_checksum_address(address)

    def to_hex(self, value):
        if isinstance(value, bytes):
            return "0x" + ubinascii.hexlify(value).decode()
        raise TypeError("El valor debe ser de tipo bytes")

    def from_wei(self, value, unit="ether"):
        if unit == "ether":
            return value / 10**18
        return value

    def keccak(self, data):
        from web3_mpy.keccak import keccak_256
        return keccak_256(data)
