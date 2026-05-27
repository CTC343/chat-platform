# 🖥️ Windows桌面版打包指南

## 方案一：便携版（已提供，直接使用）

直接运行 `聊天平台-启动.bat`，会自动：
- 检查并安装Python环境
- 启动后端服务器
- 自动打开浏览器

**优点**：无需安装，双击即用

---

## 方案二：Electron打包（推荐）

### 前置要求
- Node.js 18+
- Windows 10/11

### 打包步骤

1. **在Windows上安装Node.js**
   - 下载：https://nodejs.org/
   - 安装时勾选"Add to PATH"

2. **打开命令提示符（CMD）**

3. **执行打包命令**
```cmd
# 进入electron目录
cd D:\聊天项目\electron

# 安装依赖
npm install

# 安装打包工具
npm install electron-builder --save-dev

# 打包Windows版本
npm run build:win
```

4. **获取打包文件**
   - 打包完成后，在 `electron\dist` 目录
   - 会生成 `聊天平台 Setup 1.0.0.exe` 安装包

---

## 方案三：使用Electron Forge

```cmd
# 安装Electron Forge
npm install -g @electron-forge/cli

# 进入项目目录
cd D:\聊天项目\electron

# 初始化
npx electron-forge import

# 打包
npx electron-forge make
```

---

## 方案四：在线打包服务

### Electron Builder在线版
1. 访问 https://www.electron.build/
2. 按照文档配置
3. 使用GitHub Actions自动打包

---

## Electron项目配置

### package.json（已配置好）
```json
{
  "name": "chat-desktop",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build:win": "electron-builder --win"
  },
  "build": {
    "appId": "com.chat.desktop",
    "productName": "聊天平台",
    "win": {
      "target": "nsis",
      "icon": "icon.ico"
    }
  }
}
```

### 打包配置说明

| 配置项 | 说明 |
|--------|------|
| appId | 应用唯一标识 |
| productName | 显示名称 |
| win.target | 打包类型（nsis=安装包） |
| win.icon | 应用图标（.ico格式） |

---

## 自定义图标

### 创建ICO图标
1. 准备256x256的PNG图片
2. 访问 https://convertico.com/
3. 转换为ICO格式
4. 保存为 `electron/icon.ico`

---

## 打包优化

### 减小包体积
```json
{
  "build": {
    "files": [
      "main.js",
      "preload.js",
      "index.html",
      "package.json"
    ],
    "compression": "maximum"
  }
}
```

### 自动更新配置
```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-username",
      "repo": "chat-app"
    }
  }
}
```

---

## 常见问题

### Q: 打包后无法连接服务器？
A: 检查防火墙设置，确保端口8000开放

### Q: 打包失败？
A: 确保Node.js版本18+，并以管理员身份运行CMD

### Q: 如何修改服务器地址？
A: 编辑 `electron/index.html` 中的默认地址

---

## 推荐方案

| 方案 | 难度 | 推荐度 | 说明 |
|------|------|--------|------|
| 便携版 | ⭐ | ⭐⭐⭐⭐ | 最简单，直接用 |
| Electron | ⭐⭐ | ⭐⭐⭐⭐⭐ | 标准桌面应用 |
| Electron Forge | ⭐⭐⭐ | ⭐⭐⭐ | 功能更全 |