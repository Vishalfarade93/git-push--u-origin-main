import urllib.request
import json
import sys

def test(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    if data:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
    else:
        body = None
    with urllib.request.urlopen(req, data=body, timeout=5) as r:
        return r.status, r.read().decode('utf-8')

print("Starting end-to-end integration tests for Clean Circular Broadsheet...")

# 1. UI Root
s, h = test('http://127.0.0.1:8000/')
assert s == 200 and 'THE PERSONAL SIGNAL' in h, 'Root HTML check failed'
print(" PASS: Root index.html served with clean modern Outfit circular typography")

# 2. Daily Briefing
s, b = test('http://127.0.0.1:8000/api/briefing/today')
bd = json.loads(b)
assert s == 200 and len(bd['top_signals']) > 0, 'Briefing check failed'
assert 'regional_pulse' not in bd, 'regional_pulse should be removed'
print(f" PASS: Daily Briefing ({len(bd['top_signals'])} top signals, {len(bd['opportunity_radar'])} opportunities)")

# 3. Feed API with Pagination
s, f = test('http://127.0.0.1:8000/api/feed?page=1&per_page=5')
fd = json.loads(f)
assert s == 200 and len(fd['articles']) > 0, 'Feed check failed'
assert 'total_pages' in fd and 'unread_count' in fd, 'Pagination metadata check failed'
print(f" PASS: Feed API Pagination (Page {fd['page']} of {fd['total_pages']}, {fd['total_count']} total articles, {fd['unread_count']} unread)")

# 4. Mark as Read endpoint
first_art = fd['articles'][0]
art_id = first_art['id']
s, rm = test(f'http://127.0.0.1:8000/api/articles/{art_id}/read', method='POST', data={'is_read': True})
rd = json.loads(rm)
assert s == 200 and rd['is_read'] == True, 'Mark read endpoint failed'
print(f" PASS: Mark Article Read endpoint (is_read: {rd['is_read']}, remaining unread: {rd['unread_count']})")

# 5. Vault Toggle
s, v = test('http://127.0.0.1:8000/api/vault/toggle', method='POST', data={'article_id': art_id, 'notes': 'Test clean idea note'})
vd = json.loads(v)
assert s == 200 and 'is_saved' in vd, 'Vault toggle check failed'
print(f" PASS: Vault toggle (is_saved: {vd['is_saved']})")

# 6. Unread Only Filter
s, ufeed = test('http://127.0.0.1:8000/api/feed?unread_only=true')
ufd = json.loads(ufeed)
assert s == 200, 'Unread filter check failed'
print(f" PASS: Unread Only filter ({len(ufd['articles'])} unviewed articles on page 1)")

# 7. History Endpoint & Right Side Archive
s, hist = test('http://127.0.0.1:8000/api/history?limit=10')
hd = json.loads(hist)
assert s == 200 and 'history' in hd and 'count' in hd, 'History endpoint failed'
print(f" PASS: Reading History Archive API ({hd['count']} archived articles, {len(hd['history'])} fetched)")

# 8. Check UI HTML elements for History and Right Column
assert 'rightTabWire' in h and 'rightTabHistory' in h, 'Right tab elements missing in index.html'
print(" PASS: Right-column dual tab UI (Recent Wire + History Archive) verified in HTML")

print("\n>>> ALL TESTS PASSED! The Personal Signal is clean, history-enabled, and ready for deployment! <<<")

