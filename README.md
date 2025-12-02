# qdii-new-fund-notify

定时从资本市场电子化信息披露平台获取新发行基金的数据

```
http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=
```

## 定时 API 数据获取功能

这个项目现在包含了 GitHub Actions 定时任务功能，专门从资本市场电子化信息披露平台获取新发行基金数据：

### 功能特点
- 每天早上 8 点自动从 CSRC 网站获取基金数据
- 使用 Python 3.12 标准库 urllib（无需 requests 包）
- 支持手动触发工作流程
- 自动将原始数据保存到文本文件
- 自动提交更改到 GitHub

### 工作流程文件
- `.github/workflows/daily-api-fetch.yml`: GitHub Actions 配置
- `fetch_csrc_simple.py`: 数据获取脚本（使用 urllib）
- `fetch_csrc_data.py`: 完整版本的数据获取脚本