# main/web3_mpy/rlp.py

def int_to_bytes(x):
    """Convierte un entero a su representación en bytes."""
    if x == 0:
        return b'\x00'
    b = b""
    while x:
        b = bytes([x & 0xff]) + b
        x //= 256
    return b



def rlp_encode(item):
    if isinstance(item, int):
        if item == 0:
            return b'\x80'
        elif item < 128:
            return bytes([item])
        else:
            b = int_to_bytes(item)
            return bytes([len(b) + 0x80]) + b
    elif isinstance(item, bytes):
        if len(item) == 1 and item[0] < 128:
            return item
        elif len(item) < 56:
            return bytes([len(item) + 0x80]) + item
        else:
            length_bytes = int_to_bytes(len(item))
            return bytes([len(length_bytes) + 0xb7]) + length_bytes + item
    elif isinstance(item, list):
        output = b''.join(rlp_encode(i) for i in item)
        if len(output) < 56:
            return bytes([len(output) + 0xc0]) + output
        else:
            length_bytes = int_to_bytes(len(output))
            return bytes([len(length_bytes) + 0xf7]) + length_bytes + output
    else:
        raise TypeError("Tipo no válido para RLP encoding")