#!/usr/bin/env python3
"""
邮件功能测试脚本
用于验证GitHub Secrets配置的邮件功能是否正常工作
"""

import os
import sys
from email_notifier import SimpleEmailNotifier


def test_email_function():
    """测试邮件功能"""
    print("🧪 开始测试邮件功能...")
    print("-" * 50)

    # 检查环境变量
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_provider = os.getenv('EMAIL_PROVIDER', 'qq')

    print(f"📧 邮箱地址: {email_address or '未设置'}")
    print(f"🔐 授权码状态: {'已设置' if email_password else '未设置'}")
    print(f"🏢 邮箱服务商: {email_provider}")

    if not email_address or not email_password:
        print("\n❌ 邮件配置不完整，请设置以下环境变量:")
        print("   EMAIL_ADDRESS: 你的邮箱地址")
        print("   EMAIL_PASSWORD: 你的邮箱授权码")
        print("   EMAIL_PROVIDER: 邮箱服务商 (qq/gmail/163/outlook)")
        return False

    # 创建邮件通知器
    print("\n🔧 创建邮件通知器...")
    notifier = SimpleEmailNotifier()

    # 测试连接
    print("\n🔗 测试邮件服务器连接...")
    success, message = notifier.test_connection()
    print(f"连接测试结果: {message}")

    if not success:
        print("\n❌ 邮件服务器连接失败，请检查配置")
        return False

    # 创建测试数据
    print("\n📊 创建测试基金数据...")
    test_funds = [
        {
            'fundCode': '025587',
            'fundShortName': '光大保德信阳光香港精选混合（QDII）',
            'reportName': '光大保德信阳光香港精选混合型证券投资基金（QDII）招募说明书',
            'organName': '光大保德信',
            'uploadDate': '2025年11月27日',
            'reportSendDate': '2025年11月27日',
            'uploadInfoDetailId': '1440955'
        },
        {
            'fundCode': '020988',
            'fundShortName': '南方恒生科技ETF发起联接（QDII）',
            'reportName': '南方恒生科技交易型开放式指数证券投资基金发起式联接基金（QDII）招募说明书',
            'organName': '南方',
            'uploadDate': '2025年11月14日',
            'reportSendDate': '2025年11月17日',
            'uploadInfoDetailId': '1434582'
        }
    ]

    print(f"测试数据包含 {len(test_funds)} 条基金记录")

    # 发送测试邮件
    print("\n📮 发送测试邮件...")
    success = notifier.send_fund_notification(test_funds)

    if success:
        print("\n✅ 测试邮件发送成功！")
        print(f"📧 请检查邮箱 {email_address} 是否收到测试邮件")
        print("\n🎉 邮件功能配置正确，可以正常使用")
        return True
    else:
        print("\n❌ 测试邮件发送失败")
        print("请检查:")
        print("1. 邮箱地址是否正确")
        print("2. 授权码/应用专用密码是否正确")
        print("3. 邮箱服务商选择是否正确")
        print("4. 网络连接是否正常")
        return False


def main():
    """主函数"""
    print("🚀 QDII基金监控系统 - 邮件功能测试")
    print("=" * 60)

    try:
        success = test_email_function()

        if success:
            print("\n✨ 所有测试通过！邮件功能已就绪")
            sys.exit(0)
        else:
            print("\n⚠️  测试失败，请检查配置")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()