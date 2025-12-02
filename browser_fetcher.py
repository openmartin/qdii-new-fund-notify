#!/usr/bin/env python3
"""
使用浏览器自动化从资本市场电子化信息披露平台获取新发行基金数据
绕过反爬虫策略
"""

import json
import time
import csv
import os
import sys
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class CSRCBrowserFetcher:
    def __init__(self):
        self.driver = None
        self.wait = None

    def setup_browser(self):
        """设置浏览器选项"""
        chrome_options = Options()

        # 无头模式（在服务器上运行）
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # 反检测设置
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 安装并设置ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 执行脚本隐藏WebDriver属性
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 设置等待时间
        self.wait = WebDriverWait(self.driver, 20)

        print("浏览器初始化完成")

    def fetch_fund_data(self):
        """获取基金数据 - 通过浏览器直接发起API请求"""
        try:
            # 设置浏览器
            self.setup_browser()

            # 先访问详情页面建立会话和cookies
            detail_url = "http://eid.csrc.gov.cn/fund/disclose/index.html"
            print(f"正在访问详情页面: {detail_url}")
            self.driver.get(detail_url)

            # 等待页面加载获取必要的cookies和session信息
            time.sleep(20)

            # 计算日期范围
            current_date = datetime.now()
            yesterday = current_date - timedelta(days=30)

            # 通过浏览器直接发起API请求获取数据
            fund_data = self.make_direct_api_request(yesterday, current_date)

            return fund_data

        except Exception as e:
            print(f"获取数据失败: {e}")
            return None

        finally:
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")

    def make_direct_api_request(self, start_date, end_date):
        """通过浏览器直接发起API请求"""
        try:
            print("正在通过浏览器发起API请求...")

            # 构建API参数
            ao_data = [
                {"name": "sEcho", "value": 2},
                {"name": "iColumns", "value": 6},
                {"name": "sColumns", "value": ",,,,,,"},
                {"name": "iDisplayStart", "value": 0},
                {"name": "iDisplayLength", "value": 100},  # 增加返回数量
                {"name": "mDataProp_0", "value": "fundCode"},
                {"name": "mDataProp_1", "value": "fundId"},
                {"name": "mDataProp_2", "value": "reportName"},
                {"name": "mDataProp_3", "value": "organName"},
                {"name": "mDataProp_4", "value": "reportDesp"},
                {"name": "mDataProp_5", "value": "reportSendDate"},
                {"name": "fundType", "value": "6020-6050"},  # QDII基金
                {"name": "reportType", "value": "FA010010"},
                {"name": "reportYear", "value": ""},
                {"name": "fundCompanyShortName", "value": ""},
                {"name": "fundCode", "value": ""},
                {"name": "fundShortName", "value": ""},
                {"name": "startUploadDate", "value": start_date.strftime('%Y-%m-%d')},
                {"name": "endUploadDate", "value": end_date.strftime('%Y-%m-%d')}
            ]

            # 构建API URL
            base_url = "http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do"
            ao_data_str = urllib.parse.quote(json.dumps(ao_data))
            timestamp_ms_str = str(int(time.time() * 1000))
            api_url = f"{base_url}?aoData={ao_data_str}&_={timestamp_ms_str}"

            # 设置更长的脚本超时时间（60秒）
            self.driver.set_script_timeout(60)

            # 使用浏览器执行JavaScript发起GET请求
            # 注意：使用execute_async_script来处理异步操作
            js_code = f"""
            var callback = arguments[0];
            const xhr = new XMLHttpRequest();
            xhr.open('GET', '{api_url}', true);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');


            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4) {{
                    if (xhr.status === 200) {{
                        try {{
                            const response = JSON.parse(xhr.responseText);
                            callback(response);
                        }} catch (e) {{
                            callback(xhr.responseText);
                        }}
                    }} else {{
                        callback({{error: `HTTP ${{xhr.status}}: ${{xhr.statusText}}`}});
                    }}
                }}
            }};

            xhr.onerror = function() {{
                callback({{error: 'Network error'}});
            }};

            xhr.send();
            """

            print(f"正在请求API: {api_url}")

            # 在浏览器中执行异步JavaScript代码
            result = self.driver.execute_async_script(js_code)

            # 处理返回结果
            if result:
                # 检查是否有错误
                if isinstance(result, dict) and 'error' in result:
                    print(f"API请求错误: {result['error']}")
                    return []

                fund_data = self.process_api_response(result)
                return fund_data
            else:
                print("API请求返回空结果")
                return []

        except TimeoutException:
            print("API请求超时，请检查网络连接或增加超时时间")
            return []
        except Exception as e:
            print(f"API请求失败: {e}")
            return []

    def process_api_response(self, response):
        """处理API响应数据"""
        try:
            # 如果响应是字符串，尝试解析为JSON
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except json.JSONDecodeError:
                    print(f"响应不是有效的JSON格式: {response[:200]}")
                    return []
            else:
                data = response

            # 检查是否有aaData字段（DataTables的标准格式）
            if isinstance(data, dict) and 'aaData' in data:
                print(f"获取到 {len(data['aaData'])} 条数据")

                # 转换为标准格式
                fund_data = []
                for i, item in enumerate(data['aaData']):
                    if isinstance(item, list) and len(item) >= 6:
                        fund_item = {
                            'fundCode': item[0] if len(item) > 0 else '',
                            'fundId': item[1] if len(item) > 1 else '',
                            'reportName': item[2] if len(item) > 2 else '',
                            'organName': item[3] if len(item) > 3 else '',
                            'reportDesp': item[4] if len(item) > 4 else '',
                            'reportSendDate': item[5] if len(item) > 5 else '',
                            'uploadInfoDetailId': f"api_{i}_{int(time.time())}",
                            'uploadDate': datetime.now().strftime('%Y-%m-%d')
                        }
                        fund_data.append(fund_item)

                return fund_data
            elif isinstance(data, list):
                print(f"获取到 {len(data)} 条数据")
                return data
            else:
                print(f"未识别的数据格式: {type(data)}")
                return []

        except Exception as e:
            print(f"处理API响应失败: {e}")
            return []

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


def fetch_csrc_data_browser():
    """使用浏览器获取CSRC数据的主函数"""
    fetcher = CSRCBrowserFetcher()
    return fetcher.fetch_fund_data()


if __name__ == "__main__":
    print("开始通过浏览器获取CSRC基金数据...")
    data = fetch_csrc_data_browser()

    if data:
        print(f"获取成功，共 {len(data)} 条数据")
        # 保存为JSON文件用于测试
        with open('browser_fund_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("数据已保存到 browser_fund_data.json")
    else:
        print("获取数据失败")