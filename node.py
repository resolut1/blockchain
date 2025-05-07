from flask import Flask, request, jsonify
from blockchain import Blockchain
from transaction import Transaction
from config import PORT


app = Flask(__name__)
blockchain = Blockchain()


@app.route('/transactions/new', methods=['POST']) # Тригер на пост запрос по api
def new_transaction():
    data = request.get_json()
    
    required = ['from', 'to', 'amount', 'signature']
    if not all(k in data for k in required):
        return '❌ Отсутствуют поля', 400

    tx = Transaction(data['from'], data['to'], data['amount'])
    tx.signature = data['signature']

    try:
        blockchain.create_transaction(tx)
        return jsonify({"message": "✅ Транзакция добавлена в пул"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/mine', methods=['GET'])
def mine():
    data = request.get_json()
    miner_address = data.get('miner')
    miner_private = data.get('private')
    
    if not miner_address or not miner_private:
        return jsonify({"error": "Укажите miner и private в теле запроса"}), 400

    try:
        blockchain.mine_pending_transactions(miner_address, miner_private)
        return jsonify({"message": "✅ Блок намайнен!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce
        })
    return jsonify({
        "length": len(chain_data),
        "chain": chain_data
    }), 200


@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance}), 200


@app.route('/') # корневой каталог
def index():
    return "🔥 Добро пожаловать в мой блокчейн API!"


if __name__ == '__main__':
    app.run(port=PORT)
