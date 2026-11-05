# GIF 表情包工作室

一个 Codex Skill，把角色参考图做成成套的聊天 GIF。适合吉祥物、原创角色和有清晰渲染参考图的 3D 角色。

给它一张授权使用的角色图、表情数量和使用场景。它会规划各款的台词、姿势和动效，生成角色素材，再导出透明循环 GIF、分类 ZIP 和可播放的 MP4 预览。ZIP 内含可离线打开的动图浏览页。

## 在 Codex 中使用

把仓库放进 Codex 的 Skill 目录。以下命令会把它安装到本机用户的 Skill 目录。

```sh
git clone https://github.com/WoYun520/pixel-gif-sticker-pack.git ~/.codex/skills/pixel-gif-sticker-pack
```

打开新的 Codex 对话，附上角色图后，可以这样调用。

> 使用 $pixel-gif-sticker-pack，做 16 张中文工作群表情包。保留角色的配色和标志性配饰，输出透明循环 GIF 和动态预览。

生成新姿势需要当前会话能使用图像生成工具。已有透明精灵图时，也可以直接使用下面的导出脚本。

## 从精灵图导出

需要 Python 3 和 Pillow。生成 MP4 预览还需要带有 libx264 的 FFmpeg。

1. 准备透明 PNG 精灵图，每格一个完整姿势，格间留空。
2. 按 [清单格式](references/manifest.md) 写好台词、格子位置和动效。
3. 用一款支持台词文字的本地字体导出。

```sh
python3 -m pip install Pillow
python3 scripts/export_pack.py manifest.json build --font /path/to/font.ttf --preview
```

默认导出 320 × 320 像素、约两秒一轮的透明 GIF。动效基于每款的精灵姿势，叠加位移、挤压和像素特效。脚本检查数量、重复素材、有效帧、透明度、裁边和 ZIP 完整性。

## 许可证

[MIT](LICENSE)
