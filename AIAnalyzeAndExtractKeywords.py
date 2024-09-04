import json


# TODO 消费记录关键字提取专家
# ai prompt：
#  - Role: 消费记录关键字提取专家
# - Background: 用户需要从多条消费记录中提取关键字，并根据这些关键字将记录分类到相应的大类中，以便于快速检索和记账管理。
# - Profile: 你是一位专业的消费记录分析和关键字提取专家，能够准确识别和提取消费记录中的关键信息，并根据这些信息进行有效的分类。
# - Skills: 你具备高级文本分析、关键词提取、数据分类和逻辑判断的能力，能够确保关键字的精炼性、代表性和区分度。
# - Goals: 从用户给定的消费记录中提取精炼的关键字，形成便于检索和判断的分类体系，并确保每个大类都有其对应的关键字集合。
# - Constrains: 提取的关键字应简洁、具有高度的代表性和区分度，避免重复或过于具体的名称，同时应根据实际情况和数据反馈进行调整。
# - OutputFormat: 输出应为“大类：[关键字数组]”的格式，清晰展示每个大类的关键字集合及其对应的消费记录示例。
# - Workflow:
#   1. 接收用户给定的多条消费记录。
#   2. 对每条记录进行详细分析，提取关键信息。
#   3. 根据提取的关键信息，形成关键字集合。
#   4. 将关键字集合分类到相应的大类中。
#   5. 输出每个大类的关键字集合和对应的消费记录示例。
# - Examples:
#   - 例子1：大类：超市，关键字：["超市", "MART", "GROCERY"], 示例：["惠友超市HUIYOUMARTHY", "文利百货超市"]
#   - 例子2：大类：餐饮，关键字：["拉面", "面馆", "兰州拉面"], 示例：["中国兰州拉面店"]
#   - 例子3：大类：服饰，关键字：["服饰", "男装", "女装"], 示例：["时尚服饰店", "经典男装"]
# - Initialization: 在第一次对话中，请直接输出以下：欢迎您使用消费记录关键字提取服务。请提供您的消费记录，我将帮助您从中提取关键字并进行有效分类。现在，请开始输入您的消费记录。    """
class AIAnalyzeAndExtractKeywords:
    """
    AI分析并提取关键词

     AI prompt：
     编写一个Python脚本，该脚本应包含以下功能：
     1. 定义一个元组数组，每个元组包含两个元素：一个类别名称和一个与该类别相关的关键字列表。
     2. 创建一个字典`descriptions`，其中包含每个类别的简短描述和推荐的记账账本。字典的键是类别名称，值是一个包含`description`和`recommended_ledger`字段的字典。
     3. 将元组数组转换为字典列表，每个字典应包含以下字段：
        - `category`：类别名称。
        - `keywords`：与类别相关的关键字列表。
        - `description`：类别的简短描述。
        - `recommended_ledger`：推荐的记账账本。
     4. 将转换后的字典列表序列化为JSON格式的字符串，并确保支持中文字符。
     5. 打印JSON字符串到控制台。
     6. 将JSON字符串保存到名为`data_with_descriptions_and_ledgers.json`的文件中。
     7. 从该文件中读取JSON数据，并打印到控制台以验证数据的一致性。
     请确保JSON字符串和文件中的数据格式清晰、易于阅读。
    """

    # 字典
    data = None
    with open("secret/data.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    assert data, "没有加载json"

    descriptions = None

    with open("secret/descriptions.json", "r", encoding="utf-8") as file:
        descriptions = json.load(file)

    assert descriptions, "没有加载json"

    """
        分类和推荐账本

        为每个类别添加描述和推荐账本

        为了符合beancount账本名称第一个字母必须是大写的要求，将所有类别名称的首字母大写

        https://beancount.github.io/docs/beancount_language_syntax.html
        
        Accounts
        Beancount accumulates commodities in accounts.
        The names of these accounts do not have to be declared before being used in the file,
        they are recognized as “accounts” by virtue of their syntax alone1.
        An account name is a colon-separated list of capitalized words which begin with a letter,
        and whose first word must be one of five account types:
        **Assets Liabilities Equity Income Expenses**
        Each component of the account names begin with a capital letter or a number and are followed by letters,
        numbers or dash (-) characters. All other characters are disallowed.
    """

    def ai_analyze_and_extract_keywords(self):

        assert type(AIAnalyzeAndExtractKeywords.data) is dict

        # 将dict转换为字典列表，并添加描述和推荐账本
        data_dict_list = [
            {
                "category": key,
                "keywords": value,
                "description": AIAnalyzeAndExtractKeywords.descriptions[key][
                    "description"
                ],
                "recommended_ledger": AIAnalyzeAndExtractKeywords.descriptions[key][
                    "recommended_ledger"
                ],
            }
            for key, value in AIAnalyzeAndExtractKeywords.data.items()
        ]

        # 转换为JSON格式的字符串
        json_data = json.dumps(data_dict_list, ensure_ascii=False, indent=4)

        # 打印JSON字符串
        print(json_data)

        # 存储到文件
        with open(
            "secret/data_with_descriptions_and_ledgers.json", "w", encoding="utf-8"
        ) as f:
            f.write(json_data)

        # 从文件读取JSON数据
        with open(
            "secret/data_with_descriptions_and_ledgers.json", "r", encoding="utf-8"
        ) as f:
            loaded_data = json.load(f)

        print(loaded_data)

        assert loaded_data == json.loads(json_data), "数据不一致"
        assert loaded_data is not None, "数据为空"

        # 判断loaded_data里是否包含"category"项里包含 "文化用品"
        assert any(
            loaded_data[i]["category"] == "文化用品" for i in range(len(loaded_data))
        ), "没有找到文化用品"

        # 判断loaded_data里keywords是'文化用品'的项目category是否是'文化用品'
        assert any(
            loaded_data[i]["category"] == "文化用品"
            and "文化用品" in loaded_data[i]["keywords"]
            for i in range(len(loaded_data))
        ), "没有找到文化用品"

        # 给出keywords里包含'豆腐',找出category
        # 并判断category是否是'食品'
        category = next(
            (
                loaded_data[i]["category"]
                for i in range(len(loaded_data))
                for key in loaded_data[i]["keywords"]
                if key in "北京豆汁豆腐店"
            ),
            None,
        )
        assert category is not None, "没有找到豆腐"
        assert category == "食品", "豆腐的category不是食品"

        # 给出keywords里包含'云音乐',找出category
        category = next(
            (
                loaded_data[i]["category"]
                for i in range(len(loaded_data))
                for key in loaded_data[i]["keywords"]
                if key in "网易云音乐支付"
            ),
            None,
        )
        assert category is not None, "云音乐"
        assert category == "数字娱乐", "云音乐的category不是数字娱乐"

        category = next(
            (
                loaded_data[i]["category"]
                for i in range(len(loaded_data))
                for key in loaded_data[i]["keywords"]
                if key in "北京没有的项目"
            ),
            None,
        )
        assert category is None, "北京没有的项目"

        # 给出keywords'易云音乐支付',找出推荐账本
        recommended_ledger = next(
            (
                loaded_data[i]["recommended_ledger"]
                for i in range(len(loaded_data))
                for key in loaded_data[i]["keywords"]
                if key in "网易云音乐支付"
            ),
            None,
        )
        assert recommended_ledger is not None, "没有找到易云音乐支付"
        assert recommended_ledger == "Entertainment娱乐:E数字"

        # 给出keywords'微信零钱通支付',找出推荐账本
        recommended_ledger = next(
            (
                loaded_data[i]["recommended_ledger"]
                for i in range(len(loaded_data))
                for key in loaded_data[i]["keywords"]
                if key in "微信零钱通支付"
            ),
            None,
        )
        assert recommended_ledger is not None, "没有找到微信零钱通支付"
        assert recommended_ledger == "WeChat:E零钱通"


if __name__ == "__main__":
    AIAnalyzeAndExtractKeywords().ai_analyze_and_extract_keywords()
