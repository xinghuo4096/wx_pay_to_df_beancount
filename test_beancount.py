from datetime import date
from decimal import Decimal
from beancount.core import data
from beancount.parser.printer import EntryPrinter


entry = data.new_metadata("test.beancount", 2024)

# ('meta', Meta),
# ('date', datetime.date)]
# ('flag', Flag),
# ('payee', Optional[str]),
# ('narration', str),
# ('tags', Set),
# ('links', Set),
# ('postings', List[Posting])])
# 标签必须以“#”开头，链接必须以“^”开头。
tr1 = data.Transaction(
    entry,
    date(2024, 8, 22),
    "*",
    "开发大楼星巴克",
    "参加星巴克活动",
    ["tag1", "tag2"],
    ["link1", "link2"],
    [],
)


units = data.Amount(Decimal("-230.00"), "CNY")
posting1 = data.Posting("Assets:A中国银行:A借记卡888", units, None, None, None, None)

tr1.postings.append(posting1)

posting2 = data.create_simple_posting(tr1, "Expenses:E食物:E咖啡", "230.00", "CNY")

assert entry is not None
assert posting1 is not None
assert isinstance(tr1, data.Transaction)
assert isinstance(posting1, data.Posting)
assert isinstance(posting2, data.Posting)
assert tr1.postings[0] is posting1
assert tr1.postings[1] is posting2

print(tr1.meta["filename"])

ep = EntryPrinter()
entry_string = ep(tr1)
print(entry_string)
