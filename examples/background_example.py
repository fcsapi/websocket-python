"""
FCS Background Thread Example

Shows how to run WebSocket in background thread (non-blocking).
This allows your main code to continue running while receiving price updates.

Run: python background_example.py
"""

import sys
import os
import time

# Add parent directory to path for import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fcs_client_lib import FCSClient

# Create client with demo API key
client = FCSClient('fcs_socket_demo')

# Store latest prices
latest_prices = {}


@client.on_connected
def on_connected():
    print('[WebSocket] Connected!')
    client.join('BINANCE:BTCUSDT', '1D')
    client.join('BINANCE:ETHUSDT', '1D')


@client.on_message
def on_message(data):
    if data.get('type') == 'price':
        symbol = data.get('symbol')
        price = data['prices'].get('c')
        latest_prices[symbol] = price


if __name__ == '__main__':
    print('FCS WebSocket - Background Thread Example')
    print('=' * 50)

    # Connect and run in background (non-blocking)
    client.connect()
    client.run_forever(blocking=False)

    print('[Main] WebSocket running in background thread')
    print('[Main] Main thread continues to run...\n')

    # Wait for connection
    time.sleep(3)

    # Main loop - do your work here while prices update in background
    try:
        for i in range(20):
            print(f'[Main] Tick {i + 1}/20 - Latest prices: {latest_prices}')
            time.sleep(3)

    except KeyboardInterrupt:
        pass

    print('\n[Main] Disconnecting...')
    client.disconnect()
    print('[Main] Done!')
