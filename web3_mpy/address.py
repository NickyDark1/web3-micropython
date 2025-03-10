# main/web3_mpy/address.py

import re
from web3_mpy.eth_utils_helpers import (
    add_0x_prefix,
    remove_0x_prefix,
    decode_hex,
    encode_hex,
    hexstr_if_str,
    to_hex,
)
from web3_mpy.keccak import keccak_256

# Funciones auxiliares para detectar tipos en MicroPython
def is_text(value):
    return isinstance(value, str)

def is_bytes(value):
    return isinstance(value, bytes)

# Expresión regular para direcciones hexadecimales (40 dígitos, con o sin "0x")
_HEX_ADDRESS_REGEXP = re.compile(r"(0x)?[0-9a-f]{40}", re.IGNORECASE)

def is_hex_address(value):
    """
    Verifica si el valor (cadena) es una dirección en formato hexadecimal.
    """
    if not is_text(value):
        return False
    return _HEX_ADDRESS_REGEXP.fullmatch(value) is not None

def is_binary_address(value):
    """
    Verifica si el valor (bytes) es una dirección en formato binario (20 bytes).
    """
    return is_bytes(value) and len(value) == 20

def is_address(value):
    """
    Verifica si el valor es una dirección en formato hexadecimal o binario.
    """
    return is_hex_address(value) or is_binary_address(value)

def to_normalized_address(value):
    """
    Convierte una dirección a su representación hexadecimal normalizada (minúsculas con "0x").
    """
    try:
        # Si es cadena, se convierte usando hexstr_if_str y to_hex
        hex_address = hexstr_if_str(to_hex, value).lower()
    except AttributeError:
        raise TypeError("El valor debe ser una cadena o bytes")
    if is_address(hex_address):
        return hex_address
    else:
        raise ValueError("Formato desconocido para la dirección: " + repr(value))

def is_normalized_address(value):
    """
    Verifica si el valor es una dirección normalizada (en minúsculas con "0x").
    """
    if not is_address(value):
        return False
    return value == to_normalized_address(value)

def to_canonical_address(address):
    """
    Convierte una dirección válida a su forma canónica (bytes de 20).
    """
    norm = to_normalized_address(address)
    return decode_hex(norm)

def is_canonical_address(address):
    """
    Verifica si el valor es una dirección canónica (bytes de 20).
    """
    if not is_bytes(address) or len(address) != 20:
        return False
    return address == to_canonical_address(address)

def is_same_address(left, right):
    """
    Comprueba si dos direcciones son iguales (comparación normalizada).
    """
    if not (is_address(left) and is_address(right)):
        raise ValueError("Ambos valores deben ser direcciones válidas")
    return to_normalized_address(left) == to_normalized_address(right)

def public_key_to_eth_address(pub_x, pub_y):
    """
    Deriva la dirección Ethereum:
      - Concat x(32 bytes) + y(32 bytes)
      - keccak_256 => 32 bytes
      - últimos 20 => '0x' + hex
    """
    x_bytes = pub_x.to_bytes(32, 'big')
    y_bytes = pub_y.to_bytes(32, 'big')
    pub_concat = x_bytes + y_bytes
    hashed = keccak_256(pub_concat)
    addr_bytes = hashed[-20:]
    return "0x" + hexlify(addr_bytes).decode('ascii')

def to_checksum_address(address):
    """
    Calcula la dirección EIP-55 en checksummed.
    Asume que 'address' llega con '0x...' en minúsculas.
    """
    addr = address.lower()
    if addr.startswith('0x'):
        addr = addr[2:]
    if len(addr) != 40:
        raise ValueError("La dirección debe tener 40 hex dígitos.")

    hash_bytes = keccak_256(addr.encode('ascii'))
    hash_hex = hexlify(hash_bytes).decode('ascii')  # 64 hex chars

    result = []
    for i, c in enumerate(addr):
        if int(hash_hex[i], 16) >= 8:
            result.append(c.upper())
        else:
            result.append(c.lower())

    return "0x" + "".join(result)

def is_checksum_address(value):
    """
    Verifica si la dirección está en formato checksum correcto.
    """
    if not is_text(value) or not is_hex_address(value):
        return False
    return value == to_checksum_address(value)

def _is_checksum_formatted(value):
    unprefixed_value = remove_0x_prefix(value)
    return (not unprefixed_value.islower() and
            not unprefixed_value.isupper() and
            not unprefixed_value.isnumeric())

def is_checksum_formatted_address(value):
    """
    Verifica si la dirección está en formato checksum (no todo minúscula ni todo mayúscula).
    """
    return is_hex_address(value) and _is_checksum_formatted(value)


# (Opcional) funciones para formatear la clave pública comprimida/uncompressed:
def compress_pubkey(pub_x, pub_y):
    prefix = 2 | (pub_y & 1)  # 0x02 si y es par, 0x03 si impar
    prefix_hex = "%02x" % prefix
    x_bytes = pub_x.to_bytes(32, 'big')
    x_hex = hexlify(x_bytes).decode('ascii')
    return "0x" + prefix_hex + x_hex

def uncompressed_pubkey_hex(pub_x, pub_y):
    # '0x04' + 64 hex de x + 64 hex de y
    def pad_left(s, length):
        while len(s) < length:
            s = '0' + s
        return s

    x_hex = hex(pub_x)[2:]
    x_hex = pad_left(x_hex, 64)
    y_hex = hex(pub_y)[2:]
    y_hex = pad_left(y_hex, 64)
    return "0x04" + x_hex + y_hex