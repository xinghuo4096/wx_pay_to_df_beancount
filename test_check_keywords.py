import json
from collections import Counter
from collections import defaultdict


def check():
    # 从文件读取JSON数据
    with open(
        "secret/data_with_descriptions_and_ledgers.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    # 创建一个字典来跟踪每个分类下的关键词
    category_keywords = defaultdict(lambda: defaultdict(int))

    # 遍历每条数据
    for entry in data:
        category = entry["category"]
        for keyword in entry["keywords"]:
            category_keywords[category][keyword] += 1

    # 创建一个字典来跟踪每个关键词所属的分类
    keyword_to_category = {}

    # 填充关键词到分类的映射
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            keyword_to_category[keyword] = category

    # 找出每个分类下重复的关键词
    repeated_keywords_by_category = {}
    for category, keywords in category_keywords.items():
        repeated_keywords = {
            keyword: count for keyword, count in keywords.items() if count > 1
        }
        if repeated_keywords:
            repeated_keywords_by_category[category] = repeated_keywords

    # 打印每个分类下的重复关键词及其出现次数
    for category, keywords in repeated_keywords_by_category.items():
        print(f"分类 '{category}' 下的重复关键词及其出现次数:")
        for keyword, count in keywords.items():
            print(f"  关键词 '{keyword}' 出现了 {count} 次")

    # 检查所有分类的关键词之间是否存在包含关系并打印
    all_keywords = set(keyword_to_category.keys())
    sorted(all_keywords)

    for keyword in all_keywords:
        for other_keyword in all_keywords:
            if keyword != other_keyword and keyword in other_keyword:
                # 获取两个关键词各自的分类
                keyword_category = keyword_to_category[keyword]
                other_keyword_category = keyword_to_category[other_keyword]
                print(
                    f"分类 '{keyword_category}' 中，关键词 '{keyword}' 包含在分类 '{other_keyword_category}' 的关键词 '{other_keyword}' 中。"
                )


if __name__ == "__main__":
    check()
