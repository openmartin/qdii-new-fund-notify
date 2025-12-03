# qdii-new-fund-notify

定时从资本市场电子化信息披露平台获取新发行基金的数据

```
http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=
```

## 定时 API 数据获取功能

这个项目现在包含了 GitHub Actions 定时任务功能，专门从资本市场电子化信息披露平台获取新发行基金数据：

### 功能特点
- 使用 Python 3.12 标准库 urllib（无需 requests 包）
- 支持手动触发工作流程
- 自动将原始数据保存到文本文件

### 工作流程文件

- `fetch_csrc_data.py`: 完整版本的数据获取脚本


### 启动脚本

```shell
nohup env PYTHONUNBUFFERED=1 EMAIL_ADDRESS=xxx EMAIL_PASSWORD=xxx python fetch_csrc_data.py --schedule --interval 720 > fetch.log 2>&1 &
```