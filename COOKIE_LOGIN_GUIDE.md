# Cookie登录功能使用指南

## 功能介绍

新增的Cookie登录功能可以让您直接通过Cookie信息登录，避免每次都需要扫码的麻烦。支持两种Cookie输入方式：

## 使用方法

### 方式一：直接输入完整Cookie

1. 在登录页面选择"Cookie登录"
2. 选择"直接输入完整Cookie"
3. 在文本框中输入完整的Cookie字符串

**Cookie格式要求：**
```
cUserId=xxx;jrairstar_serviceToken=xxx
```

### 方式二：通过passToken和userId获取Cookie

1. 在登录页面选择"Cookie登录"
2. 选择"输入passToken和userId"
3. 分别输入passToken和userId
4. 系统会自动通过这些信息获取Cookie

## Cookie获取方法

### 方法一：从浏览器开发者工具获取

1. 打开浏览器，访问小米钱包相关页面并登录
2. 按F12打开开发者工具
3. 切换到"网络"(Network)标签
4. 刷新页面，找到请求头中的Cookie信息
5. 复制`cUserId`和`jrairstar_serviceToken`的值

### 方法二：从小米钱包3.0.py脚本获取

参考项目中的`小米钱包3.0.py`文件，该脚本会输出Cookie信息，格式为：
```
cUserId=xxx;jrairstar_serviceToken=xxx
```

### 方法三：使用现有的passToken和userId

如果您已经有passToken和userId，可以直接使用方式二，系统会自动获取Cookie。

## 功能特性

- ✅ **Cookie验证**：自动验证Cookie格式和有效性
- ✅ **Cookie测试**：可以在保存前测试Cookie是否有效
- ✅ **自动保存**：验证成功后自动保存账号信息
- ✅ **错误提示**：详细的错误信息和解决建议
- ✅ **安全性**：Cookie信息仅存储在本地，不会上传

## 注意事项

1. **Cookie时效性**：Cookie有一定的有效期，过期后需要重新获取
2. **格式要求**：必须包含`cUserId`和`jrairstar_serviceToken`字段
3. **账号安全**：请确保Cookie信息的安全，不要泄露给他人
4. **定期更新**：建议定期更新Cookie以确保账号正常使用

## 常见问题

**Q: Cookie无效怎么办？**
A: 请重新获取Cookie，或使用passToken和userId方式登录。

**Q: 格式错误提示？**
A: 请检查Cookie是否包含必要的字段，格式是否正确。

**Q: 测试失败？**
A: 可能是Cookie已过期或格式不正确，请重新获取。

## 与扫码登录的区别

| 特性 | 扫码登录 | Cookie登录 |
|------|----------|------------|
| 便捷性 | 需要手机扫码 | 直接输入即可 |
| 安全性 | 高 | 中等 |
| 稳定性 | 高 | 依赖Cookie有效期 |
| 适用场景 | 初次添加账号 | 批量添加或快速添加 |

建议首次使用时采用扫码登录，后续可以导出Cookie用于快速添加账号。
