# main/web3_mpy/eth_utils_helpers.py

def add_0x_prefix(value):
    """
    Agrega el prefijo "0x" a la cadena si aún no lo tiene.
    """
    if not isinstance(value, str):
        raise TypeError("El valor debe ser una cadena")
    if not value.startswith("0x"):
        return "0x" + value
    return value

def remove_0x_prefix(value):
    """
    Remueve el prefijo "0x" de la cadena, si está presente.
    """
    if not isinstance(value, str):
        raise TypeError("El valor debe ser una cadena")
    if value.startswith("0x"):
        return value[2:]
    return value

def decode_hex(hexstr):
    """
    Convierte una cadena hexadecimal (con o sin "0x") a bytes.
    """
    if not isinstance(hexstr, str):
        raise TypeError("El valor debe ser una cadena")
    hexstr = remove_0x_prefix(hexstr)
    return bytes.fromhex(hexstr)

def encode_hex(value):
    """
    Convierte un objeto bytes a su representación hexadecimal (en minúsculas, sin prefijo).
    """
    if not isinstance(value, bytes):
        raise TypeError("El valor debe ser bytes")
    return value.hex()

def hexstr_if_str(func, value):
    """
    Si 'value' es una cadena, aplica la función 'func' sobre ella;
    de lo contrario, retorna 'value' sin cambios.
    """
    if isinstance(value, str):
        return func(value)
    return value

def to_hex(value, hexstr=None, text=None):
    """
    Convierte el valor dado a una cadena hexadecimal.
    
    - Si se provee 'hexstr', se retorna ese valor directamente.
    - Si se provee 'text', se codifica a bytes usando UTF-8 y luego se convierte a hexadecimal.
    - Si el valor es de tipo bytes, se convierte a hexadecimal.
    
    De lo contrario, lanza un error.
    """
    if hexstr is not None:
        return hexstr
    if text is not None:
        return encode_hex(text.encode("utf-8"))
    if isinstance(value, bytes):
        return encode_hex(value)
    raise TypeError("No se pudo convertir el valor a hexadecimal")
