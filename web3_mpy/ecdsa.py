# main/web3_mpy/ecdsa.py
#
# Implementación minimalista ECDSA sobre secp256k1 en MicroPython.
# - Sin recursión profunda (iterativa) en la multiplicación.
# - Fuerza s <= n/2 (firma canónica).
# - Retorna (r, s, recid), donde recid ∈ {0,1}.
# - Usa k aleatorio con os.urandom(32) en vez de RFC6979.

import os

# Parámetros secp256k1
P = 2**256 - 2**32 - 977
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
A = 0
B = 7
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

def bytes_to_int(b):
    num = 0
    for byte in b:
        num = (num << 8) | byte
    return num

def inv(a, m):
    """Inverso modular de 'a' mod 'm' (Euclides extendido)."""
    if a == 0:
        return 0
    lm, hm = 1, 0
    low, high = a % m, m
    while low > 1:
        r = high // low
        nm = hm - lm*r
        new = high - low*r
        lm, low, hm, high = nm, new, lm, low
    return lm % m

def to_jacobian(p):
    # (x, y) -> (x, y, 1)
    return (p[0], p[1], 1)

def from_jacobian(p):
    # (x, y, z) -> (x/z^2, y/z^3)
    if p[2] == 0:
        return (0, 0)
    z_inv = inv(p[2], P)
    x = (p[0] * (z_inv*z_inv)) % P
    y = (p[1] * (z_inv*z_inv*z_inv)) % P
    return (x, y)

def jacobian_double(p):
    if not p[1]:
        return (0, 0, 0)
    ysq = (p[1]*p[1]) % P
    S = (4 * p[0] * ysq) % P
    M = (3*p[0]*p[0] + A*(p[2]**4)) % P
    nx = (M*M - 2*S) % P
    ny = (M*(S - nx) - 8*ysq*ysq) % P
    nz = (2*p[1]*p[2]) % P
    return (nx, ny, nz)

def jacobian_add(p, q):
    if p[1] == 0:
        return q
    if q[1] == 0:
        return p
    U1 = (p[0]*(q[2]**2)) % P
    U2 = (q[0]*(p[2]**2)) % P
    S1 = (p[1]*(q[2]**3)) % P
    S2 = (q[1]*(p[2]**3)) % P
    if U1 == U2:
        if S1 != S2:
            return (0, 0, 1)  # infinito
        return jacobian_double(p)
    H = (U2 - U1) % P
    R = (S2 - S1) % P
    H2 = (H*H) % P
    H3 = (H*H2) % P
    U1H2 = (U1*H2) % P
    nx = (R*R - H3 - 2*U1H2) % P
    ny = (R*(U1H2 - nx) - S1*H3) % P
    nz = (H*p[2]*q[2]) % P
    return (nx, ny, nz)

def jacobian_multiply(jac_point, scalar):
    """Multiplicación 'double-and-add' iterativa en jacobiano (sin recursión)."""
    if jac_point[1] == 0 or scalar == 0:
        return (0, 0, 1)
    scalar %= N
    result = (0, 0, 1)
    addend = jac_point
    while scalar > 0:
        if (scalar & 1) == 1:
            result = jacobian_add(result, addend)
        addend = jacobian_double(addend)
        scalar >>= 1
    return result

def multiply(point, scalar):
    return from_jacobian(jacobian_multiply(to_jacobian(point), scalar))

def generate_k():
    """Genera un 'k' aleatorio en [1..N-1]."""
    while True:
        rand32 = os.urandom(32)
        k = bytes_to_int(rand32) % N
        if k != 0:
            return k

def private_key_to_public_key(priv_bytes):
    """
    Calcula la pubkey (x,y) = priv*G
    """
    priv_int = bytes_to_int(priv_bytes)
    return multiply(G, priv_int)

def ecdsa_sign(msg_hash_32, priv_bytes):
    """
    Firma ECDSA de 'msg_hash_32' (bytes de 32).
      - Fuerza s <= N/2 (canónica).
      - Retorna (r, s, recid) en lugar de (v, r, s).
        recid = 0 ó 1 indica la paridad de la coordenada y,
        con la corrección si s fue invertido.

    Nota: 'sign_tx' en tu 'tx.py' asume la salida (r, s, recid).
    """
    z = bytes_to_int(msg_hash_32)
    priv_int = bytes_to_int(priv_bytes)

    while True:
        k = generate_k()
        kx, ky = multiply(G, k)
        r = kx % N
        if r == 0:
            continue

        inv_k = inv(k, N)
        s = (inv_k * (z + r * priv_int)) % N
        if s == 0:
            continue

        # Forzar s canónico (s <= N/2)
        is_high = (s * 2) > N
        if is_high:
            s = N - s

        recid = ky & 1
        if is_high:
            recid ^= 1

        # en lugar de 'v = 27 + recid', retornamos (r, s, recid)
        return (r, s, recid)

def ecdsa_recover(msg_hash_32, v, r, s):
    """
    Recupera la pubkey (x,y) dados (v, r, s), con v ∈ {27,28}.
    """
    if v not in (27, 28):
        raise ValueError("v inválido (27 u 28)")
    if r <= 0 or r >= N:
        raise ValueError("r fuera de rango")
    if s <= 0 or s >= N:
        raise ValueError("s fuera de rango")

    x = r
    alpha = (x*x*x + A*x + B) % P
    beta = pow(alpha, (P+1)//4, P)  # sqrt mod P

    even_y = (beta % 2) == 0
    is_v_odd = (v % 2) == 1
    if even_y ^ is_v_odd:
        y = (P - beta) % P
    else:
        y = beta

    if (y*y - alpha) % P != 0:
        raise ValueError("El punto no yace en la curva secp256k1")

    z = bytes_to_int(msg_hash_32)
    Rj = jacobian_multiply((x,y,1), s)
    Gj = jacobian_multiply((Gx,Gy,1), (N - z) % N)
    Qj = jacobian_add(Rj, Gj)
    r_inv = inv(r, N)
    Qj = jacobian_multiply(Qj, r_inv)
    return from_jacobian(Qj)
