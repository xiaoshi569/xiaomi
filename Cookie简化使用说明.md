# 🍪 Cookie登录简化使用说明

## 📋 简化版Cookie登录

经过优化，现在Cookie登录变得非常简单！只需要两个参数：

### ✅ 需要的信息
1. **passToken** - 长字符串token
2. **userId** - 用户ID数字

### 📝 从您的示例中提取：
```
passToken=V1:DXmurwq2/R1BHTELu6obCc+2Ip9gTy8w2NxTkAvm41UexxeULlm7bpa4g1+8uNRmS9nIKPt0cN6XZDhu6OwjlNv3sw8qnqxm9QETPf31HL3QnEolewwfVMeiFL/VRL8jFQ3o7DZ4sAb0kE0ZweHt7yrsS6RYDb3/A4KvDQ4ZGDQ1MTQrJDi5k96rHvxVSQWHzFEEK56UV+oobPU3QTFNUOnhKrSI3YijkU6wzG5olmNA0xdO8C939Cl/JAFoUVos/C9yh385FO3Yh+e4IW+G+4C6VDWchQngtXtuPruBHwjOa1vfEQWWKRPZV4twy5Njc3dh2dYE6Sw3pFUfirOctg==;userId=3081898858
```

**提取结果：**
- **passToken**: `V1:DXmurwq2/R1BHTELu6obCc+2Ip9gTy8w2NxTkAvm41UexxeULlm7bpa4g1+8uNRmS9nIKPt0cN6XZDhu6OwjlNv3sw8qnqxm9QETPf31HL3QnEolewwfVMeiFL/VRL8jFQ3o7DZ4sAb0kE0ZweHt7yrsS6RYDb3/A4KvDQ4ZGDQ1MTQrJDi5k96rHvxVSQWHzFEEK56UV+oobPU3QTFNUOnhKrSI3YijkU6wzG5olmNA0xdO8C939Cl/JAFoUVos/C9yh385FO3Yh+e4IW+G+4C6VDWchQngtXtuPruBHwjOa1vfEQWWKRPZV4twy5Njc3dh2dYE6Sw3pFUfirOctg==`
- **userId**: `3081898858`

## 🚀 使用步骤

### 1. 打开应用并选择Cookie登录
```bash
python gui.py
```

### 2. 在登录页面
- 输入账号别名（例如：`我的账号`）
- 选择"Cookie登录"

### 3. 填写Cookie信息
- **passToken框**：粘贴完整的passToken值
- **userId框**：输入userId数字

### 4. 验证和保存
- 点击"测试连接"（可选，验证是否有效）
- 点击"验证并保存"完成添加

## ✨ 界面特色

- 🎯 **极简设计**：只需两个输入框
- 💡 **智能提示**：包含示例和说明
- ✅ **一键验证**：自动转换并验证Cookie
- 🔄 **无缝集成**：与扫码登录完美共存

## 🔧 技术原理

程序会自动：
1. 接收您输入的`passToken`和`userId`
2. 调用小米API获取完整Cookie
3. 验证Cookie有效性
4. 保存到配置文件供后续使用

## 💡 优势对比

| 特性 | 扫码登录 | 简化Cookie登录 |
|------|----------|----------------|
| 输入复杂度 | 无需输入 | 仅需2个参数 |
| 速度 | 需要手机扫码 | 秒级完成 |
| 批量添加 | 逐个扫码 | 快速批量 |
| 安全性 | 最高 | 高 |

## ⚠️ 注意事项

1. **保护信息安全**：不要将passToken和userId泄露给他人
2. **有效期限制**：Cookie有一定有效期，过期需重新获取
3. **格式准确性**：确保复制完整的passToken值
4. **测试建议**：首次使用建议先点击"测试连接"验证

现在您可以快速便捷地添加账号了！🎉

