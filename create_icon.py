#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建小米钱包应用图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_xiaomi_icon():
    """创建小米钱包主题的图标"""
    print("🎨 开始创建应用图标...")
    
    # 创建多个尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 小米橙色主题
        xiaomi_orange = (255, 103, 0)  # 小米橙色
        white = (255, 255, 255)
        
        # 绘制圆形背景
        margin = max(2, size // 16)
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=xiaomi_orange, outline=white, width=max(1, size//32))
        
        # 绘制钱包图标
        center_x, center_y = size // 2, size // 2
        
        if size >= 32:
            # 绘制钱包形状
            wallet_size = size // 3
            wallet_left = center_x - wallet_size // 2
            wallet_top = center_y - wallet_size // 2
            wallet_right = center_x + wallet_size // 2
            wallet_bottom = center_y + wallet_size // 2
            
            # 钱包主体
            draw.rectangle([wallet_left, wallet_top, wallet_right, wallet_bottom], 
                         fill=white, outline=white)
            
            # 钱包折痕
            fold_y = wallet_top + wallet_size // 4
            draw.line([wallet_left, fold_y, wallet_right, fold_y], 
                     fill=xiaomi_orange, width=max(1, size//64))
            
            # 钱包扣子
            button_size = max(2, size // 24)
            button_x = wallet_right - button_size - max(2, size//32)
            button_y = fold_y - button_size // 2
            draw.ellipse([button_x, button_y, button_x + button_size, button_y + button_size], 
                        fill=xiaomi_orange)
        else:
            # 小尺寸时简化为圆点
            dot_size = size // 4
            dot_left = center_x - dot_size // 2
            dot_top = center_y - dot_size // 2
            draw.ellipse([dot_left, dot_top, dot_left + dot_size, dot_top + dot_size], 
                        fill=white)
        
        images.append(img)
        print(f"✅ 创建 {size}x{size} 图标")
    
    # 保存为ICO文件
    icon_path = 'xiaomi_wallet.ico'
    images[0].save(icon_path, format='ICO', sizes=[(img.width, img.height) for img in images])
    
    print(f"🎯 图标已保存到: {os.path.abspath(icon_path)}")
    
    # 创建预览图像
    preview_img = images[-1]  # 使用最大尺寸
    preview_path = 'xiaomi_wallet_preview.png'
    preview_img.save(preview_path, format='PNG')
    print(f"👀 预览图已保存到: {os.path.abspath(preview_path)}")
    
    return icon_path

if __name__ == "__main__":
    create_xiaomi_icon()
