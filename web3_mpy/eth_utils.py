# main/web3_mpy/eth_utils.py

# Utilizamos importaciones absolutas para que se encuentre el módulo eth_utils_helpers dentro de web3_mpy
from web3_mpy.eth_utils_helpers import (
    add_0x_prefix,
    remove_0x_prefix,
    decode_hex,
    encode_hex,
    hexstr_if_str,
    to_hex
)
from web3_mpy.keccak import keccak_256  # Asegúrate de que este módulo exista en web3_mpy/keccak.py

def apply_to_return_value(func):
    """
    Decorador que aplica 'func' al valor de retorno de la función decorada.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            return func(result)
        return wrapper
    return decorator

def from_wei(value, unit="ether"):
    """
    Convierte un valor en wei a la unidad especificada.
    Para "ether" divide por 10**18.
    """
    if unit == "ether":
        return value / 10**18
    return value

def to_wei(value, unit="ether"):
    """
    Convierte un valor a wei desde la unidad especificada.
    Para "ether" multiplica por 10**18.
    """
    if unit == "ether":
        return int(value * 10**18)
    return int(value)

def is_address(value):
    """
    Verifica si 'value' es una dirección Ethereum válida.
    Se espera una cadena que comience con "0x" y tenga 42 caracteres.
    """
    if not isinstance(value, str):
        return False
    if not value.startswith("0x") or len(value) != 42:
        return False
    try:
        int(value[2:], 16)
    except ValueError:
        return False
    return True

def to_checksum_address(value):
    """
    Convierte una dirección a su formato checksum (EIP-55).
    Se asume que se recibe en formato hexadecimal.
    """
    if not is_address(value):
        raise ValueError("Dirección Ethereum inválida")
    lower_address = remove_0x_prefix(value).lower()
    address_hash = encode_hex(keccak_256(lower_address.encode("ascii")))
    checksum_address = "0x" + "".join(
        lower_address[i].upper() if int(address_hash[i], 16) >= 8 else lower_address[i]
        for i in range(40)
    )
    return checksum_address

def is_checksum_address(value):
    """
    Verifica si la dirección proporcionada está en formato checksum correcto.
    """
    try:
        return value == to_checksum_address(value)
    except Exception:
        return False

def to_bytes(value, encoding="utf-8"):
    """
    Convierte el valor a bytes:
      - Si ya es bytes, se retorna tal cual.
      - Si es str, se codifica usando el encoding indicado.
      - Si es int, se convierte a bytes (big-endian).
    """
    if isinstance(value, bytes):
        return value
    elif isinstance(value, str):
        return value.encode(encoding)
    elif isinstance(value, int):
        length = (value.bit_length() + 7) // 8 or 1
        return value.to_bytes(length, "big")
    else:
        raise TypeError("Tipo no soportado para to_bytes")

def to_int(value, base=16):
    """
    Convierte el valor a entero:
      - Si es str y comienza con "0x", se asume base 16.
      - Si es bytes, se interpreta en orden big-endian.
    """
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value.startswith("0x"):
            return int(value, 16)
        return int(value, base)
    if isinstance(value, bytes):
        return int.from_bytes(value, "big")
    raise TypeError("Tipo no soportado para to_int")

def to_text(value, encoding="utf-8"):
    """
    Convierte bytes a texto (str) usando el encoding indicado.
    """
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode(encoding)
    raise TypeError("Tipo no soportado para to_text")

def eth_utils_keccak(data):
    """
    Calcula el hash Keccak-256 de los datos.
    """
    return keccak_256(data)
