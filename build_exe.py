#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小米钱包GUI应用打包脚本
使用PyInstaller将应用打包成单文件exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_exe():
    """构建exe文件"""
    print("🚀 开始构建小米钱包GUI应用...")
    
    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 清理之前的构建
    for clean_dir in ['build', 'dist', '__pycache__']:
        if os.path.exists(clean_dir):
            print(f"🧹 清理目录: {clean_dir}")
            shutil.rmtree(clean_dir)
    
    # 删除旧的spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        print(f"🧹 删除旧的spec文件: {spec_file}")
        spec_file.unlink()
    
    # 检查图标文件是否存在
    icon_file = 'xiaomi_wallet.ico'
    if not os.path.exists(icon_file):
        print("⚠️ 图标文件不存在，正在创建...")
        # 如果图标不存在，先创建
        try:
            import create_icon
            create_icon.create_xiaomi_icon()
            print("✅ 图标创建成功!")
        except Exception as e:
            print(f"❌ 图标创建失败: {e}")
            icon_file = 'NONE'
    
    # PyInstaller命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 打包成单个exe文件
        '--windowed',                   # 不显示控制台窗口
        '--name=小米钱包GUI',           # 指定exe文件名
        f'--icon={icon_file}',          # 使用生成的图标
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不询问确认
        '--add-data=xiaomiconfig.json;.',  # 包含配置文件（如果存在）
        'gui.py'                        # 主程序文件
    ]
    
    print("📦 执行PyInstaller命令...")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("✅ 构建成功!")
        print(f"输出:\n{result.stdout}")
        
        # 检查输出文件
        exe_path = Path('dist/小米钱包GUI.exe')
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📄 生成的exe文件: {exe_path}")
            print(f"📊 文件大小: {file_size:.2f} MB")
            
            # 创建运行说明
            readme_content = """# 小米钱包GUI应用使用说明

## 文件说明
- 小米钱包GUI.exe: 主程序，双击运行
- xiaomiconfig.json: 配置文件（如果存在），包含账号信息
- task_logs/: 任务日志目录（运行后自动创建）

## 使用方法
1. 双击 小米钱包GUI.exe 启动程序
2. 首次运行选择登录方式：
   - QR码登录：扫码获取Cookie
   - Cookie登录：直接输入passToken和userId
3. 添加账号后，点击"执行所有任务"开始自动化
4. 可在"会员兑换配置"中设置自动兑换规则

## 注意事项
- 请确保网络连接正常
- 首次运行可能被杀毒软件拦截，请添加信任
- 配置文件会自动保存账号信息
- 任务日志保存在task_logs目录中

## 版本信息
构建时间: {build_time}
基于: Python + Flet + 小米钱包3.0API
"""
            
            from datetime import datetime
            readme_path = Path('dist/使用说明.txt')
            readme_path.write_text(
                readme_content.format(build_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                encoding='utf-8'
            )
            print(f"📝 创建使用说明: {readme_path}")
            
            # 复制配置文件（如果存在）
            config_file = Path('xiaomiconfig.json')
            if config_file.exists():
                dest_config = Path('dist/xiaomiconfig.json')
                shutil.copy2(config_file, dest_config)
                print(f"📋 复制配置文件: {dest_config}")
            
            print(f"\n🎉 构建完成! exe文件位于: {exe_path.absolute()}")
            print("💡 可以将dist目录中的所有文件一起分发")
            
        else:
            print("❌ 未找到生成的exe文件")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败!")
        print(f"错误输出:\n{e.stderr}")
        print(f"标准输出:\n{e.stdout}")
    except Exception as e:
        print(f"❌ 构建过程中发生异常: {e}")

if __name__ == "__main__":
    build_exe()
