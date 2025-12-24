"""
FCS Simple Example - Quick Start

Minimal example to get started with FCS WebSocket.
Just prints price updates for Bitcoin.

Run: python simple_example.py
"""

import sys
import os

# Add parent directory to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fcs_client_lib import FCSClient

# Create client with demo API key
client = FCSClient('fcs_socket_demo')


@client.on_connected
def on_connected():
    print('Connected to FCS WebSocket!')
    print('Subscribing to BTCUSDT...\n')
    client.join('BINANCE:BTCUSDT', '1D')


@client.on_message
def on_message(data):
    if data.get('type') == 'price':
        symbol = data.get('symbol')
        price = data['prices'].get('c')  # Close price
        print(f'{symbol}: ${price}')


if __name__ == '__main__':
    print('FCS WebSocket - Simple Example')
    print('Press Ctrl+C to stop\n')

    try:
        client.connect()
        client.run_forever()
    except KeyboardInterrupt:
        print('\nDisconnecting...')
        client.disconnect()
