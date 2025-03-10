# main/web3_mpy/account.py

import time
from web3_mpy.tx import sign_tx, construct_signed_tx

from web3_mpy.ecdsa import ecdsa_sign
from web3_mpy.wallet import Wallet  # Importa la clase Wallet

class Account:
    def __init__(self, web3):
        self.web3 = web3

    def create_account(self):
        """
        Genera una nueva cuenta Ethereum usando la clase Wallet.
        Retorna un diccionario con la clave privada y la dirección.
        """
        private_key, address = Wallet.generate_keypair()
        return {"private_key": private_key, "address": address}

    def sign_transaction(self, tx, private_key_hex):
        # Convierte la clave privada hex a bytes:
        if private_key_hex.startswith("0x"):
            private_key_hex = private_key_hex[2:]
        priv_bytes = bytes.fromhex(private_key_hex)

        # (r, s, recid, tx_hash) = sign_tx(..., priv_bytes, ecdsa_sign)
        r, s, recid, tx_hash = sign_tx(tx, priv_bytes, ecdsa_sign)

        raw_tx = construct_signed_tx(
            tx,
            r,
            s,
            self.web3.chain_id,
            recid
        )
        return {
            "rawTransaction": raw_tx,
            "transactionHash": tx_hash
        }

    
    


    def send_raw_transaction(self, signed_tx):
        """
        Envía la transacción firmada al nodo Ethereum.
        Retorna el hash de la transacción o un error.
        """
        result = self.web3.provider.make_request("eth_sendRawTransaction", ["0x" + signed_tx.hex()])
        if result.get("result"):
            return result.get("result")
        else:
            return result.get("error")

    def wait_for_transaction_receipt(self, tx_hash, timeout=60):
        """
        Hace polling hasta obtener el recibo de la transacción o hasta expirar 'timeout' (segundos).
        """
        start = time.time()
        while time.time() - start < timeout:
            receipt = self.web3.provider.make_request("eth_getTransactionReceipt", [tx_hash])
            if receipt.get("result"):
                return receipt.get("result")
            time.sleep(1)
        return None

    @property
    def gas_price(self):
        """
        Retorna el precio del gas actual (en wei) consultando "eth_gasPrice".
        """
        result = self.web3.provider.make_request("eth_gasPrice", [])
        return int(result.get("result", "0x0"), 16)
