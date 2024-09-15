from DataFrameToBeancount import save_beancount, to_beancount
from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame


class WeChatPayBillToBeancount:
    """
    微信账单转beancount

    AI处理后的文件，目前必须放到secret/data_with_descriptions_and_ledgers.json

    file_path: 微信账单文件路径，指定CSV文件路径，把指定目录的以'微信'开头的.cvs文件名

    beancount_path:转换后 beancount文件路径

    beancount_account_path: 根据微信支付文件推荐beancount账户文件路径

    json_path: 微信账单转换为json文件路径

    html_path: 微信账单转换html文件路径

    csv_path: 微信账单转换csv文件路径

    beancount_html_path: beancount html文件路径

    beancount_csv_path: beancount csv文件路径

    unprocessed_html_path: 无法处理的内容的html文件路径


    """

    def __init__(
        self,
        file_path="secret",
        file_data_with_descriptions_and_account="secret\\data_with_descriptions_and_ledgers.json",
        beancount_path="secret/wechat_pay_test.beancount",
        beancount_account_path="secret/wechat_pay_test.account.beancount",
        json_path="secret\\wx_pay.json",
        html_path="secret\\wx_pay.html",
        csv_path="secret\\wx_pay.csv",
        beancount_html_path="secret\\wx_pay.beancount.html",
        beancount_csv_path="secret\\wx_pay.beancount.csv",
        unprocessed_html_path="secret\\wx_pay.unprocessed.html",
        unprocessed_csv_path="secret\\wx_pay.unprocessed.csv",
    ):
        self.file_path = file_path
        self.beancount_path = beancount_path
        self.beancount_account_path = beancount_account_path
        self.json_path = json_path
        self.html_path = html_path
        self.csv_path = csv_path
        self.beancount_html_path = beancount_html_path
        self.beancount_csv_path = beancount_csv_path
        self.unprocessed_html_path = unprocessed_html_path
        self.unprocessed_csv_path = unprocessed_csv_path
        self.file_data_with_descriptions_and_account = (
            file_data_with_descriptions_and_account
        )

    def wechat_pay_to_beancount(self):

        wx_csv = WeChatPayBillToDataFrame(self.file_path)

        wx_csv.prepare_df_for_beancount()

        wx_csv.check_data()

        all_accounts, all_transactions = to_beancount(wx_csv)

        assert all_accounts, "没有推测出账户account"
        assert all_transactions, "没有交易过账"
        assert wx_csv.beancount_df is not None, "beancount_df is None"
        assert wx_csv.beancount_df.head() is not None, "beancount_df.head() is None"

        save_beancount(
            self.beancount_path,
            self.beancount_account_path,
            all_transactions,
            all_accounts,
        )

        wx_csv.save_to_file(
            self.json_path,
            self.html_path,
            self.csv_path,
            self.beancount_html_path,
            self.beancount_csv_path,
            self.unprocessed_html_path,
            self.unprocessed_csv_path,
        )
