# 生成应用图标

由于需要图形工具生成图标，请使用以下方法之一：

## 方法1: 在线转换工具
1. 访问 https://convertico.com/
2. 上传一个聊天图标PNG图片
3. 下载生成的 .ico 文件
4. 重命名为 icon.ico 放到 electron 目录

## 方法2: 使用现有图标
可以从以下网站下载免费图标：
- https://www.flaticon.com/
- https://icons8.com/

搜索 "chat" 或 "message" 相关图标

## 方法3: 使用默认图标
electron-builder 会使用默认图标，但建议自定义

## 图标规格
- Windows: .ico 格式，256x256 像素
- macOS: .icns 格式，512x512 像素
- Linux: .png 格式，512x512 像素