# QDII基金监控 - 邮件通知配置指南

## 🎯 功能概述
当系统检测到新的QDII基金数据时，会自动发送邮件通知。

邮件功能支持：
- QQ邮箱、Gmail、163邮箱、Outlook等主流邮箱
- 自发自收（自己发给自己）或发送给多个收件人
- HTML和纯文本双格式邮件
- 详细的基金信息展示

## 📋 GitHub 环境配置步骤

### 第一步：创建生产环境
1. 打开你的GitHub仓库页面
2. 点击 `Settings` → `Environments`
3. 点击 `New environment` 按钮
4. 输入环境名称：`prod`
5. 点击 `Configure environment` 完成创建

### 第二步：在环境中配置Secrets
1. 在刚才创建的 `prod` 环境中，点击 `Add secret`
2. 依次添加以下Secrets（见下一步详细说明）

### 第三步：添加邮件配置Secrets

需要添加以下3个Secrets：

#### 1. EMAIL_ADDRESS（邮箱地址）
```
名称：EMAIL_ADDRESS
值：你的邮箱地址
示例：12345678@qq.com
```

#### 2. EMAIL_PASSWORD（邮箱授权码）
```
名称：EMAIL_PASSWORD
值：你的邮箱授权码（不是邮箱密码）
示例：abc123def456（QQ邮箱授权码）
```

#### 3. EMAIL_PROVIDER（邮箱服务商）
```
名称：EMAIL_PROVIDER
值：邮箱服务商代码
可选值：qq | gmail | 163 | outlook | 126 | sina
示例：qq
```

## 📧 各邮箱服务商配置方法

### QQ邮箱（推荐）
1. 登录QQ邮箱网页版
2. 点击顶部菜单栏的「设置」→「账户」
3. 找到「POP3/SMTP服务」，点击「开启」
4. 按提示发送短信验证
5. 获得16位授权码（这就是EMAIL_PASSWORD的值）
6. EMAIL_PROVIDER设置为：`qq`

### Gmail
1. 登录Gmail账户
2. 进入「Google账户」→「安全性」
3. 开启「两步验证」
4. 生成「应用专用密码」
5. 获得16位应用专用密码（这就是EMAIL_PASSWORD的值）
6. EMAIL_PROVIDER设置为：`gmail`

### 163邮箱
1. 登录163邮箱网页版
2. 点击顶部菜单栏的「设置」→「POP3/SMTP」
3. 开启「POP3/SMTP服务」
4. 按提示发送短信验证
5. 获得授权码（这就是EMAIL_PASSWORD的值）
6. EMAIL_PROVIDER设置为：`163`

## ⚙️ 环境变量说明

脚本会自动从环境变量读取以下配置：

| 环境变量名 | 说明 | 示例值 |
|------------|------|--------|
| EMAIL_ADDRESS | 发件人邮箱地址 | 12345678@qq.com |
| EMAIL_PASSWORD | 邮箱授权码/应用专用密码 | abc123def456 |
| EMAIL_PROVIDER | 邮箱服务商代码 | qq |

## 🧪 测试邮件功能

### 本地测试
可以创建一个测试脚本验证邮件功能：

```python
# test_email.py
import os
from email_notifier import SimpleEmailNotifier

# 设置测试环境变量
os.environ['EMAIL_ADDRESS'] = '你的邮箱地址'
os.environ['EMAIL_PASSWORD'] = '你的授权码'
os.environ['EMAIL_PROVIDER'] = 'qq'

# 测试邮件功能
notifier = SimpleEmailNotifier()

# 测试连接
success, message = notifier.test_connection()
print(f"连接测试: {message}")

# 发送测试邮件
if success:
    test_data = [{
        'fundCode': '123456',
        'fundShortName': '测试基金',
        'reportName': '测试报告',
        'organName': '测试公司',
        'uploadDate': '2025-01-01',
        'reportSendDate': '2025-01-01'
    }]

    result = notifier.send_fund_notification(test_data)
    print(f"测试邮件发送: {'成功' if result else '失败'}")
```

### GitHub Actions 环境测试
由于配置了 `environment: prod`，GitHub Actions 会自动：
1. 使用 `prod` 环境中配置的 Secrets
2. 环境变量会自动注入到工作流中
3. 无需手动设置环境变量

要验证GitHub Actions中的邮件功能是否正常工作：
1. 在GitHub Actions页面查看工作流运行日志
2. 查找"邮件通知发送成功"或相关错误信息
3. 检查你的邮箱是否收到新基金数据通知邮件

## 📊 邮件发送情况

### 发送时机
- 只有在检测到**新基金数据**时才会发送邮件
- 如果数据已存在（重复数据），不会发送邮件
- 邮件功能配置不完整时，会显示提示信息但不会中断主程序

### 邮件内容
- **主题**：[QDII基金更新] 发现 X 条新基金数据
- **内容**：包含新基金的详细信息（基金代码、名称、公司、日期等）
- **格式**：同时支持HTML和纯文本格式
- **时间戳**：显示数据获取的具体时间

### 收件人设置
- 默认发送给自己（自发自收）
- 可以通过代码修改发送到其他邮箱地址
- 支持发送给多个收件人

## 🔧 故障排除

### 常见问题

#### 1. 邮件发送失败
**可能原因**：
- 授权码错误（不是邮箱登录密码）
- 邮箱服务商选择错误
- 网络连接问题

**解决方法**：
- 检查授权码是否正确
- 确认EMAIL_PROVIDER设置正确
- 查看详细的错误信息输出

#### 2. 收不到邮件
**可能原因**：
- 邮件被归类为垃圾邮件
- 邮箱地址填写错误
- 发送频率过高

**解决方法**：
- 检查垃圾邮件文件夹
- 确认邮箱地址拼写正确
- 适当降低发送频率

#### 3. GitHub Actions中邮件发送失败
**可能原因**：
- Secrets配置不完整
- 环境变量未正确传递

**解决方法**：
- 检查所有必需的Secrets是否都已添加
- 查看Actions运行日志中的详细错误信息
- 确保Secrets名称拼写正确

## 📈 使用建议

1. **使用频率**：建议每天运行一次，避免过于频繁
2. **邮箱选择**：QQ邮箱配置最简单，推荐优先使用
3. **安全第一**：授权码不要泄露，定期更换
4. **监控状态**：定期检查GitHub Actions运行状态

## 🎯 效果验证

配置完成后，当有新基金数据时，你会收到类似这样的邮件：

```
主题：[QDII基金更新] 发现 2 条新基金数据

内容：
1. 基金代码：025587
   基金名称：光大保德信阳光香港精选混合（QDII）
   报告名称：光大保德信阳光香港精选混合型证券投资基金（QDII）招募说明书
   基金公司：光大保德信
   上传日期：2025-11-27
   报告日期：2025-11-27

2. 基金代码：020988
   基金名称：南方恒生科技ETF发起联接（QDII）
   报告名称：南方恒生科技交易型开放式指数证券投资基金发起式联接基金（QDII）招募说明书
   基金公司：南方
   上传日期：2025-11-14
   报告日期：2025-11-17
```

这样你就能第一时间了解到新的QDII基金发行信息！🎉

## 📝 注意事项

1. **免费额度**：各邮箱服务商都有免费发送额度，个人使用完全够用
2. **安全提醒**：不要将真实的邮箱密码直接用作Secrets，使用授权码
3. **隐私保护**：邮件内容只包含公开的基金信息，不涉及个人隐私
4. **备份方案**：邮件只是通知方式，主要数据仍然保存在CSV文件中

配置完成后，你的QDII基金监控系统就具备了完整的邮件通知功能！📧✨