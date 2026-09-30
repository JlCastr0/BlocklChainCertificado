# core/block.py
# Classe que representa um bloco individual na blockchain
import hashlib
import time
import json


class Block:
    def __init__(self, index, timestamp, previous_hash, data):
        """
        Inicializa um bloco com os atributos necessários.

        :param index: Índice do bloco na blockchain
        :param timestamp: Timestamp de criação do bloco
        :param previous_hash: Hash do bloco anterior
        :param data: Dados armazenados no bloco (String, CertificateData, etc.)
        """
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = data
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calcula o hash do bloco utilizando SHA-256.
        """
        if hasattr(self.data, 'to_json') and callable(self.data.to_json):
            data_str = self.data.to_json()
        else:
            data_str = str(self.data)

        data_str = f"{self.index}{self.timestamp}{self.previous_hash}{data_str}{self.nonce}"
        return hashlib.sha256(data_str.encode()).hexdigest()

    def proof_of_work(self, difficulty):
        """
        Implementa o algoritmo de Proof-of-Work para validar o bloco.

        :param difficulty: Nível de dificuldade definido para a blockchain
        """
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def __str__(self):
        """
        Retorna a representação textual do bloco.
        """
        if hasattr(self.data, 'to_json') and callable(self.data.to_json):
            data_str = self.data.to_json()
        else:
            data_str = str(self.data)
        return (
            f"Block #{self.index} [previousHash: {self.previous_hash}, "
            f"timestamp: {time.ctime(self.timestamp)}, "
            f"data: {data_str}, hash: {self.hash}]"
        )
