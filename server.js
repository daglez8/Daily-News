// Minimal static file server for local preview (Phase 1).
// Serves this folder so the dashboard can fetch news.json over http.
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, 'docs'); // serve the published folder (same as GitHub Pages)
const PORT = process.env.PORT || 8000;
const TYPES = { '.html':'text/html', '.json':'application/json', '.js':'text/javascript', '.css':'text/css', '.svg':'image/svg+xml' };

http.createServer((req, res) => {
  let rel = decodeURIComponent(req.url.split('?')[0]);
  if (rel === '/') rel = '/index.html';
  const file = path.join(ROOT, path.normalize(rel));
  if (!file.startsWith(ROOT)) { res.writeHead(403); return res.end('Forbidden'); }
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); return res.end('Not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
    res.end(data);
  });
}).listen(PORT, () => console.log(`news-dashboard on http://localhost:${PORT}`));
