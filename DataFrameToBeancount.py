import json
from datetime import date
from decimal import Decimal
import traceback
from beancount.core import data
from beancount.parser.printer import EntryPrinter
import pandas as pd

from BeancountAccountType import AccountType
from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame

import json
import os


class DataFrameToBeancount:
    def __init__(self, config_path="config/config.json"):
        # 检查config.json文件是否存在
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as config_file:
                config_data = json.load(config_file)

            # 必需的配置键列表
            required_keys = [
                "path_file",
                "path_data_with_descriptions_and_account",
                "path_beancount",
                "path_beancount_account",
                "path_dataframe_json",
                "path_dataframe_html",
                "path_dataframe_csv",
                "path_beancount_html",
                "path_beancount_csv",
                "path_unprocessed_html",
                "path_unprocessed_csv",
            ]

            # 检查所有必需的配置项是否都已提供
            for key in required_keys:
                if key not in config_data:
                    raise KeyError(f"配置文件中缺少必需的键: {key}")

            # 如果所有必需的配置项都存在，赋值给对象的属性
            self.path_file = config_data["path_file"]
            self.path_data_with_descriptions_and_account = config_data[
                "path_data_with_descriptions_and_account"
            ]
            self.path_beancount = config_data["path_beancount"]
            self.path_beancount_account = config_data["path_beancount_account"]
            self.path_dataframe_json = config_data["path_dataframe_json"]
            self.path_dataframe_html = config_data["path_dataframe_html"]
            self.path_dataframe_csv = config_data["path_dataframe_csv"]
            self.path_beancount_html = config_data["path_beancount_html"]
            self.path_beancount_csv = config_data["path_beancount_csv"]
            self.path_unprocessed_html = config_data["path_unprocessed_html"]
            self.path_unprocessed_csv = config_data["path_unprocessed_csv"]

            # 读取JSON文件并转换为Pandas DataFrame。
            self.df = pd.read_csv(
                self.path_dataframe_csv, encoding="utf-8", parse_dates=["交易时间"]
            )
            self.unprocessed_df = pd.DataFrame()

            #
            with open(
                self.path_data_with_descriptions_and_account, "r", encoding="utf-8"
            ) as file:
                self.keyword_category_mapping = json.load(file)

            # beancount相关
            self.beancount_df = pd.DataFrame()
            self.all_accounts = {}
            self.all_transactions = []

            # 缺省
            self.default_account_max_amount = 100.00

        except json.JSONDecodeError:
            raise ValueError("配置文件格式错误，请检查JSON格式")
        except KeyError as e:
            raise ValueError(f"配置文件中缺少必需的键: {e}")
        except Exception as e:
            raise ValueError(f"读取配置文件时发生错误: {e}")

    def to_beancount(self):
        if not self.df.empty:

            entry = data.new_metadata(self.path_beancount, 2024)

            # ('meta', Meta),
            # ('date', datetime.date)]
            # ('flag', Flag),
            # ('payee', Optional[str]),
            # ('narration', str),
            # ('tags', Set),
            # ('links', Set),
            # ('postings', List[Posting])])
            # 标签必须以“#”开头，链接必须以“^”开头。
            for index, bdf in self.beancount_df.iterrows():
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
                    self.all_transactions.append(tr1)

                    self.all_accounts.setdefault(account1, account1)
                    self.all_accounts.setdefault(account2, account2)
            return self.all_accounts, self.all_transactions
        else:
            return None, None

    def save_beancount(self):
        ep = EntryPrinter()
        entry_string = "\n".join([ep(t1) for t1 in self.all_transactions])
        with open(self.path_beancount, "w", encoding="utf-8") as f:
            f.write(entry_string)

        # all_accounts按键排序
        # TODO 加入ai生成的每个账本的用途说明
        all_accounts = sorted(all_accounts.values())
        account_str = "\n".join(
            [f"1949-10-01 open  {account}" for account in all_accounts]
        )

        with open(self.path_beancount_account, "w", encoding="utf-8") as f:
            f.write(account_str)

    # 处理df，为beancount格式做准备的df格式文件
    def prepare_df_for_beancount(self) -> tuple[pd.DataFrame, pd.DataFrame]:

        wxdf_list = []
        # 建立一个新的wxdf，空的df，
        # colums为:
        # date,交易日期,默认为空。
        # time,交易时间，默认为空。
        #
        # flag，交易状态，默认'!'，含义是稍后检查该交易。例如：是'*'，表示已检查。其他见`beancount.core.flags`。
        #
        # payee，收款人，默认空。
        # narration，交易概要。默认''。
        # posting1，过账条目1，默认空。
        # posting2，过账条目2，默认空。
        #
        # posting1_account_type，账户类型，默认空。五种Assets Liabilities Equity Income Expenses
        # posting1_amount，金额，默认0。
        # posting1_currency，货币类型，默认'CNY'，中国元。
        #
        # posting2_account_type，账户类型，默认空。五种Assets Liabilities Equity Income Expenses
        # posting2_amount，金额，默认0。
        # posting2_currency，货币类型，默认'CNY'，中国元。

        wxdf = pd.DataFrame(
            columns=[
                "date",
                "time",
                "flag",
                "payee",
                "narration",
                "posting1_account_type",
                "posting1_account",
                "posting1_currency",
                "posting1_amount",
                "posting2_account_type",
                "posting2_account",
                "posting2_amount",
                "posting2_currency",
            ]
        )
        # 记录未处理的wxdf内容的变量
        unprocessed_wxdf_list = []
        # unprocessed_wxdf和df结构相同
        unprocessed_wxdf = pd.DataFrame(columns=self.df.columns)

        print("开始处理微信支付账单df for beancount")
        for index, row in self.df.iterrows():
            # 交易日期
            pay_date = row["交易时间"].date()
            # 交易时间
            pay_time = row["交易时间"].time()

            # 过账1的账本
            posting1_account = ""
            # 过账1的金额
            posting1_account_amount = row["金额(元)"]
            # 过账1的货币
            posting1_currency = row["货币类型"]

            # 过账2的账本
            posting2_account = ""
            # 过账2的金额
            posting2_account_amount = row["金额(元)"]
            # 过账2的货币
            posting2_currency = row["货币类型"]

            # 交易的对手，支出时为收款人，收入时为付款人，为'/'时表示零钱
            counterparty = row["交易对方"]
            # 支付的方式，支出时为付款方式，收入时为收款方式，为'/'时表示零钱
            pay_account = row["支付方式"]

            # 交易的商品
            product = row["商品"]

            # 交易的备注
            narration = ""

            # 交易类型
            trade_type = row["交易类型"]

            # 收入或支出，row["收/支"]，分为收入，支出，'/'表示零钱
            income_or_expense = row["收/支"]

            flag = "!"
            postings = []

            if posting1_account_amount <= 0 and posting2_account_amount <= 0:
                raise ValueError(f"金额字段有异常值{posting1_account_amount}")

            counterparty, pay_account, product = self.clear_data1(
                counterparty, pay_account, product
            )

            # TODO 此处row['备注']如果不是'/',可用加到 narration ，加一个变量note ''或 '备注:row['备注']', narration里{note}
            match income_or_expense:
                case "支出":
                    match trade_type:
                        case "扫二维码付款" | "商户消费" | "转账":
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword(pay_account)
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Expenses.value
                            posting2_account = self.get_account_by_keyword(counterparty)
                            posting2_account_amount = posting2_account_amount

                            if (
                                posting2_account is None
                                and posting2_account_amount
                                < self.default_account_max_amount
                            ):
                                posting2_account = (
                                    WeChatPayBillToDataFrame.DEFAULT_ACCOUNT_EXPENSES
                                )
                            flag = "*"

                            # 生成过账备注信息
                            if product != "收款方备注:二维码收款":
                                narration = f"{trade_type}，从：{pay_account}，给：{counterparty}，购买：{product}"
                            else:
                                narration = f"{trade_type}，从：{pay_account}，给：{counterparty}"

                        # 处理微信红包
                        case wxhb if type(wxhb) is str and wxhb.startswith("微信红包"):
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword(pay_account)
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Expenses.value
                            posting2_account = self.get_account_by_keyword(counterparty)
                            posting2_account_amount = posting2_account_amount

                            flag = "*"

                            narration = (
                                f"微信红包收入,从：{pay_account}，给:{counterparty}"
                            )
                        case _:
                            posting1 = posting2 = ""
                            raise ValueError(f"支出,未处理的交易类型{trade_type}")

                case "收入":
                    match trade_type:
                        # 处理退款
                        case tk if type(tk) is str and tk.endswith("退款"):
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword(pay_account)
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Expenses.value
                            posting2_account = self.get_account_by_keyword(counterparty)
                            posting2_account_amount = -1 * posting2_account_amount

                            flag = "*"
                            narration = (
                                f"收到退款，从：{counterparty}，退款给:{pay_account},"
                            )
                        # 处理转账收入
                        case "转账" | "其他" | "二维码收款" | "微信红包":
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword(pay_account)
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Income.value
                            posting2_account = self.get_account_by_keyword(counterparty)
                            posting2_account_amount = -1 * posting2_account_amount

                            if (
                                posting2_account == None
                                and posting1_account_amount < 10
                            ):
                                posting2_account = (
                                    WeChatPayBillToDataFrame.DEFAULT_ACCOUNT_INCOME
                                )

                            flag = "*"

                            narration = f"{trade_type}，从：{counterparty}，给:{pay_account}，商品:{product}"
                        case _:
                            postings = []
                            posting1 = posting2 = ""
                            raise ValueError(f"收入,未处理的交易类型:{trade_type}")

                case "/":
                    match trade_type:
                        case "零钱提现":
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword("微信零钱")
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = self.get_account_by_keyword(pay_account)
                            posting2_account_amount = posting2_account_amount

                            flag = "*"
                            narration = f"微信零钱提现，给:{pay_account}"
                        # 处理零钱通转入
                        case lqt_in if type(lqt_in) is str and lqt_in.startswith(
                            "转入零钱通"
                        ):
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword("微信零钱通")
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = self.get_account_by_keyword(pay_account)
                            posting2_account_amount = -1 * posting2_account_amount

                            flag = "*"
                            narration = f"从：{pay_account}，转入给:微信零钱通"

                        # 处理零钱通转出
                        case lqt_out if type(lqt_out) is str and lqt_out.startswith(
                            "零钱通转出"
                        ):

                            posting1_account_type = AccountType.Assets.value
                            posting1_account = self.get_account_by_keyword(pay_account)
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = self.get_account_by_keyword(counterparty)
                            posting2_account_amount = posting2_account_amount

                            flag = "*"

                            narration = f"零钱通转出，给:{counterparty}"

                        case _:
                            posting1 = posting2 = ""
                            raise ValueError(f"/ ,未处理的交易类型{trade_type}")
                case _:
                    raise ValueError("收/支字段有异常值")

            if posting1_account and posting2_account:
                if counterparty == "/":
                    counterparty = "零钱"
                wx_pay_df_beancount_record = {
                    "过账交易日期": pay_date,
                    "过账交易时间": pay_time,
                    "过账标记": flag,
                    "交易对手": counterparty,
                    "过账1的账本类型": posting1_account_type,
                    "过账1的账本": posting1_account,
                    "过账1的金额": posting1_account_amount,
                    "过账1的货币类型": posting1_currency,
                    "过账2的账本类型": posting2_account_type,
                    "过账2的账本": posting2_account,
                    "过账2的金额": posting2_account_amount,
                    "过账2的货币类型": posting2_currency,
                    "过账的备注": narration,
                }
                wxdf_list.append(pd.DataFrame([wx_pay_df_beancount_record]))
                self.df.loc[index, "已加入记账本"] = "🆗"
            else:
                _row = pd.DataFrame([row])
                unprocessed_wxdf_list.append(_row)

        wxdf = pd.concat(wxdf_list, ignore_index=True)
        wxdf = wxdf.reset_index(drop=True)

        unprocessed_wxdf = None
        if len(unprocessed_wxdf_list) > 0:
            unprocessed_wxdf = pd.concat(unprocessed_wxdf_list, ignore_index=True)

        self.beancount_df = wxdf
        self.unprocessed_df = unprocessed_wxdf
        print("处理完成")
        return wxdf, unprocessed_wxdf

    def save_to_beancount(self):
        self.beancount_df.to_html(self.path_beancount_html, index=True)
        self.beancount_df.to_csv(
            self.path_beancount_csv, index=True, encoding="utf-8-sig"
        )
        if self.unprocessed_df and not self.unprocessed_df.empty:

            print("有未处理的内容：unprocessed_df is empty.")
            self.unprocessed_df.to_html(self.path_unprocessed_html, index=True)
            self.unprocessed_df.to_csv(
                self.path_unprocessed_csv, index=True, encoding="utf-8-sig"
            )
        else:
            print("全部处理OK.unprocessed_df is empty.")

    def ai_get_account_by_keyword(keyword):
        ## TODO：给定自己定义好的多个账户让ai选择
        # ，比如50个账户，问ai，给出最合适记账的账户，比如：易云音乐支付， 问ai后，ai从给出选择列表里选，给出最合适的账户'Entertainment娱乐:E数字'。
        pass

    def get_account_by_keyword(
        self, keyword, default_is_None: bool = True, default="默认账本:{keyword}"
    ):
        """
        根据关键字，返回过账记录的账本。
        :param keyword: 关键字
        :return: 账本
        """

        assert self.keyword_category_mapping is not None, "数据为空"

        # 给出keywords，如：'网易云音乐支付',找出推荐账本
        recommended_ledger = None

        for mapping in self.keyword_category_mapping:
            if any(key in keyword for key in mapping["keywords"]):
                recommended_ledger = mapping["recommended_ledger"]
                break

        # 如果没有找到匹配的推荐账本，recommended_ledger将保持为None

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

    def clear_data1(self, counterparty, pay_account, product):
        """
        清洗数据,如果是"/"则替换为微信零钱，如果包含"则替换为'

        """
        if pay_account == "/":
            pay_account = "微信零钱"
        if counterparty == "/":
            counterparty = "微信零钱"
        if product == "/":
            product = "微信零钱"

        pay_account = pay_account.replace('"', "'")
        counterparty = counterparty.replace('"', "'")
        product = product.replace('"', "'")
        return counterparty, pay_account, product


if __name__ == "__main__":
    # 使用示例
    try:
        my_instance = DataFrameToBeancount()
        assert my_instance

        account = my_instance.get_account_by_keyword("网易云音乐支付")
        assert account, "获取账本失败"
        print(f"推荐账本: {account}")

        df1, df2 = my_instance.prepare_df_for_beancount()
        assert not df1.empty
        print(df1.head())
        print(df1.tail())
        print(df1.shape)
        print(df2)
    except Exception as e:
        print(f"初始化失败: {e}")
        traceback.print_exc()
