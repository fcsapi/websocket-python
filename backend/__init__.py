"""
FCS WebSocket Backend - Python WebSocket Client

Pure Python WebSocket client for real-time market data.

Usage:
    from backend.fcs_client_lib import FCSClient

    client = FCSClient('YOUR_API_KEY')

    @client.on_message
    def handle(data):
        print(data)

    client.connect()
    client.join('BINANCE:BTCUSDT', '1D')
    client.run_forever()
"""

from .fcs_client_lib import FCSClient, create_client

__all__ = ['FCSClient', 'create_client']
__version__ = '1.0.5'
