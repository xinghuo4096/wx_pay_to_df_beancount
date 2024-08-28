# wx_pay_to_df_beancount

## 介绍

**wx_pay_to_df_beancount** 是一个开源 Python 工具，旨在简化微信支付账单的数据处理流程。本仓库提供了一站式的解决方案，帮助用户将微信支付账单数据高效地转换为 DataFrame 格式，进而再转换为 Beancount 记账格式。使用 AI 分析支付项目，生成关键字对应的类别，生成推荐的 beancount 记账账本名称。

## 主要功能

- **微信账单解析**：自动解析微信支付导出的账单文件。
- **DataFrame 转换**：将账单数据转换为 Pandas DataFrame，便于进行数据分析和预处理。
- **Beancount 格式输出**：将 DataFrame 中的数据转换为 Beancount 记账语言格式，以便于进行财务管理和报表生成。 ####使用场景：
- 个人财务管理：将微信支付账单数据集成到个人财务管理体系中。
- 财务分析：利用 DataFrame 进行详细的交易数据分析。
- 自动化记账：自动化处理账单数据，减少手动录入的繁琐工作。

## 安装指南

```bash

```

## 快速开始

```python
    from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame
    # AI处理后的文件，目前必须放到secret/data_with_descriptions_and_ledgers.json

    # 指定CSV文件路径
    # 把指定目录的以'微信'开头的.cvs文件名,合并目录名称后放入列表
    file_path = "secret"

    wx_csv = WeChatPayBillToDataFrame(file_path)

    df = wx_csv.read_wx_pay_to_df()
    wx_csv.prepare_df_for_beancount()

    wx_csv.check_data()

    wx_csv.save_to_file(
        json_path="secret\\wx_pay.json",
        html_path="secret\\wx_pay.html",
        csv_path="secret\\wx_pay.csv",
        beancount_html_path="secret\\wx_pay.beancount.html",
        beancount_csv_path="secret\\wx_pay.beancount.csv",
        unprocessed_html_path="secret\\wx_pay.unprocessed.html",
        unprocessed_csv_path="secret\\wx_pay.unprocessed.csv",
    )

    print(wx_csv.beancount_df.head())
    print(wx_csv.beancount_df.tail())

    assert wx_csv.beancount_df is not None, "beancount_df is None"
    assert wx_csv.beancount_df.head() is not None, "beancount_df.head() is None"

```
