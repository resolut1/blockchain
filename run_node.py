from config import PORT
from node import app

import argparse


def run_node(port):
    print(f"🚀 Запуск блокчейн-ноды на порту {port}...")
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MyCoin Node Runner")
    parser.add_argument('--port', type=int, default=PORT, help=f'Порт для запуска API (по умолчанию {PORT})')
    
    args = parser.parse_args()
    run_node(args.port)

