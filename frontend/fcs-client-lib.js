(function (global) {
    const isNode = typeof window === 'undefined'; // Check if running in Node.js or browser
    const WebSocketImpl = isNode ? require('ws') : WebSocket;

    class FCSClient {
        constructor(apiKey,url=null) {
            this.url = url ? url : 'wss://ws-v4.fcsapi.com/ws';
            this.apiKey = apiKey;
            this.socket = null;
            this.activeSubscriptions = new Map();
            this.heartbeat = null;
            this.reconnectDelay = 3000;
            this.manualClose = false;
            this.isConnected = false;

            // Event callbacks
            this.onconnected = null;
            this.onclose = null;
            this.onmessage = null;
            this.onerror = null;
            this.onreconnect = null;
            this.countreconnects = 0;
            this.reconnectlimit = 5;
            this.isreconnect = false;

            // Tab visibility / connection mode settings
            this.focusTimeout = 3; // 3 minutes, custom settings, set 0 to never disconnect

            this.visibilityTimeout = null;
            this.visibilityDisconnectTime = null; // Track when disconnect timer started
            this.intentionalDisconnect = false; // Flag to prevent auto-reconnect when tab hidden
            // Initialize visibility handling if in browser
            if (!isNode && this.focusTimeout > 0) {
                this.initVisibilityHandling();
            }
        }

        /**
         * Connect returns a Promise that resolves when connected
         */
        connect() {
            if (this.focusTimeout > 0){
                this.focusTimeout = this.focusTimeout *60* 1000; // to seconds
            }

            if (!this.apiKey) return Promise.reject(new Error('API Key required'));

            return new Promise((resolve, reject) => {
                const wsUrl = `${this.url}?access_key=${this.apiKey}`;
                this.socket = new WebSocketImpl(wsUrl);

                this.socket.onopen = () => {
                    this.manualClose = false;
                    resolve(this); // resolve with client instance
                };

                this.socket.onmessage = (event) => {
                    let data;
                    try {
                        data = JSON.parse(isNode ? event.data.toString() : event.data);
                    } catch (e) {
                        console.error('[FCS] Invalid message from server, Please report this to support@fcsapi.com', e);
                        return;
                    }
                    console.log(data.type);
                    if (data.type === 'ping') {
                        this.send({ type: 'pong', timestamp: Date.now() });
                        return;
                    }else if (data.type === 'welcome') {
                        // Successfully connected, pass all security checks
                        this.isConnected = true;
                        this.countreconnects = 0;
                        this.intentionalDisconnect = false; // Reset flag on successful connection
                        this.visibilityDisconnectTime = null; // Clear disconnect timer
                        this.rejoinAll();
                        this.startHeartbeat();
                        if (this.isreconnect && typeof this.onreconnect === 'function') this.onreconnect();
                        if (!this.isreconnect && typeof this.onconnected === 'function') this.onconnected();
                        return;
                    }
                    else if (data.type === 'message') {
                        if (data.short && data.short === 'joined_room') {
                            console.log(`[FCS] Subscribed to ${data.symbol} ${data.timeframe}`);
                            if (data.symbol && data.timeframe) {
                                const key = `${data.symbol.toUpperCase()}_${data.timeframe}`;
                                this.activeSubscriptions.set(key, { symbol: data.symbol, timeframe: data.timeframe });
                            }
                        }
                    }
                    // Pass data to onmessage callback
                    if (typeof this.onmessage === 'function') this.onmessage(data);
                };

                this.socket.onerror = (err) => {
                    if (typeof this.onerror === 'function') this.onerror(err);
                };

                this.socket.onclose = (event) => {
                    console.warn(`[FCS] Disconnected. Code: ${event.code}, Reason: ${event.reason || 'none'}`);
                    this.stopHeartbeat();
                    this.isConnected = false;
                    this.socket = null;
                    if (typeof this.onclose === 'function') this.onclose(event);

                    // Smart reconnect logic
                    if (!this.manualClose) {
                        // Check if this was an intentional disconnect due to tab visibility
                        if (this.intentionalDisconnect) {
                            console.log('[FCS] Tab hidden disconnect - auto-reconnect disabled');
                            return;
                        }

                        // Check if we're within the visibility disconnect time limit
                        if (this.visibilityDisconnectTime) {
                            const delay = this.focusTimeout;
                            const elapsed = Date.now() - this.visibilityDisconnectTime;

                            if (elapsed >= delay) {
                                // Time limit exceeded, don't auto-reconnect
                                console.log('[FCS] Disconnect time limit exceeded - auto-reconnect disabled');
                                this.visibilityDisconnectTime = null;
                                return;
                            }
                        }

                        // Normal auto-reconnect for network issues
                        this.countreconnects++;
                        if(this.countreconnects > this.reconnectlimit){
                            console.error('[FCS] Maximum reconnect attempts reached. Please check your network or contact support@fcsapi.com');
                            return;
                        }
                        this.isreconnect = true;
                        setTimeout(() => this.connect(), this.reconnectDelay);
                    }
                };
            });
        }

        disconnect() {
            this.manualClose = true;
            this.isConnected = false;
            this.clearVisibilityTimeout(); // Clear any pending visibility timeout
            if (this.socket) {
                this.socket.close();
                this.socket = null;
                this.stopHeartbeat();
            }
        }

        // this is making it alove in browser and nodejs
        startHeartbeat() {
            if (!this.socket) return;
            this.stopHeartbeat();
            this.heartbeat = setInterval(() => {
                // for browser and nodejs
                if (this.socket && this.socket.readyState === WebSocketImpl.OPEN) {
                    if (isNode) this.socket.ping();
                }

                // for fcs server
                this.send({ type: 'ping', timestamp: Date.now() });
            }, 25000);
        }

        stopHeartbeat() {
            if (this.heartbeat) {
                clearInterval(this.heartbeat);
                this.heartbeat = null;
            }
        }

        send(data) {
            if (!this.socket || this.socket.readyState !== WebSocketImpl.OPEN) return false;
            try {
                this.socket.send(JSON.stringify(data));
                return true;
            } catch (e) {
                return false;
            }
        }

        join(symbol, timeframe) {
            if (!symbol || !timeframe) {console.error('[FCS] Symbol and timeframe are required to join'); return; };
            if (!symbol.includes(':')) {console.error('[FCS] Symbol must include exchange prefix, e.g., "BINANCE:BTCUSDT"'); return; };

            this.send({ type: 'join_symbol', symbol, timeframe });
        }

        leave(symbol, timeframe) {
            if (!symbol || !timeframe) return;
            const key = `${symbol.toUpperCase()}_${timeframe}`;
            this.activeSubscriptions.delete(key);
            this.send({ type: 'leave_symbol', symbol, timeframe });
        }

        removeAll() {
            this.activeSubscriptions.clear();
            this.send({ type: 'remove_all' });
        }

        rejoinAll() {
            this.activeSubscriptions.forEach(({ symbol, timeframe }) => {
                this.send({ type: 'join_symbol', symbol, timeframe });
            });
        }

        /**
         * Initialize Page Visibility API handling for automatic disconnect/reconnect
         * Only works in browser environment
         */
        initVisibilityHandling() {
            console.log(document.visibilityState);
            if (typeof document === 'undefined') return;

            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    // Tab hidden - schedule disconnect based on mode
                    this.handleTabHidden();
                } else {
                    // Tab visible - cancel disconnect and reconnect if needed
                    this.handleTabVisible();
                }
            });
        }

        /**
         * Handle when browser tab becomes hidden
         */
        handleTabHidden() {
            this.clearVisibilityTimeout();
            // Set delay based on connection mode
            // auto: 3 seconds, persistent: 10 seconds (approximate)
            const delay = this.focusTimeout;

            console.log(`[FCS] Tab hidden. Will disconnect in ${delay / 1000}s if not returned (focusTimeout: ${this.focusTimeout})`);

            // Mark when the disconnect timer started
            this.visibilityDisconnectTime = Date.now();

            this.visibilityTimeout = setTimeout(() => {
                if (this.isConnected) {
                    console.log('[FCS] Tab inactive - disconnecting to save resources');
                    this.intentionalDisconnect = true; // Prevent auto-reconnect
                    this.manualClose = true; // Treat as manual close
                    this.disconnect();
                    this.manualClose = false; // Reset for future reconnects
                }
            }, delay);
        }

        /**
         * Handle when browser tab becomes visible
         */
        handleTabVisible() {
            this.clearVisibilityTimeout();
            if(this.manualClose) return; // Do nothing if manually closed

            // If tab became visible before time limit, allow reconnect
            if (this.visibilityDisconnectTime) {
                const delay = this.focusTimeout;
                const elapsed = Date.now() - this.visibilityDisconnectTime;

                if (elapsed < delay) {
                    // Within time limit - clear the timer
                    this.visibilityDisconnectTime = null;
                }
            }

            // Reconnect if we have active subscriptions but no connection
            if (!this.isConnected && this.activeSubscriptions.size > 0) {
                console.log('[FCS] Tab active - reconnecting...');
                this.intentionalDisconnect = false;
                this.visibilityDisconnectTime = null;
                this.connect();
            } else if (this.isConnected) {
                console.log('[FCS] Tab active - connection maintained');
            }
        }

        /**
         * Clear pending visibility timeout
         */
        clearVisibilityTimeout() {
            if (this.visibilityTimeout) {
                clearTimeout(this.visibilityTimeout);
                this.visibilityTimeout = null;
            }
        }
    }

    if (isNode) module.exports = FCSClient;
    else global.FCSClient = FCSClient;

})(typeof window !== 'undefined' ? window : global);