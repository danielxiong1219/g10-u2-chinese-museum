# -*- coding: utf-8 -*-
"""补齐缺失的肖像/背景图，带延时与重试，肖像加 Commons 兜底。"""
import urllib.request, urllib.parse, json, os, time

UA = {'User-Agent': 'MuseumCurationSchoolProject/1.0 (educational use)'}
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'images')
JSONP = os.path.join(BASE, 'images.json')

PEOPLE = [
    ("袁隆平", "rice paddy field"),
    ("张秉贵", "candy sweets shop"),
    ("钟扬", "tibetan plateau mountain"),
    ("高凤林", "welding sparks metal"),
    ("钱学森", "rocket launch"),
    ("邓稼先", "gobi desert sand"),
    ("屠呦呦", "artemisia annua herb"),
    ("南仁东", "fast radio telescope"),
    ("华罗庚", "mathematics blackboard equations"),
    ("李四光", "geology rock strata mountain"),
    ("茅以升", "bridge river arch"),
    ("于敏", "nuclear physics laboratory"),
    ("孙家栋", "satellite earth orbit space"),
    ("王进喜", "oil field derrick pumpjack"),
    ("时传祥", "clean street city"),
    ("许振超", "container port crane ship"),
    ("焦裕禄", "paulownia tree green"),
    ("雷锋", "chinese soldier uniform"),
    ("张桂梅", "mountain school children"),
    ("黄文秀", "mountain village china countryside"),
    ("黄大年", "planet earth geophysics"),
    ("申纪兰", "farmland field crops"),
    ("王继才", "island lighthouse sea"),
    ("鲁迅", "chinese calligraphy brush ink"),
    ("闻一多", "red candle flame"),
    ("朱自清", "lotus pond"),
    ("老舍", "beijing hutong old street"),
    ("吴孟超", "surgery operating room"),
    ("林巧稚", "newborn baby"),
    ("詹天佑", "railway mountain train"),
]

def get(url, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=25).read()
        except Exception:
            time.sleep(2.0 * (a + 1))
    return None

def get_json(url, tries=3):
    b = get(url, tries)
    return json.loads(b) if b else {}

def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return True
    data = get(url)
    if not data or len(data) < 4000:
        return False
    with open(path, 'wb') as f:
        f.write(data)
    return True

def commons_search(term):
    q = urllib.parse.quote(term + ' filetype:bitmap')
    url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
           '&gsrsearch=%s&gsrnamespace=6&gsrlimit=10&prop=imageinfo'
           '&iiprop=url|mime&iiurlwidth=1200&format=json' % q)
    data = get_json(url)
    cands = []
    for p in data.get('query', {}).get('pages', {}).values():
        ii = p.get('imageinfo', [{}])[0]
        if ii.get('mime') in ('image/jpeg', 'image/png'):
            u = ii.get('thumburl') or ii.get('url')
            if u:
                cands.append(u)
    return cands[0] if cands else None

def portrait(name):
    for lang, base in [('zh', 'zh.wikipedia.org'), ('en', 'en.wikipedia.org')]:
        q = urllib.parse.quote(name)
        url = ('https://%s/w/api.php?action=query&titles=%s&prop=pageimages'
               '&format=json&pithumbsize=900&redirects=1' % (base, q))
        d = get_json(url)
        for p in d.get('query', {}).get('pages', {}).values():
            t = p.get('thumbnail')
            if t and t.get('source'):
                return t['source']
    # 兜底：Commons 搜名字 + 肖像
    for term in (name + ' 肖像', name):
        u = commons_search(term)
        if u:
            return u
    return None

def slug(i, kind):
    return os.path.join(OUT, '%s-%02d.jpg' % (kind, i))

result = json.load(open(JSONP, encoding='utf-8'))
for i, (name, term) in enumerate(PEOPLE):
    r = result.get(name, {})
    fixed = []
    if not r.get('portrait'):
        u = portrait(name)
        if u and download(u, slug(i, 'portrait')):
            r['portrait'] = 'images/portrait-%02d.jpg' % i
            fixed.append('肖像')
        time.sleep(2.0)
    if not r.get('bg'):
        u = commons_search(term)
        if u and download(u, slug(i, 'bg')):
            r['bg'] = 'images/bg-%02d.jpg' % i
            fixed.append('背景')
        time.sleep(2.0)
    result[name] = r
    print('[%02d] %s: %s' % (i, name, '、'.join(fixed) if fixed else '仍缺失'))

json.dump(result, open(JSONP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n最终缺失：')
for name, r in result.items():
    miss = [k for k in ('portrait', 'bg') if not r.get(k)]
    if miss:
        print('  %s: %s' % (name, '、'.join(miss)))
