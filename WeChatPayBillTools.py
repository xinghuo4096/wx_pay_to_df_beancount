from decimal import Decimal, InvalidOperation
import numpy as np
import pandas as pd
import json


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


def ai_get_account_by_keyword(keyword):
    ## TODO：给定自己定义好的多个账户让ai选择
    # ，比如50个账户，问ai，给出最合适记账的账户，比如：易云音乐支付， 问ai后，ai从给出选择列表里选，给出最合适的账户'Entertainment娱乐:E数字'。

    pass


def get_account_by_keyword(
    keyword, default_is_None: bool = True, default="默认账本:{keyword}"
):
    """
    根据关键字，返回过账记录的账本。
    :param keyword: 关键字
    :return: 账本
    """
    # 从文件读取JSON数据
    with open(
        "secret/data_with_descriptions_and_ledgers.json", "r", encoding="utf-8"
    ) as f:
        loaded_data = json.load(f)

    assert loaded_data is not None, "数据为空"

    # 给出keywords，如：'网易云音乐支付',找出推荐账本
    recommended_ledger = next(
        (
            loaded_data[i]["recommended_ledger"]
            for i in range(len(loaded_data))
            for key in loaded_data[i]["keywords"]
            if key in keyword
        ),
        None,
    )
    if recommended_ledger:
        return recommended_ledger
    else:
        if default_is_None:
            return None
        else:
            return default.format(keyword=keyword)


def get_narration_by_keyword(keyword):
    # TODO函数根据给定关键字，生成合适的narration
    # ai prompt：
    # 生成合适的narration，
    # 确保关键字集合既具有实用性，又能够有效地帮助识别和分类购物消费相关的字符串
    # 形成关键字的完整要求：
    # 简洁性：关键字应简短，便于快速识别和测试。
    # 代表性：关键字应能代表一类商户或服务，避免过于具体或唯一性名称。
    # 区分度：关键字应具有足够的区分能力，避免在其他类别中重复出现，减少误分类。
    # 覆盖面：关键字集合应广泛覆盖不同类型的购物场所和服务。
    # 适应性：关键字应根据实际情况和数据反馈进行调整，以提高分类的准确性。
    # 保留关键部分：对于包含重要信息的商户名称，应保留其关键部分，如服务类型或主要商品，以确保关键字的识别能力。
    # 函数根据商品名称判断posting,narration，可用ai辅助判断
    return keyword
