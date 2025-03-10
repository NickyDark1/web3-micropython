# main/web3_mpy/tx.py

from web3_mpy.rlp import rlp_encode
from web3_mpy.keccak import keccak_256

def encode_tx(tx):
    """
    Codifica la transacción tx (un diccionario) en RLP.
    Se espera que tx contenga los campos:
      nonce, gasPrice, gasLimit, to, value, data, v, r, s.

    IMPORTANTE: Asegurarse de que 'rlp_encode' retorne bytes. Si retorna una str, convertimos con bytes.fromhex.
    """
    encoded = rlp_encode([
        int(tx['nonce']),
        int(tx['gasPrice']),
        int(tx['gasLimit']),
        bytes.fromhex(tx['to'][2:]) if tx['to'].startswith("0x") else tx['to'],
        int(tx['value']),
        bytes.fromhex(tx['data'][2:]) if tx['data'].startswith("0x") else bytes.fromhex(tx['data']),
        int(tx['v']),
        int(tx['r']),
        int(tx['s'])
    ])

    # Convertir si la respuesta de rlp_encode es string
    if isinstance(encoded, str):
        encoded = bytes.fromhex(encoded)

    return encoded


def construct_raw_tx(nonce, gas_price, gas_limit, to, value, data, chain_id=1):
    """
    Construye el diccionario de transacción (sin firma).
    """
    tx = {
        'nonce': nonce,
        'gasPrice': gas_price,
        'gasLimit': gas_limit,
        'to': to,
        'value': value,
        'data': data,
        'v': chain_id,
        'r': 0,
        's': 0
    }

    return tx


def sign_tx(tx, private_key, ecdsa_sign):
    """
    Firma la transacción con la clave privada 'private_key' usando 'ecdsa_sign'.
    1) RLP-encode temp_tx con v=0,r=0,s=0
    2) keccak_256 => tx_hash
    3) ecdsa_sign(tx_hash, private_key)

    Retorna (r, s, recid, tx_hash) asumiendo ecdsa_sign => (r, s, recid).
    """
    temp_tx = dict(tx)
    temp_tx['r'] = 0
    temp_tx['s'] = 0
    #print("sign_tx -> temp_tx: ",temp_tx)

    raw_tx = encode_tx(temp_tx)
    tx_hash = keccak_256(raw_tx)

    # Ajusta si ecdsa_sign retorna (v, r, s) en lugar de (r, s, recid)
    r, s, recid = ecdsa_sign(tx_hash, private_key)
    return r, s, recid, tx_hash


def construct_signed_tx(tx, r, s, chain_id, recid):
    """
    Completa la firma EIP-155: v= chain_id*2 + 35 + recid
    RLP-encode final => bytes
    """
    #print(f"Chain ID used for v calculation: {chain_id}") # Verify chain ID
    v = chain_id * 2 + 35 + recid
    tx['v'] = v
    tx['r'] = r
    tx['s'] = s

    signed_encoded = rlp_encode([
        tx['nonce'],
        tx['gasPrice'],
        tx['gasLimit'],
        bytes.fromhex(tx['to'][2:]) if tx['to'].startswith("0x") else tx['to'],
        tx['value'],
        bytes.fromhex(tx['data'][2:]) if tx['data'].startswith("0x") else tx['data'],
        tx['v'],
        tx['r'],
        tx['s']
    ])

    if isinstance(signed_encoded, str):
        signed_encoded = bytes.fromhex(signed_encoded)

    return signed_encoded
