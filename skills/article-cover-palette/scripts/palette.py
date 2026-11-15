#!/usr/bin/env python3
"""查配色、计算字色、排序和填提示词。只用Python标准库，不调用生图API。"""
import argparse
import colorsys
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
NEUTRALS = ['#000000', '#FFFFFF']
ALIASES = {'AI':'科技','人工智能':'科技','软件':'科技','投资':'财经','金融':'财经','咖啡':'饮食','美食':'饮食','户外':'自然','放松':'放松','平静':'安静','理性':'冷静','高能':'兴奋','克制':'克制','上市发布':'发布','分析':'解释'}


def normalize_hex(value):
    value = str(value).strip().upper()
    if not value.startswith('#'):
        value = '#'+value
    if re.fullmatch(r'#[0-9A-F]{3}', value):
        value = '#'+''.join(c*2 for c in value[1:])
    if not re.fullmatch(r'#[0-9A-F]{6}', value):
        raise ValueError('HEX需为三位或六位色号：'+value)
    return value


def luminance(value):
    value = normalize_hex(value)
    rgb = [int(value[i:i+2],16)/255 for i in (1,3,5)]
    linear = [c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in rgb]
    return sum(c*w for c,w in zip(linear,[0.2126,0.7152,0.0722]))


def contrast(a,b):
    low,high=sorted([luminance(a),luminance(b)])
    return (high+0.05)/(low+0.05)


def pick_ink(background, colors, minimum):
    candidates=[c['hex'] if isinstance(c,dict) else c for c in colors]
    ranked=sorted(candidates,key=lambda c:contrast(c,background),reverse=True)
    ink=ranked[0]
    auxiliary=contrast(ink,background)<minimum
    if auxiliary:
        ink=max(NEUTRALS,key=lambda c:contrast(c,background))
    return {'hex':ink,'contrast':round(contrast(ink,background),3),'auxiliary':auxiliary}


def color_roles(palette, background='不限', background_hex=None):
    colors=palette['colors']
    codes=[c['hex'] for c in colors]
    base=palette.get('background_index',0)
    if background_hex:
        bg=normalize_hex(background_hex)
        if bg not in codes:
            raise ValueError('指定底色不在本组里；请改用自定义配色。')
    elif background=='浅底':
        bg=max(codes,key=luminance)
        if luminance(bg)<0.6:
            raise ValueError('本组没有足够浅的底色。')
    elif background=='深底':
        bg=min(codes,key=luminance)
        if luminance(bg)>0.2:
            raise ValueError('本组没有足够深的底色。')
    else:
        bg=codes[base]
    if (background=='浅底' and luminance(bg)<0.6) or (background=='深底' and luminance(bg)>0.2):
        raise ValueError('指定底色与浅底或深底要求冲突。')
    title=pick_ink(bg,colors,3.0)
    body=pick_ink(bg,colors,4.5)
    rest=[c for c in codes if c not in [bg,title['hex']]]
    def accent_score(code):
        rgb=[int(code[i:i+2],16)/255 for i in (1,3,5)]
        saturation=colorsys.rgb_to_hsv(*rgb)[1]
        return saturation*2+min(contrast(code,bg)/4.5,1)
    accent=max(rest,key=accent_score) if rest else next((c for c in codes if c!=bg),title['hex'])
    by_code={c['hex']:c['name'] for c in colors}
    return {'background':{'hex':bg,'name':by_code[bg]},
            'title':dict(title,name=by_code.get(title['hex'],'辅助字色'),large_only=title['contrast']<4.5),
            'body':dict(body,name=by_code.get(body['hex'],'辅助字色')),
            'accent':{'hex':accent,'name':by_code.get(accent,'点缀')},
            'swatch_inks':[dict(name=c['name'],swatch=c['hex'],**pick_ink(c['hex'],colors,4.5)) for c in colors]}


def load_catalog():
    return json.loads((ROOT/'references/catalog.json').read_text())['palettes']


def custom_palette(values,name='自定配色'):
    if not 2<=len(values)<=6:
        raise ValueError('自定义配色接收2到6个颜色。')
    colors=[{'name':v.get('name',f'颜色{i+1}'),'hex':normalize_hex(v['hex'])} if isinstance(v,dict)
            else {'name':f'颜色{i+1}','hex':normalize_hex(v)} for i,v in enumerate(values)]
    if len({c['hex'] for c in colors})!=len(colors):
        raise ValueError('自定义配色里有重复色号。')
    return {'id':None,'number':'自定','name':name,'colors':colors,'background_index':0,
            'topics':[],'moods':[],'purposes':[],'intensity':3,'preview':None}


def tags(values):
    if isinstance(values,str):
        values=[values]
    return {ALIASES.get(v,v) for v in (values or [])}


def palette_distance(a,b):
    def rgb(c):
        return [int(c['hex'][i:i+2],16)/255 for i in (1,3,5)]
    ac,bc=[rgb(c) for c in a['colors']],[rgb(c) for c in b['colors']]
    def nearest(xs,ys):
        return sum(min(math.sqrt(sum((x-y)**2 for x,y in zip(u,v))/3) for v in ys) for u in xs)/len(xs)
    return (nearest(ac,bc)+nearest(bc,ac))/2


def select_palettes(brief,limit=3):
    catalog=load_catalog()
    background=brief.get('background','不限')
    if background not in ['不限','浅底','深底']:
        raise ValueError('background使用不限、浅底或深底。')
    required={normalize_hex(c) for c in brief.get('required_colors',[])}
    excluded={normalize_hex(c) for c in brief.get('excluded_colors',[])}
    if required & excluded:
        raise ValueError('同一个色号不能同时要求保留和排除。')
    if brief.get('custom_colors') and brief.get('palette_id') is not None:
        raise ValueError('指定编号和自定义色号不能同时作为配色来源。')
    def explicit(p,reason):
        codes={c['hex'] for c in p['colors']}
        if not required<=codes or excluded&codes or (brief.get('color_count') and len(codes)!=int(brief['color_count'])):
            raise ValueError('指定配色与要求保留、排除的色号或颜色数量有冲突。')
        return [{'palette':p,'roles':color_roles(p,background,brief.get('background_hex')),'reason':[reason]}]
    if brief.get('custom_colors'):
        p=custom_palette(brief['custom_colors'],brief.get('palette_name','自定配色'))
        return explicit(p,'采用用户自定义色号。')
    if brief.get('palette_id') is not None:
        p=next((p for p in catalog if p['id']==int(brief['palette_id'])),None)
        if not p:
            raise ValueError('编号应在1—100之间。')
        return explicit(p,'采用用户指定编号，不重新排名。')
    requested_topics,requested_moods=tags(brief.get('topics')),tags(brief.get('moods'))
    if not requested_topics and not requested_moods:
        raise ValueError('先判断文章的题材或情绪，再用结构化brief查表。')
    intensity=int(brief.get('intensity',3))
    if not 1<=intensity<=5:
        raise ValueError('intensity应在1—5之间。')
    purpose=ALIASES.get(brief.get('purpose'),brief.get('purpose'))
    ranked=[]
    for p in catalog:
        codes={c['hex'] for c in p['colors']}
        if not required<=codes or excluded&codes:
            continue
        if brief.get('color_count') and len(p['colors'])!=int(brief['color_count']):
            continue
        try:
            role=color_roles(p,background,brief.get('background_hex'))
        except ValueError:
            continue
        tm=requested_topics&tags(p['topics'])
        mm=requested_moods&tags(p['moods'])
        if not tm and not mm and not required:
            continue
        topic_score=20*len(tm)/max(1,len(requested_topics))
        mood_score=35*len(mm)/max(1,len(requested_moods))
        task_score=25 if purpose and purpose in p['purposes'] else 0
        intensity_score=20*(1-abs(intensity-p['intensity'])/4)
        score=topic_score+mood_score+task_score+intensity_score
        reasons=[]
        if tm: reasons.append('题材：'+'、'.join(sorted(tm)))
        if mm: reasons.append('情绪：'+'、'.join(sorted(mm)))
        if task_score: reasons.append('适合任务：'+purpose)
        reasons.append(f'视觉强度{p["intensity"]}/5，文章目标{intensity}/5')
        ranked.append({'palette':p,'roles':role,'score':round(score,2),'reason':reasons})
    ranked.sort(key=lambda r:(-r['score'],r['palette']['id']))
    chosen=[]
    for r in ranked:
        if not any(palette_distance(r['palette'],s['palette'])<0.065 for s in chosen):
            chosen.append(r)
        if len(chosen)>=limit:
            break
    if not chosen:
        raise ValueError('原100组中没有满足硬条件的配色；请使用自定义配色或说明哪项条件可以调整。')
    return chosen


def make_prompt(palette,mode,title=None,ratio=None,width=None,scene=None,lettering=None,background=None,background_hex=None,brief=None):
    brief=brief or {}
    title=title or brief.get('title')
    background=background if background is not None else brief.get('background','不限')
    background_hex=background_hex if background_hex is not None else brief.get('background_hex')
    if background not in ['不限','浅底','深底']:
        raise ValueError('background使用不限、浅底或深底。')
    roles=color_roles(palette,background,background_hex)
    ratio=ratio or ('3:1' if mode=='palette-card' else '5:2')
    parts=ratio.split(':')
    if len(parts)!=2 or not all(p.isdigit() and int(p)>0 for p in parts):
        raise ValueError('比例写成3:1或5:2这样的形式。')
    width=width or (1200 if mode=='palette-card' else 1500)
    height=round(width*int(parts[1])/int(parts[0]))
    if width<300 or height<100:
        raise ValueError('尺寸过小，色名和色号难以阅读。')
    if mode=='article-cover' and not title:
        raise ValueError('制作文章封面需要title；只问配色可用select或show。')
    inputs=[]
    if mode=='palette-card':
        inputs.append({'path':str(ROOT/'assets/style-reference.jpg'),'role':'仅参考已经选定的窄横版式与块字，不沿用参考图的色号和文字。'})
    for path,role in [(scene,'用户场景或内容图，保留用户指定的主体和事实。'),(lettering,'用户字稿，按其字形与文字要求使用。')]:
        if path:
            path=Path(path).expanduser().resolve()
            if not path.is_file(): raise ValueError('找不到用户素材：'+str(path))
            if path.suffix.lower() not in ['.png','.jpg','.jpeg','.webp']:
                raise ValueError('图片参数接收PNG/JPG/WebP；字体文件先由当前排版工具处理。')
            inputs.append({'path':str(path),'role':role})
    lines=[]
    for c,ink in zip(palette['colors'],roles['swatch_inks']):
        line=f'{c["name"]} {c["hex"]}'
        if mode=='palette-card':
            line+=f'；此色块文字用 {ink["hex"]}。字色只用于读字，不新增配色色块或色号标签。'
        lines.append(line)
    ratio_note='未指定固定用色比例，按主底、次色与小面积点缀安排。'
    if palette.get('source_usage_ratio'):
        if roles['background']['hex']==palette['colors'][0]['hex']:
            ratio_note='原清单建议6:3:1，按以上原色顺序安排封面大致面积；色卡为读色号保留足够宽度。'
        else:
            ratio_note='原清单建议6:3:1，但本次已明确更换底色，封面面积以当前角色分工安排；色卡保留读字空间。'
    preserve=brief.get('preserve',[])
    if isinstance(preserve,str):
        preserve=[preserve]
    values={'number':palette['number'],'palette_name':palette['name'],'title':json.dumps(title or palette['name'],ensure_ascii=False),
            'ratio':ratio,'width':str(width),'height':str(height),'color_count':str(len(palette['colors'])),
            'color_lines':'\n'.join(lines),'background_hex':roles['background']['hex'],'title_hex':roles['title']['hex'],
            'body_hex':roles['body']['hex'],'accent_hex':roles['accent']['hex'],'ratio_note':ratio_note,
            'article_summary':brief.get('article_summary','只提供了标题，按标题作暂定构思，不声称已读全文。'),
            'article_message':brief.get('message','围绕给定标题，不自加结论。'),
            'article_moods':'、'.join(brief.get('moods',palette.get('moods',[]))),
            'article_purpose':brief.get('purpose','按标题与用户要求判断'),
            'visual_direction':brief.get('visual_direction','根据文章用途选择版式、字体和材料；沿用用户已选的风格。'),
            'visual_subject':brief.get('visual_subject','用一个与核心落点有关的主体或视觉关系，不用无关小图标填空。'),
            'palette_scope':brief.get('palette_scope','可调整的底面、标题字、关键词衬底与少量点缀；照片、人物肤色、产品实色与数据图例保留。'),
            'preserve_requirements':'；'.join(preserve) or '保留用户标题、已定素材、字形与尺寸要求。',
            'title_note':'标题字色对比只适合大字；缩到390px宽时标题保持至少28px，小字另用正文色。' if roles['title']['large_only'] else '标题与背景对比足够；仍需检查用户照片里实际落字的位置。',
            'user_assets':'\n'.join(f'{i["path"]}：{i["role"]}' for i in inputs if i['path']!=str(ROOT/'assets/style-reference.jpg')) or ('没有额外素材，按以上配色色块与文字制作。' if mode=='palette-card' else '没有用户素材，可用主题物件、图解或色块，不强行加人物。')}
    template=(ROOT/f'templates/{mode}.md').read_text()
    variables=set(re.findall(r'\{\{(\w+)\}\}',template))
    missing=variables-values.keys()
    if missing: raise ValueError('模板变量缺失：'+','.join(sorted(missing)))
    template=re.sub(r'\{\{(\w+)\}\}',lambda match:values[match.group(1)],template)
    return {'prepared_only':True,'mode':mode,'palette_id':palette['id'],'palette_name':palette['name'],
            'target_size':[width,height],'ratio':ratio,'roles':roles,'input_images':inputs,'prompt':template}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    show=sub.add_parser('show');show.add_argument('id',type=int)
    sub.add_parser('vocabulary')
    select=sub.add_parser('select');select.add_argument('--brief',required=True);select.add_argument('--limit',type=int,default=3)
    prompt=sub.add_parser('prompt')
    source=prompt.add_mutually_exclusive_group(required=True)
    source.add_argument('--id',type=int);source.add_argument('--custom',nargs='+')
    prompt.add_argument('--name',default='自定配色');prompt.add_argument('--mode',choices=['palette-card','article-cover'],default='palette-card')
    prompt.add_argument('--title');prompt.add_argument('--ratio');prompt.add_argument('--width',type=int)
    prompt.add_argument('--scene');prompt.add_argument('--lettering');prompt.add_argument('--background',choices=['不限','浅底','深底'])
    prompt.add_argument('--background-hex');prompt.add_argument('--out')
    prompt.add_argument('--brief')
    args=parser.parse_args()
    try:
        if args.command=='vocabulary':
            catalog=load_catalog()
            result={key:sorted({v for p in catalog for v in p[key]}) for key in ['topics','moods','purposes']}
        elif args.command=='show':
            p=next((p for p in load_catalog() if p['id']==args.id),None)
            if p is None: raise ValueError('编号应在1—100之间。')
            result={'palette':p,'roles':color_roles(p),'preview':str(ROOT/p['preview'])}
        elif args.command=='select':
            if not 1<=args.limit<=10: raise ValueError('limit应在1—10之间。')
            brief=json.loads(Path(args.brief).read_text())
            result={'article_summary':brief.get('article_summary'),'message':brief.get('message'),
                    'recommendations':select_palettes(brief,args.limit),'note':'按助手提炼的题材、情绪和任务排序，不代表脚本已经阅读或验证全文。'}
        else:
            if args.custom:
                p=custom_palette(args.custom,args.name)
            else:
                p=next((p for p in load_catalog() if p['id']==args.id),None)
                if p is None: raise ValueError('编号应在1—100之间。')
            brief=json.loads(Path(args.brief).read_text()) if args.brief else None
            result=make_prompt(p,args.mode,args.title,args.ratio,args.width,args.scene,args.lettering,args.background,args.background_hex,brief)
            if args.out:
                out=Path(args.out).expanduser();out.mkdir(parents=True,exist_ok=True)
                (out/'prompt.txt').write_text(result['prompt'])
                (out/'plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
                result['saved_to']=str(out.resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError,json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__=='__main__':
    main()
