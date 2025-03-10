# main/web3_mpy/keccak.py
#
# Implementación simplificada de Keccak-256 para MicroPython.

def _rotl64(x, n):
    n = n % 64
    return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF

def _keccak_f(state):
    RC = [
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
        0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
        0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
        0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
        0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
        0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008
    ]
    r_values = [
        [  0,  36,   3, 105, 210 ],
        [  1, 300,  10,  45,  66 ],
        [190,   6, 171,  15, 253 ],
        [ 28,  55, 153,  21, 120 ],
        [ 91, 276, 231, 136,  78 ]
    ]
    A = [[0]*5 for _ in range(5)]
    for y in range(5):
        for x in range(5):
            A[x][y] = state[x + 5*y]
    for rnd in range(24):
        # Theta
        C = [A[x][0]^A[x][1]^A[x][2]^A[x][3]^A[x][4] for x in range(5)]
        D = [(C[(x-1)%5]^_rotl64(C[(x+1)%5],1)) for x in range(5)]
        for x in range(5):
            for y in range(5):
                A[x][y] ^= D[x]
        # Rho & Pi
        B = [[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                B[y][(2*x+3*y)%5] = _rotl64(A[x][y], r_values[x][y])
        # Chi
        for x in range(5):
            for y in range(5):
                A[x][y] = B[x][y] ^ ((~B[(x+1)%5][y]) & B[(x+2)%5][y])
        # Iota
        A[0][0] ^= RC[rnd]
    new_state = []
    for y in range(5):
        for x in range(5):
            new_state.append(A[x][y])
    return new_state

def keccak_256(data):
    """
    Calcula Keccak-256 de 'data' (tipo bytes).
    Retorna 32 bytes de hash.
    """
    rate = 136
    output_length = 32
    state = [0]*25

    data = bytearray(data)
    data.append(0x01)
    pad_len = (-len(data) - 1) % rate
    data.extend(b'\x00' * pad_len)
    data.append(0x80)

    for offset in range(0, len(data), rate):
        block = data[offset:offset+rate]
        for i in range(rate//8):
            word = 0
            for b in range(8):
                word |= block[i*8 + b] << (8*b)
            state[i] ^= word
        state = _keccak_f(state)

    out = b''
    while len(out) < output_length:
        for i in range(rate//8):
            w = state[i]
            tmp = []
            for b in range(8):
                tmp.append((w >> (8*b)) & 0xFF)
            out += bytes(tmp)
            if len(out) >= output_length:
                break
        if len(out) < output_length:
            state = _keccak_f(state)
    return out[:32]
