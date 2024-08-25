import pandas as pd
from decimal import Decimal
from WeChatPayBillTools import parse_amount_with_currency

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
