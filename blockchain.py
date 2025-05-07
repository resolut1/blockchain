from transaction import Transaction

import hashlib
import time
import os
import json


SYSTEM_PUBLIC_KEY = '79e1605eb9062883e7964e521fa98909eaa87fbbe4d25fa2e2cd216dc9fb5bf72970f153afc235c4caffc6f55be66799066131c0ae9dd72b7f7eacbd54aa34a6'


class Block:
    def __init__(self, index: int, previous_hash: str, timestamp: float, transactions: list[Transaction], nonce=0, miner= None, signature= None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
        self.miner = miner
        self.signature = signature


    def calculate_hash(self):
        '''
        Сериализация блоков из объекта в строчное представление и хэш
        '''
        tx_data = "".join([tx.to_string() + (tx.signature or "") for tx in self.transactions]) \
            if isinstance(self.transactions, list) else str(self.transactions)
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{tx_data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()


    def mine_block(self, difficulty):
        print("🔨 Майнится блок...")
        while not self.hash.startswith("0" * difficulty):
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"✅ Блок намайнен: {self.hash}")
        
        
    def sign_block(self, miner_privat_key: str):
        from wallet import sign_transaction
        self.signature = sign_transaction(miner_privat_key, self.hash)
        
        
    def is_signature_valid(self):
        '''
        Проверка подписи на валидность
        '''
        if not self.miner or not self.signature:
            return False
        from wallet import verify_signature
        return verify_signature(self.miner, self.hash, self.signature)


class Blockchain:
    def __init__(self):
        self.difficulty = 4
        self.pending_transactions: list[Transaction] = []
        self.mining_reward = 100
        
        with open("system_wallet.json", "r") as f:
            system_wallet = json.load(f)
            self.system_private_key = system_wallet["private"]
            self.system_public_key = system_wallet["public"]
        
        if os.path.exists("chains/chain.json"):
            self.chain = self.load_chain()
            print("📂 Цепочка загружена из файла")
            
            if not self.is_chain_valid():
                print("❌ Цепочка недействительна! Заменяем на новую.")
                self.chain = [self.create_genesis_block()]
        else:
            self.chain = [self.create_genesis_block()]
            print("🧱 Создан генезис-блок")


    def create_genesis_block(self):
        return Block(0, "0", time.time(), [])


    def get_latest_block(self):
        return self.chain[-1]


    def mine_pending_transactions(self, miner_address, miner_private_key):
        '''
        Майнинг
        '''
        print("🔍 Проверка транзакций перед майнингом...")
        for tx in self.pending_transactions:
            if not tx.is_valid():
                raise Exception("Обнаружена недействительная транзакция. Майнинг прерван.")

        reward_tx = Transaction("SYSTEM", miner_address, self.mining_reward)
        reward_tx.sign_message(self.system_private_key)
        
        transactions_to_mine = self.pending_transactions + [reward_tx] #Добавляем транзакцию с наградой майнера в пул

        block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            timestamp=time.time(),
            transactions=transactions_to_mine
        )
        block.mine_block(self.difficulty)

        block.miner = miner_address 
        block.sign_block(miner_private_key) # Подписываем блок приватным ключем майнера

        self.chain.append(block)
        self.save_chain() # Сохраняем цепочку

        print("💰 Блок намайнен, награда отправлена майнеру.")

        self.pending_transactions = [] # Очищаем пул транзакций



    def create_transaction(self, transaction: Transaction):
        if not transaction.from_address or not transaction.to_address:
            raise Exception("Транзакция должна содержать адреса отправителя и получателя.")
    
        if not transaction.is_valid():
            raise Exception("Невозможно добавить недействительную транзакцию.")

        if transaction.from_address != "SYSTEM":
            sender_balance = self.get_balance(transaction.from_address)
            if sender_balance < transaction.amount:
                raise Exception("Недостаточно средств для выполнения транзакции.")

        self.pending_transactions.append(transaction)



    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.from_address == address:
                    balance -= tx.amount
                if tx.to_address == address:
                    balance += tx.amount
        return balance


    def is_chain_valid(self):
        '''
        Проверка цепочки на валидность
        '''
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if not current.is_signature_valid():
                print(f"❌ Блок {i} содержит недействительную подпись майнера")
                return False
            
            if current.hash != current.calculate_hash():
                print("❌ Нарушен хеш блока")
                return False
            if current.previous_hash != prev.hash:
                print("❌ Предыдущий хеш не совпадает")
                return False
            for tx in current.transactions:
                if not tx.is_valid():
                    print("❌ Обнаружена фальшивая транзакция")
                    return False
        return True


    def save_chain(self, filename="chains/chain.json"):
        '''
        Сохранение цепочки в файл
        '''
        chain_data = []
        for block in self.chain:
            chain_data.append({
                'index': block.index,
                'previous_hash': block.previous_hash,
                'timestamp': block.timestamp,
                'transactions': [tx.to_dict() for tx in block.transactions],
                'nonce': block.nonce,
                'hash': block.hash,
                'miner': block.miner,
                'signature': block.signature
            })
        with open(filename, 'w') as f:
            json.dump(chain_data, f, indent=4)
            
    
    def load_chain(self, filename="chains/chain.json"):
        '''
        Загрузка цепочки из файла
        '''
        from transaction import Transaction
        with open(filename, "r") as f:
            data = json.load(f)
            chain = []
            for b in data:
                txs = [Transaction.from_dict(tx) for tx in b["transactions"]]
                block = Block(
                    index=b["index"],
                    previous_hash=b["previous_hash"],
                    timestamp=b["timestamp"],
                    transactions=txs,
                    nonce=b["nonce"],
                    miner=b["miner"],
                    signature=b["signature"]
                )
                block.hash = b["hash"]
                chain.append(block)
            return chain
