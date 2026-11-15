# 查表与填模板

命令里的 `<skill>` 换成当前 Skill 的实际目录。脚本只用Python标准库，不调用付费API、不下载字体，也不直接生图。

## 按文章选

先由助手读文章，再生成 brief。例如：

```json
{
  "article_summary": "拆解一款软件的成本构成与使用限制",
  "message": "帮助读者理解取舍，不是庆祝发布",
  "topics": ["科技", "商业"],
  "moods": ["冷静", "克制"],
  "purpose": "解释",
  "intensity": 2,
  "background": "不限"
}
```

```text
python3 <skill>/scripts/palette.py vocabulary
python3 <skill>/scripts/palette.py select --brief brief.json --limit 3
python3 <skill>/scripts/palette.py show 65
```

可选约束：`palette_id`指定编号；`required_colors`和`excluded_colors`接HEX列表；`color_count`指定原配色数量；`background`接“浅底”“深底”“不限”。`background_hex`必须属于原组。没有满足条件的组合时明确返回，不能把未满足条件的组当成命中。

`custom_colors`接2—6个HEX，或接带`name`与`hex`的对象列表；`palette_name`可自定。自定义不混进原100组。

使用返回的`roles`作为本次搭法；目录里的`default_roles`只是默认搭法，不能覆盖用户要求的浅底或深底。

## 填出图模板

```text
python3 <skill>/scripts/palette.py prompt --id 30 --mode palette-card --out card-030
python3 <skill>/scripts/palette.py prompt --id 65 --mode article-cover --title "从营收到利润，还差哪一步" --brief brief.json --out cover-065
python3 <skill>/scripts/palette.py prompt --custom "#003049" "#FDF0D5" "#D62828" --name "我的配色" --mode article-cover --title "用户的标题" --scene scene.jpg --lettering title.png --out custom-cover
```

可用`--ratio 16:9`、`--width 1600`改画幅；`--background 浅底`或`--background-hex "#F0F4F8"`改底色。底色优先采用命令行明确给出的值，未给时沿用brief里的`background`和`background_hex`，再没有时才用目录默认值。

输出`prompt.txt`与`plan.json`。`prepared_only: true`表示只准备了提示词，助手仍需调用当前可用的画图工具。`input_images`写明哪些文件要先查看，以及传入生图工具时各自的用途。

文章封面可用`--brief brief.json`带入摘要、核心落点、目的和情绪。只给标题时会标明是暂定构思，不把标题猜测说成全文分析。

同一份brief还可以写清画面和保留范围：

```json
{
  "article_summary": "整理六个适合独立开发者使用的开源工具",
  "message": "帮助读者找到能直接开始试的工具",
  "topics": ["科技", "效率"],
  "moods": ["明快"],
  "purpose": "分享",
  "intensity": 3,
  "background": "深底",
  "visual_direction": "简洁的资源目录封面，标题有层次，装饰克制",
  "visual_subject": "六本同一系列的小册子围绕一个清楚的取书动作",
  "palette_scope": "背景、书脊、标题与关键词底条；截图原色保留",
  "preserve": ["标题完整", "沿用用户字体", "不加虚拟人物"]
}
```

这些字段会进入封面提示词。若决定保留原有配色，直接沿原图或原方案继续制作；不用为了运行脚本而虚选一个编号。

用户字稿参数接图片。TTF/OTF字体文件由当前排版工具处理，不把字体文件当图片传给生图工具。用户指定的字形与排版要求写进提示词；不要因为色卡参考是块字就覆盖它。

## 更新表格

只维护`references/catalog.json`，再同时导出阅读表、CSV和色卡图表：

```text
python3 <skill>/scripts/export_table.py --csv <skill>/references/palette-table.csv --cards <skill>/references/color-cards.md
```

图表按001—100排序，引用本包里的100张JPG，十张一组。HTML、ZIP或个人路径不属于Skill运行所需文件。
