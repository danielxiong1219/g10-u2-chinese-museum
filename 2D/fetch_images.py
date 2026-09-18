# -*- coding: utf-8 -*-
"""抓取 30 位人物肖像（维基百科）与专业背景图（Wikimedia Commons），存到 images/ 并写 images.json。"""
import urllib.request, urllib.parse, json, os, time

UA = {'User-Agent': 'MuseumCurationSchoolProject/1.0 (educational use)'}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
os.makedirs(OUT, exist_ok=True)

# (姓名, 背景图搜索词)
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

def get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read()

def get_json(url):
    return json.loads(get(url))

def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return True
    try:
        data = get(url)
        if len(data) < 4000:
            return False
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print("      download err", type(e).__name__)
        return False

def portrait(name):
    for lang, base in [('zh', 'zh.wikipedia.org'), ('en', 'en.wikipedia.org')]:
        try:
            q = urllib.parse.quote(name)
            url = ('https://%s/w/api.php?action=query&titles=%s&prop=pageimages'
                   '&format=json&pithumbsize=900&redirects=1' % (base, q))
            data = get_json(url)
            for p in data.get('query', {}).get('pages', {}).values():
                t = p.get('thumbnail')
                if t and t.get('source'):
                    return t['source']
        except Exception:
            continue
    return None

def background(term):
    try:
        q = urllib.parse.quote(term + ' filetype:bitmap')
        url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
               '&gsrsearch=%s&gsrnamespace=6&gsrlimit=8&prop=imageinfo'
               '&iiprop=url|mime&iiurlwidth=1400&format=json' % q)
        data = get_json(url)
        pages = data.get('query', {}).get('pages', {})
        # 优先选 jpeg/png，按标题排序取稳定结果
        candidates = []
        for p in pages.values():
            ii = p.get('imageinfo', [{}])[0]
            mime = ii.get('mime', '')
            if mime in ('image/jpeg', 'image/png'):
                u = ii.get('thumburl') or ii.get('url')
                if u:
                    candidates.append(u)
        if candidates:
            return candidates[0]
    except Exception as e:
        print("      bg search err", type(e).__name__)
    return None

def slug(i, kind):
    return os.path.join(OUT, '%s-%02d.jpg' % (kind, i))

result = {}
for i, (name, term) in enumerate(PEOPLE):
    print('[%02d] %s' % (i, name))
    p_url = portrait(name)
    b_url = background(term)
    ok_p = p_url and download(p_url, slug(i, 'portrait'))
    ok_b = b_url and download(b_url, slug(i, 'bg'))
    result[name] = {
        'portrait': ('images/portrait-%02d.jpg' % i) if ok_p else None,
        'bg': ('images/bg-%02d.jpg' % i) if ok_b else None,
        'portrait_src': p_url or '',
        'bg_src': b_url or '',
    }
    print('   肖像', 'OK' if ok_p else '缺失', '| 背景', 'OK' if ok_b else '缺失')
    time.sleep(0.3)

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images.json'), 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print('\n完成。缺失项：')
for name, r in result.items():
    miss = [k for k in ('portrait', 'bg') if not r[k]]
    if miss:
        print('  %s: %s' % (name, '、'.join(miss)))
