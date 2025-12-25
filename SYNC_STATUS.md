# FCS WebSocket Library Sync Status

**Last Synced:** 2025-12-24
**JS Version:** fcs-client-lib.js
**PY Version:** fcs_client_lib.py
**Status:** IN_SYNC

---

## Feature Comparison

| Feature | JS | Python | Notes |
|---------|:--:|:------:|-------|
| **Core Connection** |
| connect() | ✅ | ✅ | |
| disconnect() | ✅ | ✅ | |
| send() | ✅ | ✅ | `_send()` in Python |
| **Subscription** |
| join(symbol, timeframe) | ✅ | ✅ | |
| leave(symbol, timeframe) | ✅ | ✅ | |
| removeAll() | ✅ | ✅ | `remove_all()` in Python |
| rejoinAll() | ✅ | ✅ | `_rejoin_all()` in Python |
| activeSubscriptions | ✅ | ✅ | `active_subscriptions` in Python |
| **Event Callbacks** |
| onconnected | ✅ | ✅ | |
| onmessage | ✅ | ✅ | |
| onclose | ✅ | ✅ | |
| onerror | ✅ | ✅ | |
| onreconnect | ✅ | ✅ | |
| **Reconnection** |
| reconnectDelay | ✅ | ✅ | `reconnect_delay` in Python |
| reconnectLimit | ✅ | ✅ | `reconnect_limit` in Python |
| countReconnects | ✅ | ✅ | `count_reconnects` in Python |
| isReconnect | ✅ | ✅ | `is_reconnect` in Python |
| Auto-reconnect logic | ✅ | ✅ | |
| **Heartbeat** |
| startHeartbeat() | ✅ | ✅ | `_start_heartbeat()` in Python |
| stopHeartbeat() | ✅ | ✅ | `_stop_heartbeat` flag in Python |
| 25s interval | ✅ | ✅ | |
| **Logging** |
| showLogs | ✅ | ✅ | Controls console output |
| **Message Handling** |
| ping/pong | ✅ | ✅ | |
| welcome message | ✅ | ✅ | |
| joined_room confirmation | ✅ | ✅ | |
| **Browser-Only (Not in Python)** |
| focusTimeout | ✅ | ❌ | Browser tab visibility - N/A for Python |
| initVisibilityHandling() | ✅ | ❌ | Browser only |
| handleTabHidden() | ✅ | ❌ | Browser only |
| handleTabVisible() | ✅ | ❌ | Browser only |
| clearVisibilityTimeout() | ✅ | ❌ | Browser only |
| **Python-Only Extras** |
| run_forever(blocking) | ❌ | ✅ | Python threading support |
| Decorator callbacks | ❌ | ✅ | @client.on_message pattern |
| create_client() helper | ❌ | ✅ | Factory function |

---

## Properties Mapping

| JavaScript | Python |
|------------|--------|
| `this.url` | `self.url` |
| `this.apiKey` | `self.api_key` |
| `this.socket` | `self.socket` |
| `this.activeSubscriptions` | `self.active_subscriptions` |
| `this.heartbeat` | `self._heartbeat_thread` |
| `this.reconnectDelay` | `self.reconnect_delay` |
| `this.manualClose` | `self.manual_close` |
| `this.isConnected` | `self.is_connected` |
| `this.showLogs` | `self.show_logs` |
| `this.countreconnects` | `self.count_reconnects` |
| `this.reconnectlimit` | `self.reconnect_limit` |
| `this.isreconnect` | `self.is_reconnect` |

---

## Sync Instructions

When updating JS file, update Python file with these rules:

1. **New property added in JS** → Add to Python `__init__` with snake_case
2. **New method added in JS** → Add to Python class with snake_case
3. **Property removed in JS** → Remove from Python
4. **Method removed in JS** → Remove from Python
5. **Logic changed in JS** → Update corresponding Python logic

**Ignore these JS features (browser-only):**
- Tab visibility handling (`focusTimeout`, `initVisibilityHandling`, etc.)
- `WebSocketImpl` browser detection (Python always uses websocket-client)

---

## Change Log

### 2025-12-24 - Initial Sync
- Added `show_logs` property to Python `__init__`
- Updated all print statements to respect `show_logs` flag
- All core features synced
- Browser-only features excluded (not applicable to Python backend)

