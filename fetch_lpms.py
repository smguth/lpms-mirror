#!/usr/bin/env python3
"""Fetch the USACE LPMS feeds used by the Great Loop locks panel and
write them verbatim (plus meta.json) into an output directory.
Public data from https://ndc.ops.usace.army.mil/ords/lpms - LPMS sends
no CORS header, so browsers cannot read it directly; this mirror lets
a GitHub raw URL (Access-Control-Allow-Origin: *) carry the same bytes.
"""
import json, os, re, sys, time, urllib.request

BASE = 'https://ndc.ops.usace.army.mil/ords/lpms'
CHAIN = [('CH','01'),('IL','02'),('IL','03'),('IL','04'),('IL','05'),
         ('IL','06'),('IL','07'),('IL','08'),('MI','26'),('MI','27'),
         ('OH','79'),('TN','01'),('TN','02'),('TT','50'),('TT','49'),
         ('TT','48'),('TT','47'),('TT','46'),('TT','45'),('TT','44'),
         ('TT','43'),('TT','42'),('TT','41'),('BW','02'),('BW','01')]

def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'lpms-mirror/1.0 (+github actions)'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last

def main():
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else 'data_out'
    os.makedirs(out, exist_ok=True)
    feeds = {}
    def save(name, url, validate):
        try:
            body = fetch(url)
            validate(body)
            with open(os.path.join(out, name), 'wb') as f:
                f.write(body)
            feeds[name] = {'ok': True, 'bytes': len(body)}
            print('OK ', name, len(body))
        except Exception as e:
            feeds[name] = {'ok': False, 'error': str(e)[:120]}
            print('FAIL', name, e)
    save('delay.txt', BASE + '/lock_delay_json',
         lambda b: (_ for _ in ()).throw(ValueError('no riverCode')) if b'riverCode' not in b else None)
    save('stoppage.json', BASE + '/stall_stoppage_json',
         lambda b: json.loads(b.decode('utf-8', 'replace')))
    for river, num in CHAIN:
        name = 'queue_%s%s.json' % (river, num)
        save(name, '%s/json/lock_queue_json?in_river=%s&in_lock=%s' % (BASE, river, num),
             lambda b: json.loads(b.decode('utf-8', 'replace')))
    meta = {'fetchedAt': int(time.time()), 'source': BASE,
            'ok': sum(1 for v in feeds.values() if v['ok']), 'feeds': feeds}
    with open(os.path.join(out, 'meta.json'), 'w') as f:
        json.dump(meta, f, indent=1)
    print('fetchedAt', meta['fetchedAt'], 'ok', meta['ok'], 'of', len(feeds))
    return 0 if meta['ok'] >= 20 else 1

if __name__ == '__main__':
    sys.exit(main())
