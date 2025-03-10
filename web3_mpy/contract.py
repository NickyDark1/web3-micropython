# main/web3_mpy/contract.py

'''
# nota: Sin decodificacion dinamica
from web3_mpy.keccak import keccak_256

import gc

def clear_memory():
    gc.collect()

def get_function_selector(abi_item):
    """
    Dado un elemento del ABI para una función, retorna el selector:
    los primeros 4 bytes del hash Keccak-256 de la firma de la función.
    Ejemplo: para transfer(address,uint256) retorna b'\xa9\x05\x9c\xbb'
    """
    if abi_item.get("type") != "function":
        return None
    inputs = abi_item.get("inputs", [])
    types = [inp["type"] for inp in inputs]
    signature_str = "{}({})".format(abi_item["name"], ",".join(types))
    hash_bytes = keccak_256(signature_str.encode("utf-8"))
    return bytes.fromhex(hash_bytes[:4].hex())

class Contract:
    def __init__(self, address, abi, web3):
        """
        Inicializa el contrato.
        :param address: Dirección del contrato (string con "0x...").
        :param abi: Lista con el ABI del contrato.
        :param web3: Instancia de Web3.
        """
        self.address = address
        self.abi = abi
        self.web3 = web3
        self.functions = ContractFunctions(abi, web3, address)

class ContractFunctions:
    def __init__(self, abi, web3, address):
        self.abi = abi
        self.web3 = web3
        self.address = address

    def __getattr__(self, name):
        """
        Permite acceder a las funciones del contrato como atributos.
        Ejemplo: contract.functions.getPool(*args)
        Busca en el ABI un elemento con "name" igual al nombre solicitado.
        """
        for item in self.abi:
            if item.get("type") == "function" and item.get("name") == name:
                # Devuelve una función lambda que crea una instancia de ContractFunction
                return lambda *args: ContractFunction(item, args, self.web3, self.address)
        raise AttributeError("Function {} not found in contract ABI.".format(name))


class ContractFunction:
    def __init__(self, abi_item, args, web3, address):
        self.abi_item = abi_item
        self.args = args
        self.web3 = web3
        self.address = address
        self.data = self.encode_call()

    def encode_call(self):
        """
        Codifica la llamada a la función:
         - Calcula el selector (primeros 4 bytes del hash keccak de la firma).
         - Codifica los argumentos:
             * Si es int: se codifica en 32 bytes (big-endian).
             * Si es una dirección (string con "0x" y longitud 42): se decodifica a 20 bytes
               y se rellena a la izquierda con 12 bytes de cero para alcanzar 32 bytes.
             * Otros tipos no son soportados en esta implementación mínima.
        Retorna la concatenación del selector y la codificación de argumentos.
        """
        selector = get_function_selector(self.abi_item)
        encoded_args = b""
        for arg in self.args:
            if isinstance(arg, int):
                encoded_args += arg.to_bytes(32, "big")
            elif isinstance(arg, str) and arg.startswith("0x") and len(arg) == 42:
                # Se asume que es una dirección Ethereum
                addr_bytes = bytes.fromhex(arg[2:])
                # Se rellena a la izquierda con 12 bytes de 0 para obtener 32 bytes
                encoded_args += (b'\x00' * 12) + addr_bytes
            else:
                raise ValueError("Unsupported argument type: only integers and addresses are supported in this implementation.")
        return selector + encoded_args
    def call(self):
        """
        Realiza la llamada a la función mediante JSON‑RPC usando el método "eth_call".
        Construye el payload con la dirección del contrato y los datos codificados.
        Retorna el resultado devuelto por el nodo (generalmente en hexadecimal).
        """
        payload = {
            "to": self.address,
            "data": "0x" + self.data.hex()
        }
        response = self.web3.provider.make_request("eth_call", [payload, "latest"])
        return response.get("result")
'''

# main/web3_mpy/contract.py
# nota: Con decodificacion dinamica

from web3_mpy.keccak import keccak_256
import gc
import re

def clear_memory():
    gc.collect()

def get_function_selector(abi_item):
    """
    Dado un elemento del ABI para una función, retorna el selector:
    los primeros 4 bytes del hash Keccak-256 de la firma de la función.
    Ejemplo: para transfer(address,uint256) retorna b'\xa9\x05\x9c\xbb'
    """
    if abi_item.get("type") != "function":
        return None
    inputs = abi_item.get("inputs", [])
    types = [inp["type"] for inp in inputs]
    signature_str = "{}({})".format(abi_item["name"], ",".join(types))
    hash_bytes = keccak_256(signature_str.encode("utf-8"))
    return bytes.fromhex(hash_bytes[:4].hex())

def is_dynamic_type(typ):
    """
    Retorna True si el tipo es dinámico (string, bytes o array dinámico).
    """
    if typ == "string" or typ == "bytes":
        return True
    if typ.endswith("[]"):
        return True
    return False

def is_array_type(typ):
    """
    Retorna True si el tipo es un array (dinámico o de tamaño fijo).
    """
    return typ.endswith("]")

def get_array_info(typ):
    """
    Extrae el tipo base y la longitud (None para arrays dinámicos) de un tipo de array.
    Ejemplos:
      "uint256[3]" -> ("uint256", 3)
      "uint256[]"  -> ("uint256", None)
    """
    m = re.match(r"(.*)\[(.*?)\]$", typ)
    if m:
        base = m.group(1)
        length_str = m.group(2)
        if length_str == "":
            return base, None
        else:
            return base, int(length_str)
    return None, None

def decode_static(typ, data):
    """
    Decodifica tipos estáticos contenidos en 32 bytes.
    Soporta: uint, int, address, bool y bytes fijos (ej. bytes32).
    """
    if typ.startswith("uint"):
        return int.from_bytes(data, "big")
    elif typ.startswith("int"):
        unsigned_val = int.from_bytes(data, "big")
        # Si el entero es negativo, se ajusta
        if unsigned_val >= (1 << 255):
            return unsigned_val - (1 << 256)
        return unsigned_val
    elif typ == "address":
        return "0x" + data[-20:].hex()
    elif typ == "bool":
        return bool(int.from_bytes(data, "big"))
    elif typ.startswith("bytes") and typ != "bytes":
        # bytes fijos: ej. bytes4, bytes32; se toman los primeros N bytes
        size = int(typ[5:])
        return data[:size]
    else:
        raise ValueError("Tipo estático no soportado: " + typ)


def decode_dynamic(typ, full_data, offset):
    """
    Decodifica tipos dinámicos a partir de full_data comenzando en offset.
    Soporta:
      - string: se decodifica asumiendo codificación UTF-8.
      - bytes: retorna los bytes.
      - Arrays dinámicos con elementos estáticos.
    """
    if typ == "string":
        length = int.from_bytes(full_data[offset:offset+32], "big")
        data = full_data[offset+32: offset+32+length]
        return data.decode("utf-8")
    elif typ == "bytes":
        length = int.from_bytes(full_data[offset:offset+32], "big")
        data = full_data[offset+32: offset+32+length]
        return data
    elif is_array_type(typ):
        base, fixed_length = get_array_info(typ)
        # Para arrays dinámicos, el primer slot es la longitud
        length = int.from_bytes(full_data[offset:offset+32], "big")
        arr = []
        # En este ejemplo se asume que los elementos son de tipo estático.
        element_size = 32
        for i in range(length):
            start = offset + 32 + i * element_size
            element_data = full_data[start:start+element_size]
            arr.append(decode_static(base, element_data))
        return arr
    else:
        raise ValueError("Tipo dinámico no soportado: " + typ)

class Contract:
    def __init__(self, address, abi, web3):
        """
        Inicializa el contrato.
        :param address: Dirección del contrato (string con "0x...").
        :param abi: Lista con el ABI del contrato.
        :param web3: Instancia de Web3.
        """
        self.address = address
        self.abi = abi
        self.web3 = web3
        self.functions = ContractFunctions(abi, web3, address)

class ContractFunctions:
    def __init__(self, abi, web3, address):
        self.abi = abi
        self.web3 = web3
        self.address = address

    def __getattr__(self, name):
        """
        Permite acceder a las funciones del contrato como atributos.
        Ejemplo: contract.functions.getPool(*args)
        Busca en el ABI un elemento con "name" igual al solicitado.
        """
        for item in self.abi:
            if item.get("type") == "function" and item.get("name") == name:
                # Retorna una lambda que crea una instancia de ContractFunction
                return lambda *args: ContractFunction(item, args, self.web3, self.address)
        raise AttributeError("Función {} no encontrada en el ABI del contrato.".format(name))

class ContractFunction:
    def __init__(self, abi_item, args, web3, address):
        self.abi_item = abi_item
        self.args = args
        self.web3 = web3
        self.address = address
        self.data = self.encode_call()

    def encode_call(self):
        """
        Codifica la llamada a la función:
          - Calcula el selector (primeros 4 bytes del hash keccak de la firma).
          - Codifica los argumentos (en esta versión se soportan enteros y direcciones).
        Retorna la concatenación del selector y la codificación de argumentos.
        """
        selector = get_function_selector(self.abi_item)
        encoded_args = b""
        for arg in self.args:
            if isinstance(arg, int):
                encoded_args += arg.to_bytes(32, "big")
            elif isinstance(arg, str) and arg.startswith("0x") and len(arg) == 42:
                # Se asume que es una dirección Ethereum
                addr_bytes = bytes.fromhex(arg[2:])
                # Se rellena a la izquierda con 12 bytes de 0 para completar 32 bytes
                encoded_args += (b'\x00' * 12) + addr_bytes
            else:
                raise ValueError("Tipo de argumento no soportado: solo enteros y direcciones en esta implementación.")
        return selector + encoded_args

    def decode_output(self, raw_result):
        """
        Decodifica la respuesta del nodo según la estructura de salida definida en el ABI.
        Separa la parte head (32 bytes por cada salida) y, para cada salida:
          - Si es un tipo dinámico, se utiliza el offset indicado para decodificar.
          - Si es un tipo estático, se decodifica directamente el slot.
        """
        outputs = self.abi_item.get("outputs", [])
        if not outputs:
            return None

        # Convertir el resultado a bytes, removiendo el prefijo "0x" si existe.
        full_data = bytes.fromhex(raw_result[2:]) if raw_result.startswith("0x") else bytes.fromhex(raw_result)
        values = []
        # Se asume que la parte head tiene 32 bytes por cada salida.
        head_slots = [full_data[i*32:(i+1)*32] for i in range(len(outputs))]
        
        for i, output in enumerate(outputs):
            typ = output["type"]
            if is_dynamic_type(typ):
                # Para tipos dinámicos, el slot contiene el offset relativo al inicio de full_data.
                offset = int.from_bytes(head_slots[i], "big")
                value = decode_dynamic(typ, full_data, offset)
            else:
                value = decode_static(typ, head_slots[i])
            values.append(value)
        if len(values) == 1:
            return values[0]
        return tuple(values)

    def call(self):
        """
        Realiza la llamada a la función mediante JSON‑RPC usando el método "eth_call".
        Construye el payload con la dirección del contrato y los datos codificados.
        Retorna la respuesta decodificada según el ABI.
        """
        payload = {
            "to": self.address,
            "data": "0x" + self.data.hex()
        }
        response = self.web3.provider.make_request("eth_call", [payload, "latest"])
        raw_result = response.get("result")
        return self.decode_output(raw_result)
