#!/usr/bin/env python3
"""
从资本市场电子化信息披露平台获取新发行基金数据
使用 urllib 和浏览器自动化两种方式
"""

import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import sys
import csv

# 浏览器自动化模块
try:
    from browser_fetcher import fetch_csrc_data_browser
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False
    print("浏览器自动化模块不可用，将仅使用urllib方式")


def fetch_csrc_data():
    """从 CSRC 网站获取基金数据"""

    # API 地址和参数
    base_url = "http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do"

    current_date_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # 设置请求参数
    ao_data = [
        {"name": "sEcho", "value": 2},
        {"name": "iColumns", "value": 6},
        {"name": "sColumns", "value": ",,,,,,"},
        {"name": "iDisplayStart", "value": 0},
        {"name": "iDisplayLength", "value": 20},
        {"name": "mDataProp_0", "value": "fundCode"},
        {"name": "mDataProp_1", "value": "fundId"},
        {"name": "mDataProp_2", "value": "reportName"},
        {"name": "mDataProp_3", "value": "organName"},
        {"name": "mDataProp_4", "value": "reportDesp"},
        {"name": "mDataProp_5", "value": "reportSendDate"},
        {"name": "fundType", "value": "6020-6050"},
        {"name": "reportType", "value": "FA010010"},
        {"name": "reportYear", "value": ""},
        {"name": "fundCompanyShortName", "value": ""},
        {"name": "fundCode", "value": ""},
        {"name": "fundShortName", "value": ""},
        {"name": "startUploadDate", "value": yesterday_str},
        {"name": "endUploadDate", "value": current_date_str}
    ]

    # 将参数编码为 JSON 字符串
    ao_data_str = urllib.parse.quote(json.dumps(ao_data))
    timestamp_ms_str = str(int(time.time() * 1000))
    api_url = f"{base_url}?aoData={ao_data_str}&_={timestamp_ms_str}"

    try:
        print(f"正在获取数据从: {api_url}")

        # 创建请求对象
        req = urllib.request.Request(api_url)

        # 设置请求头，模拟浏览器访问
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')
        req.add_header('Accept', 'application/json, text/javascript, */*; q=0.01')
        req.add_header('Accept-Language', 'zh-CN,zh;q=0.9')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Host', 'eid.csrc.gov.cn')
        req.add_header('Referer', 'http://eid.csrc.gov.cn/fund/disclose/fund_detail.do?fundId=15977&rnd=0.9272639559371317')
        req.add_header('X-Requested-With', 'XMLHttpRequest')

        # 发送请求并获取响应
        with urllib.request.urlopen(req, timeout=60) as response:
            # 获取响应状态码
            status_code = response.getcode()
            print(f"HTTP 状态码: {status_code}")

            # 读取响应头信息
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")

            # 读取响应内容
            content = response.read().decode('utf-8')
            print(f"响应内容长度: {len(content)}")

            # 如果内容为空，返回 None
            if not content or len(content.strip()) == 0:
                print("响应内容为空")
                return None

            # 尝试解析 JSON
            try:
                data = json.loads(content)
                print(f"成功解析 JSON 数据，数据类型: {type(data)}")
                return data
            except json.JSONDecodeError as e:
                print(f"JSON 解析失败，返回原始内容: {e}")
                # 如果 JSON 解析失败，返回原始内容
                return content

    except urllib.error.URLError as e:
        print(f"API 请求失败: {e}")
        if hasattr(e, 'reason'):
            print(f"失败原因: {e.reason}")
        return None
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return None


def process_fund_data(data):
    """处理基金数据，转换为标准格式"""

    if not data:
        return []

    # 如果数据是字符串（HTML 或其他格式），尝试提取有用信息
    if isinstance(data, str):
        print("数据是字符串格式，尝试处理...")
        # 这里可以根据实际返回格式进行解析
        # 暂时返回空列表
        return []

    # 如果数据是字典，检查是否有 aaData 字段（实际API返回格式）
    if isinstance(data, dict):
        if 'aaData' in data and isinstance(data['aaData'], list):
            print(f"从 aaData 中提取数据，共 {len(data['aaData'])} 条记录")
            return data['aaData']
        elif 'data' in data and isinstance(data['data'], list):
            return data['data']
        else:
            return [data]
    elif isinstance(data, list):
        return data
    else:
        print(f"不支持的数据格式: {type(data)}")
        return []


def save_fund_data_to_csv(fund_data, filename='data/csrc_fund_data.csv'):
    """保存基金数据到 CSV 文件，以 uploadInfoDetailId 为主键进行去重"""

    if not fund_data:
        print("没有数据需要保存")
        return False

    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)

    try:
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 如果文件已存在，先读取现有数据并创建以 uploadInfoDetailId 为键的字典
        existing_data_dict = {}
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 使用 uploadInfoDetailId 作为主键，如果不存在则跳过
                    if 'uploadInfoDetailId' in row:
                        existing_data_dict[row['uploadInfoDetailId']] = row

        # 准备新数据，同样以 uploadInfoDetailId 为键
        new_data_dict = {}
        for item in fund_data:
            # 确保有 uploadInfoDetailId 字段
            if 'uploadInfoDetailId' in item:
                # 添加时间戳
                item['fetched_at'] = current_time
                new_data_dict[str(item['uploadInfoDetailId'])] = item
            else:
                print(f"警告: 数据项缺少 uploadInfoDetailId 字段，已跳过: {item}")

        # 检查是否有新数据
        existing_ids = set(existing_data_dict.keys())
        new_ids = set(new_data_dict.keys())

        # 找出真正的新数据（不在现有数据中的）
        truly_new_ids = new_ids - existing_ids

        if not truly_new_ids:
            print("没有新的数据需要保存")
            return True

        print(f"发现 {len(truly_new_ids)} 条新数据")

        # 只处理新数据
        final_new_data = {id_: new_data_dict[id_] for id_ in truly_new_ids}

        # 获取新数据用于邮件通知
        new_data_for_email = []
        for id_ in truly_new_ids:
            new_data_for_email.append(new_data_dict[id_])

        # 合并数据，只添加新数据
        merged_data_dict = existing_data_dict.copy()
        merged_data_dict.update(final_new_data)

        # 转换为列表并按 uploadInfoDetailId 排序
        all_data = list(merged_data_dict.values())
        all_data.sort(key=lambda x: int(x['uploadInfoDetailId']))

        # 获取所有可能的字段
        all_fields = set()
        for item in all_data:
            all_fields.update(item.keys())

        # 定义核心字段的顺序，其他字段按字母顺序排列
        core_fields = ['uploadInfoDetailId', 'fundCode', 'fundShortName', 'reportName',
                      'organName', 'reportDesp', 'uploadDate', 'reportSendDate', 'fetched_at']
        other_fields = sorted([f for f in all_fields if f not in core_fields])
        all_fields = core_fields + other_fields

        # 写入 CSV 文件
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_fields)
            writer.writeheader()
            writer.writerows(all_data)

        new_records_count = len(final_new_data)
        total_records_count = len(all_data)
        print(f"数据已保存到 {filename}")
        print(f"新增记录: {new_records_count} 条")
        print(f"总记录数: {total_records_count} 条")

        # 发送邮件通知（如果有新数据且配置了邮件功能）
        if new_data_for_email:
            try:
                from email_notifier import SimpleEmailNotifier

                # 创建邮件通知器
                email_notifier = SimpleEmailNotifier()

                # 检查是否配置了邮件功能
                if email_notifier.is_configured():
                    print("正在发送邮件通知...")

                    # 发送邮件通知
                    success = email_notifier.send_fund_notification(new_data_for_email)

                    if success:
                        print("✅ 邮件通知发送成功")
                    else:
                        print("❌ 邮件通知发送失败")
                else:
                    print("邮件功能未配置（如需使用，请设置环境变量：EMAIL_ADDRESS, EMAIL_PASSWORD）")

            except ImportError:
                print("邮件模块导入失败，跳过邮件通知")
            except Exception as e:
                print(f"邮件通知发送异常: {e}")
                # 邮件发送失败不影响主程序继续运行

        return True

    except Exception as e:
        print(f"保存 CSV 文件失败: {e}")
        return False


def main():
    """主函数"""
    print("开始获取 CSRC 基金数据...")
    print("数据来源: 资本市场电子化信息披露平台")

    raw_data = None

    # 首先尝试使用浏览器自动化方式
    if BROWSER_AVAILABLE and os.environ.get('USE_BROWSER_FETCHER', 'true').lower() == 'true':
        print("尝试使用浏览器自动化获取数据...")
        try:
            raw_data = fetch_csrc_data_browser()
            if raw_data:
                print(f"浏览器自动化获取成功，共 {len(raw_data)} 条数据")
            else:
                print("浏览器自动化获取失败，将尝试urllib方式")
        except Exception as e:
            print(f"浏览器自动化出错: {e}")
            print("将尝试urllib方式")

    # 如果浏览器方式失败，尝试urllib方式
    if raw_data is None:
        print("使用urllib方式获取数据...")
        raw_data = fetch_csrc_data()

    if raw_data is None:
        print("获取数据失败，脚本退出")
        sys.exit(1)

    # 处理数据
    fund_data = process_fund_data(raw_data)
    print(f"处理后的数据量: {len(fund_data)}")

    if fund_data:
        print("数据示例:")
        for i, item in enumerate(fund_data[:3]):  # 显示前3条数据
            print(f"  {i + 1}: {item}")

    # 保存到 CSV 文件
    success = save_fund_data_to_csv(fund_data)

    if success:
        print("数据保存成功!")
    else:
        print("数据保存失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
