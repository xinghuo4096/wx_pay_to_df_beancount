from datetime import date
from decimal import Decimal
from beancount.core import data
from beancount.parser.printer import EntryPrinter
from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame


def wechat_pay_to_beancount(
    wx_csv: WeChatPayBillToDataFrame,
    beancount_path="secret/wechat_pay_test.beancount",
    beancount_account_path="secret/wechat_pay_test_account.beancount",
):
    if wx_csv and not wx_csv.beancount_df.empty:

        entry = data.new_metadata(beancount_path, 2024)
        all_transactions = []
        all_accounts = {}

        # ('meta', Meta),
        # ('date', datetime.date)]
        # ('flag', Flag),
        # ('payee', Optional[str]),
        # ('narration', str),
        # ('tags', Set),
        # ('links', Set),
        # ('postings', List[Posting])])
        # 标签必须以“#”开头，链接必须以“^”开头。
        for index, bdf in wx_csv.beancount_df.iterrows():
            tr1 = data.Transaction(
                meta=entry,
                date=bdf["过账交易日期"],
                flag=bdf["过账标记"],
                payee=bdf["交易对手"],
                narration=bdf["过账的备注"],
                tags=[],
                links=[],
                postings=[],
            )
            account1 = f"{bdf['过账1的账本类型']}:{bdf['过账1的账本']}"
            posting1 = data.create_simple_posting(
                tr1, account1, bdf["过账1的金额"], bdf["过账1的货币类型"]
            )

            account2 = f"{bdf['过账2的账本类型']}:{bdf['过账2的账本']}"
            posting2 = data.create_simple_posting(
                tr1, account2, bdf["过账2的金额"], bdf["过账2的货币类型"]
            )

            if posting1 and posting2:
                all_transactions.append(tr1)

                all_accounts.setdefault(account1, account1)
                all_accounts.setdefault(account2, account2)

        # TODO 加入ai生成的账本说明

        ep = EntryPrinter()
        entry_string = "\n".join([ep(t1) for t1 in all_transactions])
        with open(beancount_path, "w", encoding="utf-8") as f:
            f.write(entry_string)

        # all_accounts按键排序
        all_accounts = sorted(all_accounts.values())
        account_str = "\n".join(
            [f"1949-10-01 open  {account}" for account in all_accounts]
        )

        with open(beancount_account_path, "w", encoding="utf-8") as f:
            f.write(account_str)


if __name__ == "__main__":

    # AI处理后的文件，目前必须放到secret/data_with_descriptions_and_ledgers.json

    # 指定CSV文件路径
    # 把指定目录的以'微信'开头的.cvs文件名,合并目录名称后放入列表
    file_path = "secret"

    wx_csv = WeChatPayBillToDataFrame(file_path)

    df = wx_csv.read_wx_pay_to_df()
    wx_csv.prepare_df_for_beancount()

    wx_csv.check_data()

    wechat_pay_to_beancount(wx_csv, "secret/wechat_pay_test.beancount")

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
