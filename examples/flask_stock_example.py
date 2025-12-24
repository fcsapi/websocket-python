"""
FCS Real-time Stock Example with Flask

Real-time Stock price streaming using WebSocket
Demo API Key: fcs_socket_demo

Install: pip install flask
Run: python flask_stock_example.py
Then open http://localhost:5002 in your browser
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# Configuration
API_KEY = 'fcs_socket_demo'  # Replace with your API key
SYMBOLS = ['NASDAQ:AAPL', 'NASDAQ:GOOGL', 'NASDAQ:MSFT', 'NYSE:TSLA']
DEFAULT_TIMEFRAME = '1D'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FCS Real-time Stocks - Flask Example</title>
    <script src="https://cdn.jsdelivr.net/gh/fcsapi/websocket-python/fcs-client-lib.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            text-align: center;
            margin-bottom: 10px;
            font-size: 2rem;
            background: linear-gradient(90deg, #58a6ff, #1f6feb);
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
            background: #161b22;
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
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 25px;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(88, 166, 255, 0.3);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .symbol {
            font-size: 1.3rem;
            font-weight: 700;
            color: #58a6ff;
        }
        .exchange {
            font-size: 0.75rem;
            color: #666;
        }
        .timeframe {
            background: rgba(88, 166, 255, 0.2);
            padding: 4px 10px;
            border-radius: 10px;
            font-size: 0.75rem;
            color: #58a6ff;
        }
        .price {
            font-size: 2rem;
            font-weight: 700;
            font-family: 'Monaco', monospace;
            margin-bottom: 10px;
        }
        .price.up { color: #00ff88; }
        .price.down { color: #ff4757; }
        .volume {
            color: #666;
            font-size: 0.85rem;
        }
        .ohlc {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 0.85rem;
            color: #888;
        }
        .ohlc span { font-family: 'Monaco', monospace; color: #fff; }
        .api-hint {
            text-align: center;
            margin-top: 30px;
            padding: 15px;
            background: rgba(88, 166, 255, 0.1);
            border-radius: 8px;
            color: #58a6ff;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Real-time Stock Prices</h1>
        <p class="subtitle">Flask + WebSocket Example</p>

        <div class="controls">
            <div class="control-group">
                <label>Timeframe:</label>
                <select id="timeframe">
                    <option value="1">1 Min</option>
                    <option value="5">5 Min</option>
                    <option value="15">15 Min</option>
                    <option value="1H">1 Hour</option>
                    <option value="1D" selected>1 Day</option>
                </select>
            </div>
            <div id="connection-status" class="status connecting">
                <span class="status-dot"></span>
                <span>Connecting...</span>
            </div>
        </div>

        <div class="grid" id="prices-grid">
            {% for symbol in symbols %}
            <div class="card">
                <div class="card-header">
                    <div>
                        <span class="symbol">{{ symbol.split(':')[1] }}</span>
                        <span class="exchange">{{ symbol.split(':')[0] }}</span>
                    </div>
                    <span class="timeframe" id="tf-{{ symbol.replace(':', '-') }}">{{ timeframe }}</span>
                </div>
                <div class="price" id="price-{{ symbol.replace(':', '-') }}">$--</div>
                <div class="volume" id="vol-{{ symbol.replace(':', '-') }}">Vol: --</div>
                <div class="ohlc">
                    <div>O: <span id="open-{{ symbol.replace(':', '-') }}">--</span></div>
                    <div>H: <span id="high-{{ symbol.replace(':', '-') }}">--</span></div>
                    <div>L: <span id="low-{{ symbol.replace(':', '-') }}">--</span></div>
                    <div>C: <span id="close-{{ symbol.replace(':', '-') }}">--</span></div>
                </div>
            </div>
            {% endfor %}
        </div>

        <div class="api-hint">
            Demo API Key: <code>fcs_socket_demo</code> - Get your free API key at <a href="https://fcsapi.com" style="color: #58a6ff;">fcsapi.com</a>
        </div>
    </div>

    <script>
        const apiKey = '{{ api_key }}';
        const symbols = {{ symbols | tojson }};
        let currentTimeframe = '{{ timeframe }}';
        let previousPrices = {};

        const client = new FCSClient(apiKey);

        function updateStatus(status, text) {
            const el = document.getElementById('connection-status');
            el.className = 'status ' + status;
            el.innerHTML = '<span class="status-dot"></span><span>' + text + '</span>';
        }

        function formatPrice(price) {
            return parseFloat(price).toFixed(2);
        }

        function formatVolume(vol) {
            const num = parseFloat(vol);
            if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
            if (num >= 1000) return (num / 1000).toFixed(2) + 'K';
            return num.toFixed(0);
        }

        function updateCard(symbol, data) {
            const id = symbol.replace(':', '-');
            const p = data.prices;

            if (p.mode === 'initial' || p.mode === 'candle') {
                const priceEl = document.getElementById('price-' + id);
                const prevPrice = previousPrices[symbol];
                const currentPrice = parseFloat(p.c);

                priceEl.textContent = '$' + formatPrice(p.c);

                if (prevPrice !== undefined) {
                    priceEl.className = 'price ' + (currentPrice >= prevPrice ? 'up' : 'down');
                }
                previousPrices[symbol] = currentPrice;

                document.getElementById('open-' + id).textContent = formatPrice(p.o);
                document.getElementById('high-' + id).textContent = formatPrice(p.h);
                document.getElementById('low-' + id).textContent = formatPrice(p.l);
                document.getElementById('close-' + id).textContent = formatPrice(p.c);

                if (p.v !== undefined) {
                    document.getElementById('vol-' + id).textContent = 'Vol: ' + formatVolume(p.v);
                }
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
                document.getElementById('tf-' + s.replace(':', '-')).textContent = newTimeframe;
            });
            currentTimeframe = newTimeframe;
            symbols.forEach(s => client.join(s, currentTimeframe));
        });

        client.connect();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(
        HTML_TEMPLATE,
        api_key=API_KEY,
        symbols=SYMBOLS,
        timeframe=DEFAULT_TIMEFRAME
    )

if __name__ == '__main__':
    print("Starting FCS Real-time Stock Example (Flask)...")
    print("Open http://localhost:5002 in your browser")
    print("Press Ctrl+C to stop")
    app.run(debug=True, port=5002)
