from wallet import sign_transaction, verify_signature


class Transaction:
    def __init__(self, from_address: str, to_address: str, amount: float):
        self.from_address = from_address   
        self.to_address = to_address       
        self.amount = amount               
        self.signature = None              


    def to_string(self):
        """
        Строковое представление транзакции — то, что подписывается.
        """
        return f"{self.from_address}:{self.to_address}:{self.amount}"


    def sign_message(self, private_key_hex: str):
        """
        Подписывает транзакцию приватным ключом.
        """
        if not self.from_address:
            raise Exception("Нельзя подписать транзакцию без адреса отправителя.")
        
        self.signature = sign_transaction(private_key_hex, self.to_string())


    def is_valid(self):
        """
        Проверяет валидность подпись.
        """
        from wallet import verify_signature
        
        if not self.signature:
            return False
        
        if self.from_address == "SYSTEM":
            from blockchain import SYSTEM_PUBLIC_KEY
            return verify_signature(SYSTEM_PUBLIC_KEY, self.to_string(), self.signature)
        
        return verify_signature(self.from_address, self.to_string(), self.signature)


    def to_dict(self):
        """
        Сериализация в словарь.
        """
        return {
            "from": self.from_address,
            "to": self.to_address,
            "amount": self.amount,
            "signature": self.signature
        }


    @staticmethod
    def from_dict(data):
        """
        Восстановление объекта Transaction из словаря.
        """
        tx = Transaction(
            from_address=data['from'],
            to_address=data['to'],
            amount=data['amount']
        )

        tx.signature = data.get('signature')
        return tx
