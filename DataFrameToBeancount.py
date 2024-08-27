import enum
import json


class AccountType(enum.Enum):
    """
    枚举类型，用于表示账户类型
    五种Assets Liabilities Equity Income Expenses，每行都注释

    """

    # Assets 资产
    Assets = "Assets"
    # Liabilities 负债
    Liabilities = "Liabilities"
    # Equity 所有者权益
    Equity = "Equity"
    # Income 收入
    Income = "Income"
    # Expenses 花费
    Expenses = "Expenses"


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

    # 给出keywords'易云音乐支付',找出推荐账本
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
