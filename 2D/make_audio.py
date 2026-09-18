# -*- coding: utf-8 -*-
"""用微软 Edge 神经网络语音生成讲解音频（按人物性格配不同声线），存到 audio/ 目录。"""
import asyncio, os, re, html as htmlmod
import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(BASE, 'audio')
os.makedirs(AUDIO, exist_ok=True)

RATE = '-8%'   # 稍慢，博物馆讲解节奏

# 声线分配：女性人物用晓晓（温暖女声）；文人/楷模/医者用云健（深沉纪录片）；科学家用云扬（专业沉稳）；工匠用云希（朴实真诚）
VOICE = {
    '袁隆平':'zh-CN-YunyangNeural','张秉贵':'zh-CN-YunxiNeural','钟扬':'zh-CN-YunyangNeural',
    '高凤林':'zh-CN-YunxiNeural','钱学森':'zh-CN-YunyangNeural','邓稼先':'zh-CN-YunyangNeural',
    '屠呦呦':'zh-CN-XiaoxiaoNeural','南仁东':'zh-CN-YunyangNeural','华罗庚':'zh-CN-YunyangNeural',
    '李四光':'zh-CN-YunyangNeural','茅以升':'zh-CN-YunyangNeural','于敏':'zh-CN-YunyangNeural',
    '孙家栋':'zh-CN-YunyangNeural','王进喜':'zh-CN-YunxiNeural','时传祥':'zh-CN-YunxiNeural',
    '许振超':'zh-CN-YunxiNeural','焦裕禄':'zh-CN-YunjianNeural','雷锋':'zh-CN-YunjianNeural',
    '张桂梅':'zh-CN-XiaoxiaoNeural','黄文秀':'zh-CN-XiaoxiaoNeural','黄大年':'zh-CN-YunyangNeural',
    '申纪兰':'zh-CN-XiaoxiaoNeural','王继才':'zh-CN-YunjianNeural','鲁迅':'zh-CN-YunjianNeural',
    '闻一多':'zh-CN-YunjianNeural','朱自清':'zh-CN-YunjianNeural','老舍':'zh-CN-YunjianNeural',
    '吴孟超':'zh-CN-YunjianNeural','林巧稚':'zh-CN-XiaoxiaoNeural','詹天佑':'zh-CN-YunyangNeural',
}
MUSEUM_VOICE = 'zh-CN-YunjianNeural'

def extract_narration(fn):
    h = open(fn, encoding='utf-8').read()
    m = re.search(r'data-narration="([^"]*)"', h)
    return htmlmod.unescape(m.group(1)) if m else None

async def gen(text, path, voice):
    tts = edge_tts.Communicate(text, voice, rate=RATE)
    await tts.save(path)

async def main():
    count = 0
    intro = extract_narration(os.path.join(BASE, 'index.html'))
    if intro:
        await gen(intro, os.path.join(AUDIO, 'museum.mp3'), MUSEUM_VOICE)
        print('✓ 博物馆总介绍（云健）')
        count += 1
    for fn in sorted(os.listdir(BASE)):
        if not fn.endswith('.html') or fn in ('index.html', 'game.html'):
            continue
        name = fn[:-5]
        nar = extract_narration(os.path.join(BASE, fn))
        if not nar:
            print('⚠ 缺讲解词', name)
            continue
        voice = VOICE.get(name, 'zh-CN-YunjianNeural')
        await gen(nar, os.path.join(AUDIO, name + '.mp3'), voice)
        print('✓', name, '(' + voice.split('-')[-1].replace('Neural','') + ')')
        count += 1
        await asyncio.sleep(0.3)
    print('\n共生成 %d 段音频' % count)

asyncio.run(main())
