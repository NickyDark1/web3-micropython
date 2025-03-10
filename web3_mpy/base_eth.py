# main/web3_mpy/base_eth.py

# Definición de un objeto 'empty' para representar un valor vacío (similar a web3._utils.empty.empty)
empty = object()

def assoc(d, key, value):
    """
    Retorna una copia del diccionario 'd' con la clave 'key' actualizada al valor 'value'.
    """
    new_d = d.copy()
    new_d[key] = value
    return new_d

class BaseEth:
    def __init__(self, w3):
        """
        Inicializa BaseEth con la instancia de Web3 'w3'.
        """
        self.w3 = w3
        self._default_account = empty
        self._default_block = "latest"
        self._default_contract_factory = None
        self._gas_price_strategy = None
        self.is_async = False
        # En MicroPython no contamos con eth_account; aquí se podría implementar una funcionalidad mínima de cuenta.
        self.account = None

    def namereg(self):
        raise NotImplementedError("namereg no está implementado en esta versión.")

    def icap_namereg(self):
        raise NotImplementedError("icap_namereg no está implementado en esta versión.")

    @property
    def default_block(self):
        return self._default_block

    @default_block.setter
    def default_block(self, value):
        self._default_block = value

    @property
    def default_account(self):
        return self._default_account

    @default_account.setter
    def default_account(self, account):
        self._default_account = account

    def send_transaction_munger(self, transaction):
        """
        Si en la transacción no se especifica 'from' y se tiene definido un default_account,
        se asocia el 'from' al default_account.
        """
        if "from" not in transaction and self.default_account != empty:
            transaction = assoc(transaction, "from", self.default_account)
        return (transaction,)

    def generate_gas_price(self, transaction_params=None):
        """
        Retorna el gas price generado a partir de una estrategia si está definida.
        """
        if self._gas_price_strategy:
            return self._gas_price_strategy(self.w3, transaction_params)
        return None

    def set_gas_price_strategy(self, gas_price_strategy):
        """
        Establece la estrategia para calcular gas price.
        """
        self._gas_price_strategy = gas_price_strategy

    def _eth_call_and_estimate_gas_munger(self, transaction, block_identifier=None, state_override=None):
        """
        Prepara (munga) la transacción para llamadas o estimación de gas:
         - Agrega el campo 'from' si no existe.
         - Establece el block_identifier por defecto.
         - Incluye state_override si se proporciona.
        """
        if "from" not in transaction and self.default_account != empty:
            transaction = assoc(transaction, "from", self.default_account)
        if block_identifier is None:
            block_identifier = self.default_block
        if state_override is None:
            return (transaction, block_identifier)
        else:
            return (transaction, block_identifier, state_override)

    def estimate_gas_munger(self, transaction, block_identifier=None, state_override=None):
        return self._eth_call_and_estimate_gas_munger(transaction, block_identifier, state_override)

    def get_block_munger(self, block_identifier, full_transactions=False):
        return (block_identifier, full_transactions)

    def block_id_munger(self, account, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.default_block
        return (account, block_identifier)

    def get_storage_at_munger(self, account, position, block_identifier=None):
        if block_identifier is None:
            block_identifier = self.default_block
        return (account, position, block_identifier)

    def call_munger(self, transaction, block_identifier=None, state_override=None):
        return self._eth_call_and_estimate_gas_munger(transaction, block_identifier, state_override)

    def create_access_list_munger(self, transaction, block_identifier=None):
        if "from" not in transaction and self.default_account != empty:
            transaction = assoc(transaction, "from", self.default_account)
        if block_identifier is None:
            block_identifier = self.default_block
        return (transaction, block_identifier)

    def sign_munger(self, account, data=None, hexstr=None, text=None):
        """
        Prepara la firma de un mensaje. Utiliza 'w3.to_hex' para convertir
        los datos a un mensaje hexadecimal. Se prioriza 'data' sobre 'hexstr' o 'text'.
        """
        if data is not None:
            message_hex = self.w3.to_hex(data)
        elif hexstr is not None:
            message_hex = hexstr
        elif text is not None:
            message_hex = text  # Se podría aplicar un encoding aquí si es necesario.
        else:
            message_hex = None
        return (account, message_hex)

    def filter_munger(self, filter_params=None, filter_id=None):
        """
        Prepara los parámetros para la creación de un filtro.
        Se debe proporcionar o bien filter_params o filter_id, pero no ambos.
        """
        if filter_id and filter_params:
            raise Exception("Invocación ambigua: proporcionar o filter_params o filter_id, no ambos.")
        if isinstance(filter_params, dict):
            return [filter_params]
        elif isinstance(filter_params, str):
            if filter_params in {"latest", "pending"}:
                return [filter_params]
            else:
                raise Exception("El API de filtros solo acepta 'pending' o 'latest' para filtros tipo string.")
        elif filter_id and not filter_params:
            return [filter_id]
        else:
            raise Exception("Debe proporcionarse filter_params (como string o diccionario) o filter_id.")
