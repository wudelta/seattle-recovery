const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = 3000;
const DJANGO_TARGET = 'http://django_app:8000';

// 1. Serve Django Static Files directly via NodeJS
app.use('/static', express.static(path.join(__dirname, 'staticfiles')));

// 2. Proxy WebSockets to Daphne
const wsProxy = createProxyMiddleware({
    target: DJANGO_TARGET,
    changeOrigin: false,
    ws: true,
    logger: console
});
app.use('/ws', wsProxy);

// 3. Proxy all other HTTP routing endpoints to Django
app.use('/', createProxyMiddleware({
    target: DJANGO_TARGET,
    changeOrigin: false,
    logger: console
}));

const server = app.listen(PORT, () => {
    console.log(`NodeJS Reverse Proxy listening on port ${PORT}`);
});

// Upgrade HTTP server to handle WebSocket connection handshakes
server.on('upgrade', wsProxy.upgrade);
