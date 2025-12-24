# FCS WebSocket Python

Real-time WebSocket client library for **Forex**, **Cryptocurrency**, and **Stock** market data from [FCS API](https://fcsapi.com).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/fcsapi-websocket-python.svg)](https://pypi.org/project/fcsapi-websocket-python/)

## Features

- **Real-time WebSocket** - Live price updates via WebSocket connection
- **Multi-Market Support** - Forex, Crypto, and Stock data
- **Frontend & Backend** - Use in browser or pure Python
- **Auto-Reconnect** - Handles connection drops automatically
- **No Dependencies** - Frontend uses Python built-in modules

## Installation

```bash
pip install fcsapi-websocket-python
```

For backend usage, also install:
```bash
pip install websocket-client
```

## Demo

Use demo API key for testing: `fcs_socket_demo`

---

## Frontend (Browser-based)

For web applications that display real-time prices in the browser.

### Structure
```
frontend/
├── fcs-client-lib.js      # JavaScript WebSocket client
└── examples/
    ├── crypto_example.py  # Crypto prices in browser
    ├── forex_example.py   # Forex prices in browser
    └── stock_example.py   # Stock prices in browser
```

### Quick Start

```bash
cd frontend/examples
python crypto_example.py
# Open http://localhost:5000
```

### How it works
- Python serves HTML page with embedded JavaScript
- JavaScript (`fcs-client-lib.js`) connects to WebSocket
- Real-time updates displayed in browser

---

## Backend (Pure Python)

For server-side applications, bots, or scripts that need real-time data without a browser.

### Structure
```
backend/
├── fcs_client_lib.py      # Python WebSocket client
└── examples/
    ├── crypto_example.py  # Terminal crypto prices
    ├── forex_example.py   # Terminal forex prices
    └── stock_example.py   # Terminal stock prices
```

### Quick Start

```bash
pip install websocket-client
cd backend/examples
python crypto_example.py
```

### Usage

```python
from backend import FCSClient

client = FCSClient('YOUR_API_KEY')

@client.on_message
def handle_message(data):
    if data.get('type') == 'price':
        print(data)

client.connect()
client.join('BINANCE:BTCUSDT', '1D')
client.run_forever()
```

### Backend API

```python
from backend import FCSClient

# Create client
client = FCSClient(api_key, url=None)

# Connect
client.connect()
client.run_forever(blocking=True)  # blocking=False for background

# Subscribe
client.join('BINANCE:BTCUSDT', '1D')
client.leave('BINANCE:BTCUSDT', '1D')
client.remove_all()

# Disconnect
client.disconnect()

# Event callbacks (decorators)
@client.on_connected
@client.on_message
@client.on_close
@client.on_error
@client.on_reconnect
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
