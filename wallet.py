from ecdsa import SigningKey, SECP256k1
import ecdsa


def generate_keys() -> dict[ecdsa.keys.SigningKey, ecdsa.keys.VerifyingKey]:
    """
    Генерация приватного и публичного ключа.
    """
    private_key = SigningKey.generate(curve=SECP256k1)
    public_key = private_key.get_verifying_key()
    return {
        "private": private_key.to_string().hex(),
        "public": public_key.to_string().hex()
    }


def sign_transaction(private_key_hex: str, transaction_data: str) -> str:
    """
    Подпись транзакции приватным ключом.
    """
    private_key = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    signature = private_key.sign(transaction_data.encode())
    return signature.hex()


def verify_signature(public_key_hex: str, message: str, signature_hex: str) -> bool:
    """
    Проверка подписи.
    """
    from ecdsa import VerifyingKey
    public_key = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
    try:
        return public_key.verify(bytes.fromhex(signature_hex), message.encode())
    except:
        return False


