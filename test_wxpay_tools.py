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


if __name__ == "__main__":

    # 包含金额和货币符号的字符串
    data = [
        "￥100.00",
        "$2.50",
        "€3.15",
        "£4.16",
        "100.01",
        "无效金额",
    ]

    # 创建DataFrame并应用函数
    df = pd.DataFrame({"amount_data": data})
    df[["amount", "currency"]] = (
        df["amount_data"].apply(parse_amount_with_currency).apply(pd.Series)
    )

    print(df[["amount", "currency"]])
    # 验证结果
    # 缺失值数目为1
    assert df["amount"].isna().sum() == 1
    # 总金额为109.81
    assert df["amount"].sum() == Decimal("209.82")
    # 货币种类为CNY, USD, EUR, GBP
    assert set(df["currency"]) == {"CNY", "USD", "EUR", "GBP"}

    # 每种货币的金额和数量
    assert df[df["currency"] == "CNY"]["amount"].sum() == Decimal("200.01")

    assert df["amount"][0] == Decimal("100.00")
    assert df["currency"][0] == "CNY"

    assert df["amount"][1] == Decimal("2.50")
    assert df["currency"][1] == "USD"

    assert df["amount"][2] == Decimal("3.15")
    assert df["currency"][2] == "EUR"

    assert df["amount"][3] == Decimal("4.16")
    assert df["currency"][3] == "GBP"

    assert df["amount"][4] == Decimal("100.01")
    assert df["currency"][4] == "CNY"

    assert df["amount"][5] is pd.NA
    assert df["currency"][5] == "CNY"

    print("All tests passed!")
    print(df[["amount", "currency"]])
