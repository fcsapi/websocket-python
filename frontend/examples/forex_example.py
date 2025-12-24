"""
FCS Real-time Forex Example

Real-time Forex price streaming using WebSocket
Demo API Key: fcs_socket_demo

Run: python forex_example.py
Then open http://localhost:5001 in your browser
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

# Configuration
API_KEY = 'fcs_socket_demo'  # Replace with your API key
SYMBOLS = ['FX:EURUSD', 'FX:GBPUSD', 'FX:USDJPY', 'FX:AUDUSD']
DEFAULT_TIMEFRAME = '1D'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FCS Real-time Forex - Python Example</title>
    <script src="/fcs-client-lib.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 2rem;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .control-group { display: flex; align-items: center; gap: 10px; }
        .control-group label { color: #888; font-size: 0.9rem; }
        select {
            padding: 10px 15px;
            border: 1px solid #333;
            border-radius: 8px;
            background: #1a1a2e;
            color: #fff;
            font-size: 1rem;
            cursor: pointer;
        }
        .status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        .status.connected { background: rgba(0, 255, 136, 0.2); color: #00ff88; }
        .status.disconnected { background: rgba(255, 71, 87, 0.2); color: #ff4757; }
        .status.connecting { background: rgba(255, 193, 7, 0.2); color: #ffc107; }
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: currentColor;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 212, 255, 0.3);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .symbol {
            font-size: 1.3rem;
            font-weight: 700;
            color: #00d4ff;
        }
        .timeframe {
            background: rgba(0, 212, 255, 0.2);
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            color: #00d4ff;
        }
        .price {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 15px;
            font-family: 'Monaco', monospace;
        }
        .price.up { color: #00ff88; }
        .price.down { color: #ff4757; }
        .ohlc {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .ohlc-item {
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 8px;
        }
        .ohlc-label {
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 4px;
        }
        .ohlc-value {
            font-size: 1rem;
            font-family: 'Monaco', monospace;
        }
        .spread {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
        }
        .spread-item { text-align: center; }
        .spread-label { font-size: 0.75rem; color: #666; }
        .spread-value { font-size: 1rem; font-family: 'Monaco', monospace; }
        .ask { color: #00ff88; }
        .bid { color: #ff4757; }
        .api-hint {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 8px;
            color: #ffc107;
            font-size: 0.9rem;
        }
        .api-hint code {
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 8px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Real-time Forex Prices</h1>
        <p class="subtitle">Live WebSocket streaming with Python</p>

        <div class="controls">
            <div class="control-group">
                <label>Timeframe:</label>
                <select id="timeframe">
                    <option value="1">1 Minute</option>
                    <option value="5">5 Minutes</option>
                    <option value="15">15 Minutes</option>
                    <option value="30">30 Minutes</option>
                    <option value="1H">1 Hour</option>
                    <option value="4H">4 Hours</option>
                    <option value="1D" selected>1 Day</option>
                    <option value="1W">1 Week</option>
                    <option value="1M">1 Month</option>
                </select>
            </div>
            <div id="connection-status" class="status connecting">
                <span class="status-dot"></span>
                <span>Connecting...</span>
            </div>
        </div>

        <div class="grid" id="prices-grid">
            <!--SYMBOLS_PLACEHOLDER-->
        </div>

        <div class="api-hint">
            Demo API Key: <code>fcs_socket_demo</code> - Get your free API key at <a href="https://fcsapi.com" target="_blank" style="color: #00d4ff;">fcsapi.com</a>
        </div>
    </div>

    <script>
        const apiKey = '<!--API_KEY-->';
        const symbols = <!--SYMBOLS_JSON-->;
        let currentTimeframe = '<!--DEFAULT_TIMEFRAME-->';
        let previousPrices = {};

        const client = new FCSClient(apiKey);

        function updateStatus(status, text) {
            const el = document.getElementById('connection-status');
            el.className = 'status ' + status;
            el.innerHTML = '<span class="status-dot"></span><span>' + text + '</span>';
        }

        function formatPrice(price, decimals = 5) {
            return parseFloat(price).toFixed(decimals);
        }

        function updateCard(symbol, data) {
            const id = symbol.replace(':', '-');
            const p = data.prices;

            if (p.mode === 'initial' || p.mode === 'candle') {
                const priceEl = document.getElementById('price-' + id);
                const prevPrice = previousPrices[symbol];
                const currentPrice = parseFloat(p.c);

                priceEl.textContent = formatPrice(p.c);

                if (prevPrice !== undefined) {
                    priceEl.className = 'price ' + (currentPrice >= prevPrice ? 'up' : 'down');
                }
                previousPrices[symbol] = currentPrice;

                document.getElementById('open-' + id).textContent = formatPrice(p.o);
                document.getElementById('high-' + id).textContent = formatPrice(p.h);
                document.getElementById('low-' + id).textContent = formatPrice(p.l);
                document.getElementById('close-' + id).textContent = formatPrice(p.c);

                if (p.a) document.getElementById('ask-' + id).textContent = formatPrice(p.a);
                if (p.b) document.getElementById('bid-' + id).textContent = formatPrice(p.b);
            }

            if (p.mode === 'askbid') {
                document.getElementById('ask-' + id).textContent = formatPrice(p.a);
                document.getElementById('bid-' + id).textContent = formatPrice(p.b);
            }
        }

        client.onconnected = () => {
            updateStatus('connected', 'Connected');
            symbols.forEach(s => client.join(s, currentTimeframe));
        };

        client.onmessage = (data) => {
            if (data.type === 'price' && data.prices) {
                updateCard(data.symbol, data);
            }
        };

        client.onclose = () => updateStatus('disconnected', 'Disconnected');
        client.onerror = () => updateStatus('disconnected', 'Error');
        client.onreconnect = () => updateStatus('connected', 'Reconnected');

        document.getElementById('timeframe').addEventListener('change', function() {
            const newTimeframe = this.value;

            symbols.forEach(s => {
                client.leave(s, currentTimeframe);
                const id = s.replace(':', '-');
                document.getElementById('tf-' + id).textContent = newTimeframe;
            });

            currentTimeframe = newTimeframe;

            symbols.forEach(s => client.join(s, currentTimeframe));
        });

        client.connect();
    </script>
</body>
</html>
'''

def generate_symbol_cards(symbols, default_timeframe):
    cards = ''
    for symbol in symbols:
        symbol_id = symbol.replace(':', '-')
        cards += f'''
            <div class="card" id="card-{symbol_id}">
                <div class="card-header">
                    <span class="symbol">{symbol}</span>
                    <span class="timeframe" id="tf-{symbol_id}">{default_timeframe}</span>
                </div>
                <div class="price" id="price-{symbol_id}">--</div>
                <div class="ohlc">
                    <div class="ohlc-item">
                        <div class="ohlc-label">OPEN</div>
                        <div class="ohlc-value" id="open-{symbol_id}">--</div>
                    </div>
                    <div class="ohlc-item">
                        <div class="ohlc-label">HIGH</div>
                        <div class="ohlc-value" id="high-{symbol_id}">--</div>
                    </div>
                    <div class="ohlc-item">
                        <div class="ohlc-label">LOW</div>
                        <div class="ohlc-value" id="low-{symbol_id}">--</div>
                    </div>
                    <div class="ohlc-item">
                        <div class="ohlc-label">CLOSE</div>
                        <div class="ohlc-value" id="close-{symbol_id}">--</div>
                    </div>
                </div>
                <div class="spread">
                    <div class="spread-item">
                        <div class="spread-label">ASK</div>
                        <div class="spread-value ask" id="ask-{symbol_id}">--</div>
                    </div>
                    <div class="spread-item">
                        <div class="spread-label">BID</div>
                        <div class="spread-value bid" id="bid-{symbol_id}">--</div>
                    </div>
                </div>
            </div>
        '''
    return cards

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = HTML_TEMPLATE
            html = html.replace('<!--SYMBOLS_PLACEHOLDER-->', generate_symbol_cards(SYMBOLS, DEFAULT_TIMEFRAME))
            html = html.replace('<!--API_KEY-->', API_KEY)
            html = html.replace('<!--SYMBOLS_JSON-->', json.dumps(SYMBOLS))
            html = html.replace('<!--DEFAULT_TIMEFRAME-->', DEFAULT_TIMEFRAME)

            self.wfile.write(html.encode())
        elif self.path == '/fcs-client-lib.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            with open('../fcs-client-lib.js', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

if __name__ == '__main__':
    port = 5001
    server = HTTPServer(('localhost', port), RequestHandler)
    print(f"Starting FCS Real-time Forex Example...")
    print(f"Open http://localhost:{port} in your browser")
    print("Press Ctrl+C to stop")
    server.serve_forever()
