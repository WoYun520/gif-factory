# 制作来源与许可

**本片由 Codex 调用 [Lemo-Opuscar by Lemomo（LemoLab）](https://github.com/lemomo-ai/lemo-opuscar) 的 `lemo-opuscar` Skill 制作。** 使用其分色机械图解（Color-Coded Mechanism）风格，复用其渐开线齿形、描边代码及材质与剖面渲染方法。

## Lemo-Opuscar 的贡献

制作时使用的上游版本：[`3a7132b996be0241c1ea0ab180d519f06e6f10b6`](https://github.com/lemomo-ai/lemo-opuscar/tree/3a7132b996be0241c1ea0ab180d519f06e6f10b6)。

- [`lemo-opuscar` Skill](https://github.com/lemomo-ai/lemo-opuscar/tree/main/plugin/skills/lemo-opuscar)：制作工作流入口，实际被调用。
- [`gears.js`](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/styles/precise-mechanism/demo/gears.js)：渐开线齿廓与几何辅助方法，用于本期自行布局的20/40及18/36齿轮。
- [`film-outline.js`](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/styles/precise-mechanism/demo/film-outline.js)：同色轮廓渲染。
- [`film.js`](https://github.com/lemomo-ai/lemo-opuscar/blob/3a7132b996be0241c1ea0ab180d519f06e6f10b6/styles/precise-mechanism/demo/film.js)：软分层材质与剖面渲染方法，经本期工程适配。

代码版权属于 Lemomo（LemoLab），按 MIT 使用，制作来源记录保留[原始MIT文本](LEMO-MIT.txt)。上游 Skill 和风格等Markdown文档按CC BY-NC 4.0及其额外授权处理，具体见[上游LICENSE](https://github.com/lemomo-ai/lemo-opuscar/blob/main/LICENSE)；本仓库的MIT不替代上游许可。本目录没有分发上游样片、风格文档或完整运行时。

## 本期新增内容

两级减速箱的布局与建模参数、中文讲解稿、镜头路径、输入轴时钟与联动时序、字幕排版、原创程序配乐和机械音效编排由本项目定制。成片画面由代码渲染，没有使用同行原片或上游钟表样片。Three.js为MIT；原理来源与教学模型范围见[FACTS](FACTS.md)。

## 配音、音乐与字体

- 配音：微软[Clipchamp](https://app.clipchamp.com/)在线文字转语音，`Yunjie Dragon HD Flash Latest`，中文普通话、默认音调、1倍速。云杰是本期选择，其他使用者可按自己的偏好选择。服务条款适用；本仓库不提供离线声音模型或免费API，也不分发独立配音音轨。
- 配乐与拟音：本期原创程序合成的拨弦、敲击音、开盖气声、剖切声和齿频点击；没有使用第三方成品音乐。
- 字体：[Noto Sans CJK SC](https://github.com/notofonts/noto-cjk)，SIL Open Font License 1.1。公开媒体中为已渲染文字，不附字体二进制。
- `preview.gif`从本期完整视频8.3–11.3、19–21.5、32–34、44–46秒提取，480×270、10fps、静音循环；封面来自本期47秒画面。5秒小样也是本项目调用上述Skill后制作的独立教学齿轮箱。

本仓库原创说明、模型及数据记录按[仓库MIT](../../../LICENSE)提供；第三方代码、文档、字体和声音服务各按其来源处理。

## 可用于发布说明的署名

> 本片使用 Lemo-Opuscar by Lemomo（LemoLab）的 lemo-opuscar Skill 制作，采用分色机械图解风格，并复用部分齿形与渲染代码；内容、齿轮箱布局、镜头和运动时序为本期定制。上游：https://github.com/lemomo-ai/lemo-opuscar 。配音：Microsoft Clipchamp，云杰HD。
