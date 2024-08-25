from decimal import Decimal, InvalidOperation
import numpy as np
import pandas as pd


# 定义一个函数，用于识别货币符号并转换金额，未识别的货币符号默认为人民币（CNY）
def parse_amount_with_currency(x):
    amount = None
    currency = "CNY"  # 默认币种设置为人民币

    # 定义一个字典，映射货币符号到货币代码
    currency_symbols = {
        "¥": "CNY",  # 人民币
        "￥": "CNY",  # 人民币
        "$": "USD",  # 美元
        "€": "EUR",  # 欧元
        "£": "GBP",  # 英镑
        # 可以根据需要添加其他货币符号
    }
    # 尝试找到并移除货币符号,记录货币符号
    for symbol in currency_symbols:
        if symbol in x:
            x = x.replace(symbol, "")
            currency = currency_symbols[symbol]
            break

    # 移除可能存在的空格和逗号
    x = x.replace(" ", "").replace(",", "")

    # 尝试将输入字符串转换为浮点数，如果失败则捕获异常
    try:
        # 将字符串转换为Decimal类型
        amount = Decimal(x)  #
    except InvalidOperation:
        amount = pd.NA  # 如果转换失败，标记为缺失值
    return amount, currency  # 示例返回值
