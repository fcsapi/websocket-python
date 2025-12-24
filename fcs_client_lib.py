"""
FCS WebSocket Client Library for Python Backend

Pure Python WebSocket client for real-time Forex, Crypto, and Stock data.
No browser required - runs directly in Python.

Usage:
    from fcs_client_lib import FCSClient

    client = FCSClient('YOUR_API_KEY')

    @client.on_message
    def handle_message(data):
        print(data)

    client.connect()
    client.join('BINANCE:BTCUSDT', '1D')
    client.run_forever()

Install:
    pip install websocket-client
"""

import json
import threading
import time
import ssl

try:
    import websocket
except ImportError:
    raise ImportError("Please install websocket-client: pip install websocket-client")


class FCSClient:
    """
    FCS WebSocket client for Python backend applications.

    Provides real-time market data streaming for:
    - Forex (FX:EURUSD, FX:GBPUSD, etc.)
    - Crypto (BINANCE:BTCUSDT, BINANCE:ETHUSDT, etc.)
    - Stocks (NASDAQ:AAPL, NYSE:TSLA, etc.)
    """

    def __init__(self, api_key, url=None):
        """
        Initialize FCS WebSocket client.

        Args:
            api_key (str): Your FCS API key (use 'fcs_socket_demo' for testing)
            url (str, optional): WebSocket server URL
        """
        self.url = url or 'wss://ws-v4.fcsapi.com/ws'
        self.api_key = api_key
        self.socket = None
        self.active_subscriptions = {}  # Map() equivalent
        self.heartbeat = None
        self.reconnect_delay = 3  # seconds (3000ms in JS)
        self.manual_close = False
        self.is_connected = False
        self.show_logs = False  # Control console output (like JS showLogs)

        # Event callbacks
        self._onconnected = None
        self._onclose = None
        self._onmessage = None
        self._onerror = None
        self._onreconnect = None
        self.count_reconnects = 0
        self.reconnect_limit = 5
        self.is_reconnect = False

        # Heartbeat thread
        self._heartbeat_thread = None
        self._stop_heartbeat = False

    # ============================================
    # Event callback decorators (like JS callbacks)
    # ============================================

    @property
    def onconnected(self):
        return self._onconnected

    @onconnected.setter
    def onconnected(self, func):
        self._onconnected = func

    def on_connected(self, func):
        """Decorator for connection callback."""
        self._onconnected = func
        return func

    @property
    def onmessage(self):
        return self._onmessage

    @onmessage.setter
    def onmessage(self, func):
        self._onmessage = func

    def on_message(self, func):
        """Decorator for message callback."""
        self._onmessage = func
        return func

    @property
    def onclose(self):
        return self._onclose

    @onclose.setter
    def onclose(self, func):
        self._onclose = func

    def on_close(self, func):
        """Decorator for close callback."""
        self._onclose = func
        return func

    @property
    def onerror(self):
        return self._onerror

    @onerror.setter
    def onerror(self, func):
        self._onerror = func

    def on_error(self, func):
        """Decorator for error callback."""
        self._onerror = func
        return func

    @property
    def onreconnect(self):
        return self._onreconnect

    @onreconnect.setter
    def onreconnect(self, func):
        self._onreconnect = func

    def on_reconnect(self, func):
        """Decorator for reconnect callback."""
        self._onreconnect = func
        return func

    # ============================================
    # Connection methods
    # ============================================

    def connect(self):
        """
        Connect to FCS WebSocket server.
        Returns self for chaining.
        """
        if not self.api_key:
            raise ValueError('API Key required')

        ws_url = f"{self.url}?access_key={self.api_key}"

        self.socket = websocket.WebSocketApp(
            ws_url,
            on_open=self._handle_open,
            on_message=self._handle_message,
            on_error=self._handle_error,
            on_close=self._handle_close
        )

        return self

    def run_forever(self, blocking=True):
        """
        Start the WebSocket connection.

        Args:
            blocking (bool): If True, blocks the main thread. If False, runs in background.
        """
        if blocking:
            self.socket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            thread = threading.Thread(
                target=lambda: self.socket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            )
            thread.daemon = True
            thread.start()
            return thread

    def disconnect(self):
        """Disconnect from WebSocket server."""
        self.manual_close = True
        self.is_connected = False
        self._stop_heartbeat = True
        if self.socket:
            self.socket.close()

    # ============================================
    # Subscription methods
    # ============================================

    def join(self, symbol, timeframe):
        """
        Subscribe to a symbol for real-time updates.

        Args:
            symbol (str): Symbol with exchange prefix (e.g., 'BINANCE:BTCUSDT', 'FX:EURUSD')
            timeframe (str): Timeframe (e.g., '1', '5', '15', '1H', '1D')
        """
        if not symbol or not timeframe:
            if self.show_logs:
                print('[FCS] Symbol and timeframe are required to join')
            return

        if ':' not in symbol:
            if self.show_logs:
                print('[FCS] Symbol must include exchange prefix, e.g., "BINANCE:BTCUSDT"')
            return

        self._send({'type': 'join_symbol', 'symbol': symbol, 'timeframe': timeframe})

    def leave(self, symbol, timeframe):
        """
        Unsubscribe from a symbol.

        Args:
            symbol (str): Symbol to unsubscribe
            timeframe (str): Timeframe
        """
        if not symbol or not timeframe:
            return

        key = f"{symbol.upper()}_{timeframe}"
        self.active_subscriptions.pop(key, None)
        self._send({'type': 'leave_symbol', 'symbol': symbol, 'timeframe': timeframe})

    def remove_all(self):
        """Unsubscribe from all symbols."""
        self.active_subscriptions.clear()
        self._send({'type': 'remove_all'})

    def _rejoin_all(self):
        """Rejoin all subscriptions after reconnect."""
        for sub in self.active_subscriptions.values():
            self._send({'type': 'join_symbol', 'symbol': sub['symbol'], 'timeframe': sub['timeframe']})

    # ============================================
    # Internal methods
    # ============================================

    def _send(self, data):
        """Send data to WebSocket server."""
        if not self.socket or not self.is_connected:
            return False
        try:
            self.socket.send(json.dumps(data))
            return True
        except Exception as e:
            if self.show_logs:
                print(f'[FCS] Send error: {e}')
            return False

    def _handle_open(self, ws):
        """Handle WebSocket connection open."""
        self.manual_close = False
        if self.show_logs:
            print('[FCS] WebSocket connection opened')

    def _handle_message(self, ws, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError as e:
            if self.show_logs:
                print(f'[FCS] Invalid message from server: {e}')
            return

        # Handle ping
        if data.get('type') == 'ping':
            self._send({'type': 'pong', 'timestamp': int(time.time() * 1000)})
            return

        # Handle welcome message
        if data.get('type') == 'welcome':
            self.is_connected = True
            self.count_reconnects = 0
            self._rejoin_all()
            self._start_heartbeat()

            if self.is_reconnect and callable(self._onreconnect):
                self._onreconnect()
            elif not self.is_reconnect and callable(self._onconnected):
                self._onconnected()
            return

        # Handle subscription confirmation
        if data.get('type') == 'message' and data.get('short') == 'joined_room':
            symbol = data.get('symbol')
            timeframe = data.get('timeframe')
            if symbol and timeframe:
                key = f"{symbol.upper()}_{timeframe}"
                self.active_subscriptions[key] = {'symbol': symbol, 'timeframe': timeframe}
                if self.show_logs:
                    print(f'[FCS] Subscribed to {symbol} {timeframe}')

        # Call user's message handler
        if callable(self._onmessage):
            self._onmessage(data)

    def _handle_error(self, ws, error):
        """Handle WebSocket error."""
        if self.show_logs:
            print(f'[FCS] Error: {error}')
        if callable(self._onerror):
            self._onerror(error)

    def _handle_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close."""
        if self.show_logs:
            print(f'[FCS] Disconnected. Code: {close_status_code}, Reason: {close_msg}')
        self.is_connected = False
        self._stop_heartbeat = True

        if callable(self._onclose):
            self._onclose(close_status_code, close_msg)

        # Auto-reconnect (like JS version)
        if not self.manual_close and self.count_reconnects < self.reconnect_limit:
            self.count_reconnects += 1
            self.is_reconnect = True
            if self.show_logs:
                print(f'[FCS] Reconnecting in {self.reconnect_delay}s... (attempt {self.count_reconnects}/{self.reconnect_limit})')
            time.sleep(self.reconnect_delay)
            self.connect()
            self.run_forever()

    def _start_heartbeat(self):
        """Start heartbeat to keep connection alive."""
        self._stop_heartbeat = False

        def heartbeat():
            while not self._stop_heartbeat and self.is_connected:
                self._send({'type': 'ping', 'timestamp': int(time.time() * 1000)})
                time.sleep(25)  # 25000ms in JS

        self._heartbeat_thread = threading.Thread(target=heartbeat)
        self._heartbeat_thread.daemon = True
        self._heartbeat_thread.start()

    def _stop_heartbeat_thread(self):
        """Stop heartbeat thread."""
        self._stop_heartbeat = True


# ============================================
# Module exports (like JS module.exports)
# ============================================

def create_client(api_key, url=None):
    """
    Create FCS WebSocket client.

    Args:
        api_key (str): Your FCS API key
        url (str, optional): WebSocket server URL

    Returns:
        FCSClient: Client instance
    """
    return FCSClient(api_key, url)


# For direct execution test
if __name__ == '__main__':
    print("FCS WebSocket Client Library for Python")
    print("=" * 40)
    print("Import and use:")
    print("  from fcs_client_lib import FCSClient")
    print("  client = FCSClient('fcs_socket_demo')")
    print("  client.connect()")
    print("  client.join('BINANCE:BTCUSDT', '1D')")
    print("  client.run_forever()")
