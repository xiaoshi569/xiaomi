# 小米钱包每日任务多平台应用

[![Build Status](https://github.com/kai648846760/xiaomiwallet/actions/workflows/build-app.yml/badge.svg)](https://github.com/kai648846760/xiaomiwallet/actions/workflows/build-app.yml)

## 🚨 **<span style="color:red">重要警告</span>** 🚨

### **<span style="color:red; font-weight:bold">⚠️ 强烈建议仅使用本地GUI程序！</span>**

**<span style="color:red; font-weight:bold">❌ 不再推荐使用GitHub Actions或其他服务器自动化方式运行此程序，这会导致小米账号异常或被封禁！</span>**

**✅ 推荐使用方式：**
- **GUI本地运行**：下载桌面版或移动版应用，在本地设备上运行
- **降低封号风险**：本地IP环境更安全，避免服务器IP被识别为异常
- **完全可控**：可以随时停止、调整执行频率和时间

---

基于Flet框架开发的跨平台小米钱包每日任务应用，支持以下平台：

📱 **移动端**: Android APK、iOS IPA
💻 **桌面端**: Windows、macOS

通过本地GUI程序，你可以安全、便捷地实现小米钱包每日任务的自动化管理。

## 📥 应用下载与使用

**🚨 强烈建议使用本地GUI程序，这是最安全、最简单的方式！**

### 页面展示
<img width="1600" height="1256" alt="image" src="https://github.com/user-attachments/assets/f3d2e736-3ea1-4ea7-bbd4-4ee2634ded37" />
<img width="1600" height="1256" alt="image" src="https://github.com/user-attachments/assets/a3f04cac-bba2-41bb-80c6-d361d77f0149" />
<img width="1600" height="1256" alt="image" src="https://github.com/user-attachments/assets/75401ded-e818-4e9a-bbd6-001e068313c3" />



### 📱 移动端下载

从 [Releases页面](https://github.com/kai648846760/xiaomiwallet/releases) 下载移动端版本：

- **Android**: `xiaomi-wallet-gui-android.zip` - 解压后安装 `.apk` 文件
- **iOS**: `xiaomi-wallet-gui-ios.zip` - 解压后通过Xcode或TestFlight安装 `.ipa` 文件

### 💻 桌面端下载

从 [Releases页面](https://github.com/kai648846760/xiaomiwallet/releases) 下载桌面端版本：

- **Windows**: `xiaomi-wallet-gui-windows.zip` - 解压后运行可执行文件
- **macOS**: `xiaomi-wallet-gui-macos.tar.gz` - 解压后运行 `.app` 文件

### 🚀 使用步骤

1. **选择平台**：根据您的设备选择对应版本下载
2. **安装应用**：
   - 移动端：安装APK/IPA文件
   - 桌面端：解压后直接运行
3. **添加账号**：点击"扫码登录"标签页，扫描二维码登录小米账号
4. **配置兑换**（可选）：在"会员兑换"标签页为账号配置自动兑换的会员类型和手机号
5. **执行任务**：在"主页面"点击"一键运行所有任务"开始自动执行
6. **查看结果**：在"运行结果"标签页查看任务执行结果和历史记录

### 📺 会员兑换功能

**支持的会员类型：**
- 腾讯视频VIP月卡（31天）
- 爱奇艺黄金会员月卡（31天）
- 优酷VIP会员月卡（31天）
- 芒果TV会员月卡（31天）

**使用方法：**
1. 在"会员兑换"标签页选择账号
2. 选择要兑换的会员类型
3. 输入接收会员的手机号（11位数字）
4. 点击"添加兑换配置"
5. 当账号天数≥31天时，执行任务时会自动兑换

**兑换条件：**
- 账号可兑换天数≥31天
- 会员有库存且当日可兑换
- 配置的手机号格式正确

### 🚀 从源码运行

如果你想从源码运行或进行开发：

```bash
# 克隆项目
git clone https://github.com/kai648846760/xiaomiwallet.git
cd xiaomiwallet

# 安装依赖
pip install flet requests qrcode urllib3
# 或使用 uv: uv sync

# 运行应用
flet run gui.py

# 或者运行Web版本
flet run gui.py --web
```

#### 构建Web/PWA版本

如果你想构建Web/PWA版本，可以使用以下命令：

```bash
# 安装flet-cli
pip install flet-cli

# 构建Web/PWA应用
flet publish gui.py --app-name "小米钱包助手" --app-short-name "小米钱包" --app-description "小米钱包每日任务自动化助手" --pwa-background-color "#ffffff" --pwa-theme-color "#FF6700" --distpath build/web
```

构建完成后，可以在`build/web`目录中找到构建产物。将这些文件部署到Web服务器或直接在浏览器中打开`index.html`文件即可使用Web版本。在支持PWA的浏览器中（如Chrome、Edge），可以点击地址栏中的安装按钮将应用安装到桌面或移动设备。

## 🌟 项目特色

### 🚀 多平台支持

* **📱 移动端原生体验**：Android APK和iOS IPA，随时随地管理任务
* **💻 桌面端完整功能**：Windows、macOS桌面应用，已修复Windows编码问题

### 🎯 核心功能

* **🎨 统一用户界面**：基于Flet框架的跨平台一致性体验
* **👥 多账号管理**：可视化添加、删除和管理多个小米账号
* **📱 扫码登录**：内置二维码生成，手机扫码即可完成账号添加
* **⚡ 实时执行**：一键执行所有账号任务，实时显示执行进度
* **📊 结果查看**：详细的任务执行记录和结果展示
* **🔄 自动刷新**：执行记录按时间倒序显示，最新结果一目了然
* **💾 数据同步**：跨平台配置文件同步
* **📺 会员兑换**：支持自动兑换腾讯视频、爱奇艺、优酷、芒果TV等会员
* **🎯 新手任务**：自动执行应用下载试用任务，获取额外奖励

### 🔧 技术优势

* **🏗️ 现代架构**：基于Flet框架，Python后端 + Flutter前端
* **📦 一键构建**：支持所有平台的自动化构建和发布
* **🔐 安全可靠**：账号凭证仅存储在您的本地设备上，不会上传到任何服务器
* **⚡ 一键操作**：简单直观的用户界面，点击即可完成所有任务
* **📊 结果展示**：详细的任务执行记录和结果展示

## ⚙️ GUI程序工作原理

1. **本地运行**：GUI程序在您的本地设备上运行，所有操作都在本地完成
2. **扫码登录**：程序生成二维码，您使用手机小米社区/App扫码登录
3. **凭证存储**：登录凭证安全地存储在您的本地设备上
4. **任务执行**：点击执行按钮，程序在本地执行所有任务
5. **结果展示**：实时显示任务执行进度和结果

## 🚨 重要安全提示

- 账号凭证仅存储在您的本地设备上
- 程序不会上传您的任何个人信息
- 请确保从官方GitHub Releases页面下载应用程序
- 定期更新应用以获取最新功能和安全修复

## 🔧 配置说明

GUI程序会在您的本地设备上自动管理配置文件。一般情况下，您无需手动编辑配置文件。

### 📁 配置文件位置
- Windows：`%APPDATA%\xiaomiwallet\xiaomiconfig.json`
- macOS：`~/Library/Application Support/xiaomiwallet/xiaomiconfig.json`
- Android/iOS：应用私有目录
- 源码运行：项目根目录下的`xiaomiconfig.json`

### 📄 配置文件格式（v3.0）

```json
[
  {
    "data": {
      "us": "账号别名",
      "userId": "小米用户ID",
      "passToken": "登录凭证",
      "securityToken": "安全令牌",
      "exchange_configs": [
        {
          "type": "腾讯视频",
          "phone": "18888888888"
        },
        {
          "type": "爱奇艺",
          "phone": "18888888889"
        }
      ],
      "log": "最近一次执行日志"
    }
  }
]
```

**新增字段说明：**
- `exchange_configs`: 会员兑换配置数组
  - `type`: 会员类型（腾讯视频、爱奇艺、优酷、芒果TV）
  - `phone`: 接收会员的手机号

## ❓ 常见问题 (FAQ)

* **Q: 任务执行失败，显示认证错误怎么办？**

  * **A:** 这意味着你的账号登录凭证已过期。解决方案：只需在GUI程序中重新添加账号即可。

* **Q: 应用无法打开或运行怎么办？**

  * **A:** 请确保您下载了与您设备匹配的版本，并检查系统是否满足最低要求（Python 3.11+）。

* **Q: 项目是安全的吗？我的账号信息会泄露吗？**

  * **A:** 是的，GUI程序是安全的。您的账号凭证仅存储在您自己的设备上，不会上传到任何服务器。代码完全开源，您可以审查每一行。

* **Q: 会员兑换功能如何使用？**

  * **A:** 在"会员兑换"标签页为账号配置兑换类型和手机号，当账号天数≥31天时会自动兑换。兑换成功后会发送到指定手机号。

* **Q: 为什么兑换失败？**

  * **A:** 可能的原因：1）天数不足31天；2）当日库存不足；3）手机号格式错误；4）小米接口变化。请检查配置或手动在小米钱包中兑换。

* **Q: 新手任务是什么？**

  * **A:** 应用下载试用任务，可以获得额外的视频会员天数奖励。程序会自动尝试完成这个任务。

* **Q: 如何从旧版本升级？**

  * **A:** 直接使用新版本即可，配置文件会自动兼容。新功能（会员兑换）需要重新配置。



## 🔨 开发者信息

### 🏗️ 多平台自动构建系统

本项目使用GitHub Actions + Flet构建系统，支持多平台的自动化构建：

- **🚀 自动触发**：推送标签时自动构建所有平台版本
- **🎯 手动触发**：在Actions页面手动触发构建
- **📱 支持平台**：Windows、macOS、Android、iOS（已修复Windows编码问题）
- **🛠️ 构建工具**：Flet + Flutter SDK + 平台特定工具链

### 📦 构建架构

- **桌面端**：使用Flet构建原生应用（Windows、macOS）
- **移动端**：生成APK和IPA文件（Android、iOS）
- **依赖管理**：基于pyproject.toml的现代Python项目结构

### 🚀 发布新版本

要发布新版本，请按以下步骤操作：

```bash
# 1. 更新版本号（在pyproject.toml中）
# 2. 提交更改
git add .
git commit -m "Release v1.0.0"

# 3. 创建并推送标签
git tag v1.0.0
git push origin v1.0.0

# 4. GitHub Actions会自动构建所有平台并创建Release
```

### 🛠️ 本地构建

#### 安装构建环境

```bash
# 安装Flet和依赖
pip install flet requests qrcode urllib3

# 安装Flutter SDK（构建移动端需要）
# 参考：https://flutter.dev/docs/get-started/install
```

#### 构建不同平台

```bash
# 构建桌面应用
flet build windows    # Windows（已修复编码问题）
flet build macos      # macOS

# 构建移动应用
flet build apk        # Android APK
flet build aab        # Android App Bundle
flet build ipa        # iOS (需要macOS)

# 构建结果在 build/ 目录
```

## 📜 免责声明

本项目仅用于个人学习和技术研究，请在遵守相关法律法规的前提下使用。

由于小米官方接口可能随时发生变化，本项目不保证其功能的长期可用性。

用户在使用本项目时，应自行承担因使用不当或项目失效等原因可能造成的任何风险和损失。


## ⭐ Star 支持 

如果这个项目对您有帮助，请给一个 ⭐ Star 以表示支持！您的支持是我们持续改进的动力。 

[![Star History Chart](https://api.star-history.com/svg?repos=kai648846760/xiaomiwallet&type=Date)](https://star-history.com/#kai648846760/xiaomiwallet&Date) 

--- 

<div align="center"> 
  <strong>📱 小米钱包助手 - 让任务管理更便捷</strong><br> 
  <em>Powered by Loki Wang</em> 
</div>
