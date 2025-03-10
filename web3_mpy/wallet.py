# main/web3_mpy/wallet.py

import os
import ubinascii
from web3_mpy.keccak import keccak_256  # Asegúrate de que keccak.py esté en el mismo directorio

import gc

def clear_memory():
    gc.collect()

# Parámetros de la curva secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def modinv(a, p):
    """Calcula el inverso modular de a mod p usando Fermat."""
    return pow(a, p - 2, p)

def ecc_double(point):
    (x, y) = point
    s = (3 * x * x) * modinv(2 * y, p) % p
    x_r = (s * s - 2 * x) % p
    y_r = (s * (x - x_r) - y) % p
    return (x_r, y_r)

def ecc_add(point1, point2):
    if point1 is None:
        return point2
    if point2 is None:
        return point1
    (x1, y1) = point1
    (x2, y2) = point2
    if x1 == x2 and y1 == (-y2 % p):
        return None
    if point1 == point2:
        return ecc_double(point1)
    s = (y2 - y1) * modinv(x2 - x1, p) % p
    x_r = (s * s - x1 - x2) % p
    y_r = (s * (x1 - x_r) - y1) % p
    return (x_r, y_r)

def scalar_mult(k, point):
    result = None
    addend = point
    while k:
        if k & 1:
            result = ecc_add(result, addend)
        addend = ecc_double(addend)
        k >>= 1
    return result

'''
def pad_left(s, width):
    """Rellena la cadena s con ceros a la izquierda hasta alcanzar el ancho width."""
    return s.rjust(width, "0")
'''
def pad_left(s, width):
    while len(s) < width:
        s = "0" + s
    return s

class Wallet:
    """Clase para generar claves privadas, públicas y la dirección Ethereum."""
    
    @staticmethod
    def generate_keypair():
        # Generar una clave privada aleatoria (32 bytes) y asegurar que sea válida
        private_key = int.from_bytes(os.urandom(32), 'big') % n
        if private_key == 0:
            private_key = 1
        # Calcular la clave pública (punto en la curva secp256k1)
        public_point = scalar_mult(private_key, G)
        # Formatear la clave privada a hexadecimal (64 dígitos)
        private_key_hex = pad_left(hex(private_key)[2:].rstrip("L"), 64)
        # Convertir las coordenadas de la clave pública a bytes (32 bytes cada una)
        x_bytes = public_point[0].to_bytes(32, 'big')
        y_bytes = public_point[1].to_bytes(32, 'big')
        public_key_bytes = x_bytes + y_bytes
        # Calcular el hash Keccak-256 de la clave pública
        hash_bytes = keccak_256(public_key_bytes)
        # Derivar la dirección Ethereum: se toman los últimos 20 bytes del hash
        address_bytes = hash_bytes[-20:]
        address_hex = ubinascii.hexlify(address_bytes).decode()
        clear_memory()
        return "0x" + private_key_hex, "0x" + address_hex
'''
if __name__ == '__main__':
    priv, addr = Wallet.generate_keypair()
    print("Clave privada:", priv)
    print("Dirección Ethereum:", addr)
'''