#!/usr/bin/env python3
"""
简单邮件通知模块
支持QQ邮箱、Gmail、163邮箱等SMTP发送
配置从环境变量读取（GitHub Secrets）
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class SimpleEmailNotifier:
    """简单邮件通知类"""

    def __init__(self):
        """从环境变量读取配置"""
        self.sender_email = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')  # 授权码或应用专用密码
        self.email_provider = os.getenv('EMAIL_PROVIDER', 'qq').lower()

        # SMTP服务器配置
        self.smtp_configs = {
            'qq': {'server': 'smtp.qq.com', 'port': 465},
            'gmail': {'server': 'smtp.gmail.com', 'port': 587},
            '163': {'server': 'smtp.163.com', 'port': 25},
            'outlook': {'server': 'smtp.office365.com', 'port': 587},
            '126': {'server': 'smtp.126.com', 'port': 25},
            'sina': {'server': 'smtp.sina.com', 'port': 587}
        }

        self.logger = logging.getLogger(__name__)

    def is_configured(self):
        """检查是否已配置邮件功能"""
        return bool(self.sender_email and self.email_password)

    def send_fund_notification(self, new_funds_data, recipient_emails=None):
        """
        发送基金更新通知邮件
        :param new_funds_data: 新基金数据列表
        :param recipient_emails: 收件人邮箱列表（默认发给自己）
        :return: 发送成功返回True，失败返回False
        """

        if not self.is_configured():
            self.logger.warning("邮件功能未配置，跳过邮件发送")
            return False

        if not new_funds_data:
            self.logger.info("没有新基金数据，跳过邮件通知")
            return True

        # 默认收件人为发件人自己（自发自收）
        if not recipient_emails:
            recipient_emails = [self.sender_email]

        try:
            # 格式化邮件内容
            subject, body_text, body_html = self._format_email_content(new_funds_data)

            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipient_emails)
            msg['Subject'] = subject

            # 添加邮件正文（同时支持纯文本和HTML格式）
            msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
            msg.attach(MIMEText(body_html, 'html', 'utf-8'))

            # 连接SMTP服务器并发送
            config = self.smtp_configs.get(self.email_provider, self.smtp_configs['qq'])

            with smtplib.SMTP_SSL(config['server'], config['port']) as server:
                server.login(self.sender_email, self.email_password)
                # 使用 sendmail 替代 send_message 避免 QQ 邮箱的响应错误
                server.sendmail(self.sender_email, recipient_emails, msg.as_string())

            self.logger.info(f"📧 邮件发送成功: {subject}")
            print(f"✅ 基金更新邮件已发送至: {', '.join(recipient_emails)}")
            return True

        except smtplib.SMTPException as e:
            # QQ 邮箱在发送成功后可能返回 (-1, b'\x00\x00\x00')，这实际上表示成功
            error_str = str(e)
            if "(-1, b'\\x00\\x00\\x00')" in error_str or error_str == "(-1, b'\\x00\\x00\\x00')":
                self.logger.info(f"📧 邮件发送成功 (QQ邮箱特殊响应): {subject}")
                print(f"✅ 基金更新邮件已发送至: {', '.join(recipient_emails)}")
                return True
            else:
                self.logger.error(f"📧 邮件发送失败: {e}")
                print(f"❌ 邮件发送失败: {e}")
                return False
        except Exception as e:
            self.logger.error(f"📧 邮件发送失败: {e}")
            print(f"❌ 邮件发送失败: {e}")
            return False

    def _format_email_content(self, new_funds_data):
        """格式化邮件内容"""

        current_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"[QDII基金更新] {current_date} - 发现 {len(new_funds_data)} 条新基金数据"

        # 纯文本格式
        body_text = f"""
QDII基金数据更新通知

发现 {len(new_funds_data)} 条新基金数据：

"""

        for i, fund in enumerate(new_funds_data, 1):
            body_text += f"""
{i}. 基金代码：{fund.get('fundCode', 'N/A')}
   基金名称：{fund.get('fundShortName', 'N/A')}
   报告名称：{fund.get('reportName', 'N/A')}
   基金公司：{fund.get('organName', 'N/A')}
   上传日期：{fund.get('uploadDate', 'N/A')}
   报告日期：{fund.get('reportSendDate', 'N/A')}
"""

        body_text += f"""
数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
CSV文件路径：data/csrc_fund_data.csv

---
此邮件由QDII基金监控系统自动发送
"""

        # HTML格式（更美观）
        body_html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
        .fund-item {{ background: white; margin: 15px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid #667eea; }}
        .fund-title {{ font-size: 18px; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
        .fund-info {{ margin: 5px 0; }}
        .fund-label {{ font-weight: bold; color: #555; }}
        .footer {{ background: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #666; margin-top: 20px; border-radius: 8px; }}
        .stats {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🚀 QDII基金数据更新通知</h2>
        <p>发现 {len(new_funds_data)} 条新基金数据</p>
    </div>

    <div class="content">
        <div class="stats">
            <strong>📊 本次更新概况</strong><br>
            新增基金数量：<strong>{len(new_funds_data)}</strong> 条<br>
            更新时间：<strong>{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</strong>
        </div>

        <h3>📋 新基金详情：</h3>
"""

        for i, fund in enumerate(new_funds_data, 1):
            body_html += f"""
        <div class="fund-item">
            <div class="fund-title">{i}. {fund.get('fundCode', 'N/A')} - {fund.get('fundShortName', 'N/A')}</div>
            <div class="fund-info"><span class="fund-label">📄 报告名称：</span>{fund.get('reportName', 'N/A')}</div>
            <div class="fund-info"><span class="fund-label">🏢 基金公司：</span>{fund.get('organName', 'N/A')}</div>
            <div class="fund-info"><span class="fund-label">⬆️ 上传日期：</span>{fund.get('uploadDate', 'N/A')}</div>
            <div class="fund-info"><span class="fund-label">📅 报告日期：</span>{fund.get('reportSendDate', 'N/A')}</div>
        </div>
"""

        body_html += f"""
    </div>

    <div class="footer">
        <p>⏰ 数据获取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>📁 CSV文件路径：data/csrc_fund_data.csv</p>
        <p>🤖 此邮件由QDII基金监控系统自动发送</p>
    </div>
</body>
</html>
"""

        return subject, body_text, body_html

    def test_connection(self):
        """测试邮件连接"""
        try:
            config = self.smtp_configs.get(self.email_provider, self.smtp_configs['qq'])
            with smtplib.SMTP(config['server'], config['port']) as server:
                server.starttls()
                server.login(self.sender_email, self.email_password)
            return True, "邮件连接测试成功"
        except Exception as e:
            return False, f"邮件连接测试失败: {e}"