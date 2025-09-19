# 📱 小米钱包助手 - 本地编译指南

## 🎯 概述
本指南提供在本地环境中编译Windows EXE和Android APK文件的完整步骤。

## 💻 Windows EXE编译 (已完成)

### ✅ 使用PyInstaller（推荐）
```bash
# 安装PyInstaller
pip install pyinstaller

# 编译EXE文件
pyinstaller --onefile --windowed --name "小米钱包助手" gui.py

# 编译结果位置
# dist/小米钱包助手.exe (约65MB)
```

### 🔧 使用Flet构建
```bash
# 需要安装Visual Studio (Desktop development with C++)
flet build windows

# 编译结果位置
# build/windows/
```

## 📱 Android APK编译

### 方法1：使用在线构建服务 (推荐)

#### GitHub Actions (已配置)
1. 推送代码到GitHub仓库
2. 创建版本标签触发构建：
   ```bash
   git tag v3.0.3
   git push origin v3.0.3
   ```
3. 在GitHub Actions页面查看构建进度
4. 下载构建完成的APK文件

#### 其他在线构建服务
- **GitHub Codespaces**: 提供云端开发环境
- **Gitpod**: 自动配置的云端IDE
- **Replit**: 在线Python环境

### 方法2：本地环境配置 (复杂但完整)

#### 步骤1：安装Java开发环境
```bash
# Windows (使用Chocolatey)
choco install openjdk17

# 或手动下载安装
# https://adoptium.net/temurin/releases/
```

#### 步骤2：安装Android Studio
1. 下载Android Studio: https://developer.android.com/studio
2. 安装时选择包含Android SDK
3. 启动Android Studio，完成初始设置
4. 安装必要的SDK组件：
   - Android SDK Platform 34
   - Android SDK Build-Tools 34.0.0
   - Android SDK Platform-Tools

#### 步骤3：配置环境变量
```bash
# Windows PowerShell
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
$env:PATH += ";$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\tools\bin"

# 永久设置（系统属性 -> 高级 -> 环境变量）
ANDROID_HOME = C:\Users\YourUsername\AppData\Local\Android\Sdk
PATH += %ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools\bin
```

#### 步骤4：安装Flutter
```bash
# 下载Flutter SDK
# https://flutter.dev/docs/get-started/install/windows

# 解压到合适位置，如 C:\flutter
# 添加到PATH环境变量
PATH += C:\flutter\bin
```

#### 步骤5：验证环境
```bash
# 检查Flutter环境
flutter doctor

# 接受Android许可证
flutter doctor --android-licenses
```

#### 步骤6：编译APK
```bash
# 使用Flet编译
flet build apk --verbose

# 编译结果位置
# build/apk/app-release.apk
```

### 方法3：使用Docker容器 (推荐给有经验用户)

#### 创建Dockerfile
```dockerfile
FROM ubuntu:22.04

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl git unzip xz-utils zip libglu1-mesa \
    openjdk-17-jdk python3 python3-pip

# 安装Flutter
RUN git clone https://github.com/flutter/flutter.git /flutter
ENV PATH="/flutter/bin:$PATH"
RUN flutter doctor

# 安装Android SDK
ENV ANDROID_HOME="/android-sdk"
RUN mkdir -p $ANDROID_HOME
RUN curl -o android-sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
RUN unzip android-sdk.zip -d $ANDROID_HOME
ENV PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# 接受许可证并安装必要组件
RUN yes | sdkmanager --licenses
RUN sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

WORKDIR /app
COPY . .

# 安装Python依赖
RUN pip3 install .
RUN pip3 install flet-cli

# 构建APK
CMD ["flet", "build", "apk"]
```

#### 使用Docker构建
```bash
# 构建Docker镜像
docker build -t xiaomi-wallet-builder .

# 运行构建
docker run -v $(pwd)/build:/app/build xiaomi-wallet-builder
```

## 🚀 推荐方案

### 对于大多数用户：
1. **Windows EXE**: 使用已编译的版本 (`dist/小米钱包助手.exe`)
2. **Android APK**: 等待GitHub Actions自动构建完成

### 对于开发者：
1. **本地开发**: 配置完整的Flutter + Android开发环境
2. **CI/CD**: 使用GitHub Actions或其他云构建服务

## 📞 支持

如果遇到编译问题：
1. 检查环境变量配置
2. 确认所有依赖已正确安装
3. 查看详细错误日志
4. 考虑使用云端构建服务

## 🔧 故障排除

### 常见问题：
- **Visual Studio未安装**: Windows EXE需要C++构建工具
- **Android许可证**: 运行 `flutter doctor --android-licenses`
- **内存不足**: 增加Gradle JVM内存设置
- **网络问题**: 使用国内镜像源加速下载
