from wallet import generate_keys
from transaction import Transaction
from config import PORT

import argparse
import json
import requests


API_URL = f"http://localhost:{PORT}" # Порт можно изменить в config.py


def create_wallet():
    wallet = generate_keys()
    filename = input("Введите имя файла для сохранения ключей: ")
    with open(f'{filename}.json', 'w') as f:
        json.dump(wallet, f)
    print(f"✅ Кошелёк сохранён в {filename}")
    print("🔐 Private:", wallet["private"])
    print("🔓 Public :", wallet["public"])


def load_wallet(path):
    with open(f'{path}.json', 'r') as f:
        return json.load(f)


def get_balance(public_key):
    resp = requests.get(f"{API_URL}/balance/{public_key}")
    print("💰 Баланс:", resp.json()["balance"])


def send_transaction(wallet_path, to_address, amount):
    wallet = load_wallet(wallet_path)
    tx = Transaction(wallet["public"], to_address, amount)
    tx.sign_message(wallet["private"])

    data = {
        "from": tx.from_address,
        "to": tx.to_address,
        "amount": tx.amount,
        "signature": tx.signature
    }

    resp = requests.post(f"{API_URL}/transactions/new", json=data)
    print("📤 Ответ сервера:", resp.json())


def mine(miner_wallet_path):
    wallet = load_wallet(miner_wallet_path)
    public_key = wallet["public"]
    private_key = wallet["private"]
    
    resp = requests.get(f"{API_URL}/mine", json={
        'miner': public_key,
        'private': private_key
    })
    print("⛏️ Ответ на майнинг:", resp.json())


def main():
    parser = argparse.ArgumentParser(description="CLI для управления кошельком и транзакциями")
    subparsers = parser.add_subparsers(dest="command")

    # Создание кошелька
    subparsers.add_parser("create-wallet", help="Создать новый кошелёк")

    # Проверка баланса
    balance_parser = subparsers.add_parser("balance", help="Показать баланс")
    balance_parser.add_argument("--wallet", required=True, help="Путь к файлу кошелька")

    # Отправка транзакции
    send_parser = subparsers.add_parser("send", help="Отправить транзакцию")
    send_parser.add_argument("--wallet", required=True, help="Файл кошелька")
    send_parser.add_argument("--to", required=True, help="Публичный ключ получателя")
    send_parser.add_argument("--amount", type=float, required=True, help="Сумма")

    # Майнинг
    mine_parser = subparsers.add_parser("mine", help="Намайнить блок")
    mine_parser.add_argument("--wallet", required=True, help="Файл кошелька (для получения награды)")

    args = parser.parse_args()

    if args.command == "create-wallet":
        create_wallet()
    elif args.command == "balance":
        wallet = load_wallet(args.wallet)
        get_balance(wallet["public"])
    elif args.command == "send":
        send_transaction(args.wallet, args.to, args.amount)
    elif args.command == "mine":
        mine(args.wallet)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

