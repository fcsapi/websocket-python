# FCS WebSocket Python

Real-time WebSocket client library for **Forex**, **Cryptocurrency**, and **Stock** market data from [FCS API](https://fcsapi.com).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/fcsapi-websocket.svg)](https://pypi.org/project/fcsapi-websocket/)

## Features

- **Real-time WebSocket** - Live price updates via WebSocket connection
- **Multi-Market Support** - Forex, Crypto, and Stock data
- **Auto-Reconnect** - Handles connection drops automatically
- **Simple API** - Easy to use with decorators

## Installation

```bash
pip install fcsapi-websocket
```

## Examples

To download example files, clone the repository:

```bash
git clone https://github.com/fcsapi/websocket-python
cd websocket-python/examples
python simple_example.py
```

## Demo API Key

Use demo API key for testing: `fcs_socket_demo`

---

## Quick Start

```python
from fcs_client_lib import FCSClient

client = FCSClient('YOUR_API_KEY')

@client.on_message
def handle_message(data):
    if data.get('type') == 'price':
        print(data)

client.connect()
client.join('BINANCE:BTCUSDT', '1D')
client.run_forever()
```

---

## Usage Examples

### Example 1: Simple Crypto Price

```python
from fcs_client_lib import FCSClient

client = FCSClient('fcs_socket_demo')

@client.on_message
def on_message(data):
    if data.get('type') == 'price':
        symbol = data.get('symbol')
        price = data['prices'].get('c')  # Close price
        print(f'{symbol}: ${price}')

client.connect()
client.join('BINANCE:BTCUSDT', '1D')
client.run_forever()
```

### Example 2: Multiple Forex Pairs with Spread

```python
from fcs_client_lib import FCSClient

client = FCSClient('fcs_socket_demo')

@client.on_connected
def on_connected():
    print('Connected! Subscribing to forex pairs...')
    client.join('FX:EURUSD', '1D')
    client.join('FX:GBPUSD', '1D')
    client.join('FX:USDJPY', '1D')

@client.on_message
def on_message(data):
    if data.get('type') == 'price':
        p = data['prices']
        symbol = data.get('symbol')
        ask = p.get('a')
        bid = p.get('b')
        spread = round((float(ask) - float(bid)) * 10000, 1) if ask and bid else '--'
        print(f'{symbol}: Ask={ask} Bid={bid} Spread={spread} pips')

client.connect()
client.run_forever()
```

### Example 3: Background Thread (Non-blocking)

```python
from fcs_client_lib import FCSClient
import time

client = FCSClient('fcs_socket_demo')

@client.on_message
def on_message(data):
    if data.get('type') == 'price':
        print(f"Price update: {data.get('symbol')}")

# Connect and run in background thread
client.connect()
client.run_forever(blocking=False)

# Subscribe after connection
time.sleep(2)  # Wait for connection
client.join('BINANCE:ETHUSDT', '1D')

# Your other code continues here...
print('Main thread continues...')
time.sleep(60)  # Keep running for 60 seconds
client.disconnect()
```

---

## API Reference

### Create Client

```python
from fcs_client_lib import FCSClient

client = FCSClient(api_key, url=None)
client.show_logs = True  # Enable console logs (default: False)
```

### Connection

```python
client.connect()                    # Connect to server
client.run_forever(blocking=True)   # Start receiving (blocking=False for background)
client.disconnect()                 # Disconnect from server
```

### Subscription

```python
client.join('BINANCE:BTCUSDT', '1D')   # Subscribe to symbol
client.leave('BINANCE:BTCUSDT', '1D')  # Unsubscribe from symbol
client.remove_all()                     # Unsubscribe from all
```

### Event Callbacks (Decorators)

```python
@client.on_connected
def on_connected():
    print('Connected!')

@client.on_message
def on_message(data):
    print(data)

@client.on_close
def on_close(code, msg):
    print(f'Closed: {code}')

@client.on_error
def on_error(error):
    print(f'Error: {error}')

@client.on_reconnect
def on_reconnect():
    print('Reconnected!')
```

### Properties

```python
client.is_connected          # Connection status (bool)
client.active_subscriptions  # Current subscriptions (dict)
client.reconnect_delay       # Reconnect delay in seconds (default: 3)
client.reconnect_limit       # Max reconnect attempts (default: 5)
client.show_logs             # Enable/disable console logs (default: False)
```

---

## Symbol Format

| Market | Format | Examples |
|--------|--------|----------|
| Forex | `FX:PAIR` | `FX:EURUSD`, `FX:GBPUSD` |
| Crypto | `EXCHANGE:PAIR` | `BINANCE:BTCUSDT`, `BINANCE:ETHUSDT` |
| Stock | `EXCHANGE:SYMBOL` | `NASDAQ:AAPL`, `NYSE:TSLA` |

## Timeframes

| Timeframe | Description |
|-----------|-------------|
| `1` | 1 minute |
| `5` | 5 minutes |
| `15` | 15 minutes |
| `1H` | 1 hour |
| `1D` | 1 day |
| `1W` | 1 week |

## Message Data Format

```python
# Price update
{
    "type": "price",
    "symbol": "BINANCE:BTCUSDT",
    "timeframe": "1D",
    "prices": {
        "mode": "candle",  # or "initial", "askbid"
        "t": 1766361600,   # Timestamp
        "o": 88658.87,     # Open
        "h": 90588.23,     # High
        "l": 87900,        # Low
        "c": 89962.61,     # Close
        "v": 8192.70,      # Volume
        "a": 89962.62,     # Ask
        "b": 89962.61      # Bid
    }
}
```

---

## Get API Key

1. Visit [FCS API](https://fcsapi.com)
2. Sign up for free
3. Get your API key

## Documentation

- [FCS API Docs](https://fcsapi.com/document/stock-api)
- [WebSocket Guide](https://fcsapi.com/document/stock-api#websocket)

## Support

- Email: support@fcsapi.com
- Website: [fcsapi.com](https://fcsapi.com)

## License

MIT License - see [LICENSE](LICENSE) file.
