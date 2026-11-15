# 来源与复用

本例从自己制作的吸管与铜管五秒同屏实验扩展。铜管装置、纵缝、磁铁、释放机构、局部透视、磁场与电流讲解、受力与能量图、统一模型、镜头、字幕、轻配乐和拟音由本项目编写。

**没有调用 lemo-opuscar Skill，没有复用其风格文档、场景、着色器、示例代码或渲染/音频工具。** 仓库里的[齿轮剖面案例](../gear-reduction-cutaway/CREDITS.md)属于另一条实际调用上游 Skill 的流程，其来源说明继续保留。

## 通用依赖

- Three.js 0.170.0及官方RoomEnvironment：通用三维库，[MIT](https://github.com/mrdoob/three.js/blob/r170/LICENSE)。源码通过npm安装，不在本案例重复分发运行库。
- Noto Sans CJK SC：正式成片使用的中文字体，SIL Open Font License 1.1，见[Noto CJK](https://github.com/notofonts/noto-cjk)。本案例不分发字体二进制；公开画面源码使用中文系统字体栈。
- Python、NumPy与FFmpeg：模型辅助、原创拨弦/落物合成、混音、编码与预览裁切。没有使用第三方音乐录音、乐器采样、同行视频音轨或生成视频模型。

## 声音

完整片的正式旁白通过微软Clipchamp网页生成并导出，用户选择 `Yunjie Dragon HD Flash Latest`、中文普通话、默认音调、1倍速。不是Edge TTS普通同名声线，没有克隆真人。

原始旁白和音色模型不随源码发布，也不把网页功能描述为离线模型或公开免费API。需要改稿或换声时，按用户当前选择、服务可用性与授权重新生成，并更新时轴。微软说明见[文字转语音](https://support.microsoft.com/en-us/clipchamp/how-to-use-the-text-to-speech-feature)。

背景为本项目合成的轻拨弦音色，拟音为夹爪释放和磁铁落入软垫；没有电磁声学仿真或电流嗡鸣。公开GIF没有声音。铜管和吸管五秒小样只有轻拟音，没有旁白。

## 原理资料与许可边界

参考[FACTS](FACTS.md)所列高校原理资料，只使用事实与机制，没有使用其中的图片、视频、模型或声音。

本例原创说明、数据与三维源码按仓库[MIT](../../../LICENSE)提供。通用软件、字体和微软在线声音仍按各自来源处理，仓库许可不转授第三方音色模型或服务权限。没有本机账号、Cookie、访问令牌、私有接口地址或原始配音缓存。

正片、封面与两个五秒小样保留既有交付版本；预览GIF和四格参考图由正片缩放/裁切制作，不是新增物理验收或新的用户评价。
