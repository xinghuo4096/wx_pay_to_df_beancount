import os
import pandas as pd
from test_wxpay_tools import parse_amount_with_currency
from test_wxpay_account import get_account_by_keyword
from DataFrameToBeancount import AccountType


class WeChatPayBillToDataFrame:
    """
    微信支付账单转DataFrame

    """

    # 列的数据类型，根据列名进行合理的假设

    dtypes = {
        "交易时间": "str",  # 假设交易时间是datetime类型
        "交易类型": "category",  # 假设交易类型是分类数据
        "交易对方": "str",  # 假设交易对方是字符串
        "商品": "str",  # 假设商品名称是字符串
        "收/支": "category",  # 假设收/支是分类数据，例如"收入"或"支出"
        "金额(元)": "str",  # 假设金额是浮点数
        "支付方式": "category",  # 假设支付方式是分类数据
        "当前状态": "category",  # 假设当前状态是分类数据
        "交易单号": "str",  # 假设交易单号是字符串
        "商户单号": "str",  # 假设商户单号是字符串
        "备注": "str",  # 假设备注是字符串
    }
    """
    微信支付账单的内部类型，供pd用
    """

    def __init__(self, file_path: str = "secret"):
        self.file_list = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if f.startswith("微信") and f.endswith(".csv")
        ]
        self.df = None
        self.beancount_df = None
        self.unprocessed_df = None

        self.default_account = f"{AccountType.Expenses}:Live日常生活:小额默认账本"
        """
        默认账本，用于类型是支出时，找不到账本的情况下
        """

        self.default_account_max_amount = 100.00
        """
        定义交易时支出,找不到账本情况下,低于最大的金额,则使用默认账本
        """

    def process(self):
        """
        处理微信支付账单，生成DataFrame
        """
        # 读取所有微信支付账单文件
        for file_path in self.file_list:
            # 读取微信支付账单文件
            df = pd.read_csv(file_path, skiprows=15, header=0, dtype=self.dtypes)
            # 将金额列转换为浮点数
            df["金额(元)"] = df["金额(元)"].apply(parse_amount_with_currency)
            # 将交易时间列转换为datetime类型
        self.max_amount = 0
        """
        最大的金额，用于计算最大金额的百分比
        """

    def check_wx_csv_16_17(file_path: str) -> bool:
        """
        检查文件是否为微信支付账单</br>
        检查第16行是否包含"微信支付账单明细列表"</br>
        检查第17行是否是预期的表头</br>
        预期表头为："交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注"
        """
        line16_ok = line17_ok = False

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        line16 = lines[15].strip()
        line17 = lines[16].strip()

        # 检查第16行是否包含"微信支付账单明细列表"
        # 由于索引从0开始，所以第16行对应索引15
        line_16_content = line16.strip()
        if "微信支付账单明细列表" in line_16_content:
            line16_ok = True
        else:
            print("第16行不包含文本：'微信支付账单明细列表'")
            line16_ok = False

        # 检查第17行是否是预期的表头
        expected_header = "交易时间,交易类型,交易对方,商品,收/支,金额(元),支付方式,当前状态,交易单号,商户单号,备注"
        line_17_content = line17.strip()  # 第17行对应索引16
        if line_17_content == expected_header:
            line17_ok = True
        else:
            print("第17行不是预期的表头")
            line17_ok = False
        return line16_ok and line17_ok

    # 处理原始微信账单为df格式
    def read_wx_pay_to_df(self) -> pd.DataFrame:
        wxdf = pd.DataFrame()
        for file_path in self.file_list:
            print(f"正在处理文件：{file_path} to df")
            # 检查文件是否为微信支付账单
            if not WeChatPayBillToDataFrame.check_wx_csv_16_17(file_path):
                print("文件格式不正确，跳过处理")
                raise ValueError("文件格式检查失败，不是微信支付账单，跳过处理。")
                continue

            # 读取CSV文件，指定表头在第17行，以及列的数据类型
            df = pd.read_csv(
                file_path,
                header=16,
                dtype=WeChatPayBillToDataFrame.dtypes,
            )

            # 清除\\t字符
            df = df.replace("\t", " ", regex=True)

            # 尝试将交易时间转换为datetime类型
            df["交易时间"] = pd.to_datetime(df["交易时间"], errors="coerce")

            # 把df["金额(元)"]处理为，一列是金额，一列是币种
            result_series = df["金额(元)"].apply(
                lambda x: parse_amount_with_currency(x)
            )

            # 使用列表推导式和解包来分别创建两个新的 Series
            # 这将自动把元组中的金额和货币类型分别提取到两个列表中
            amounts, currencies = zip(*result_series)

            # 在第金额列后面插入新的列
            if "金额(元)" in df.columns:
                df.insert(
                    df.columns.get_loc("金额(元)") + 1,
                    "货币类型",
                    pd.Series(currencies),
                )
            df["金额(元)"] = pd.Series(amounts)
            df["货币类型"] = pd.Series(currencies)

            # 处理微信支付的数据
            df = df.sort_values(by="交易时间")
            df = df.reset_index(drop=True)

            # 增加已经加入记账本的标记
            df.insert(loc=1, column="已加入记账本", value="⚠")

            # 如果dataframe 是空集，wxdf=df，不是则合并

            if wxdf.empty:
                wxdf = df
            else:
                wxdf = pd.concat([wxdf, df], ignore_index=True)
                wxdf.drop_duplicates(inplace=True)
                wxdf.reset_index(drop=True, inplace=True)
        self.df = wxdf
        return wxdf

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

            if pay_account == "/":
                pay_account = "零钱"
            if counterparty == "/":
                counterparty = "零钱"
            if product == "/":
                product = "零钱"

            match income_or_expense:
                case "支出":
                    match trade_type:
                        case "扫二维码付款" | "商户消费" | "转账":
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = get_account_by_keyword(pay_account)
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Expenses.value
                            posting2_account = get_account_by_keyword(counterparty)
                            posting2_account_amount = posting2_account_amount

                            if (
                                posting2_account is None
                                and posting2_account_amount
                                < self.default_account_max_amount
                            ):
                                posting2_account = self.default_account
                            flag = "*"

                            # 生成过账备注信息
                            if product != "收款方备注:二维码收款":
                                narration = f"{trade_type}，从：{pay_account}，给：{counterparty}，购买：{product}"
                            else:
                                narration = f"{trade_type}，从：{pay_account}，给：{counterparty}"

                        # 处理微信红包
                        case wxhb if type(wxhb) is str and wxhb.startswith("微信红包"):
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = get_account_by_keyword(pay_account)
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Expenses.value
                            posting2_account = get_account_by_keyword("微信红包")
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
                            posting1_account = get_account_by_keyword(pay_account)
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Income.value
                            posting2_account = get_account_by_keyword(counterparty)
                            posting2_account_amount = -1 * posting2_account_amount

                            flag = "*"
                            narration = (
                                f"收到退款，从：{counterparty}，退款给:{pay_account},"
                            )
                        # 处理转账收入
                        case "转账" | "其他" | "二维码收款" | "微信红包":
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = get_account_by_keyword(pay_account)
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Income.value
                            posting2_account = get_account_by_keyword(counterparty)
                            posting2_account_amount = -1 * posting2_account_amount

                            if (
                                posting2_account == None
                                and posting1_account_amount < 10
                            ):
                                posting2_account = "小额收入:默认小额收入"

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
                            posting1_account = get_account_by_keyword("零钱")
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = get_account_by_keyword(pay_account)
                            posting2_account_amount = posting2_account_amount

                            flag = "*"
                            narration = f"微信零钱提现，给:{pay_account}"
                        # 处理零钱通转入
                        case lqt_in if type(lqt_in) is str and lqt_in.startswith(
                            "转入零钱通"
                        ):
                            posting1_account_type = AccountType.Assets.value
                            posting1_account = get_account_by_keyword("零钱通")
                            posting1_account_amount = posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = get_account_by_keyword(pay_account)
                            posting2_account_amount = -1 * posting2_account_amount

                            flag = "*"
                            narration = f"从：{pay_account}，转入给:微信零钱通"

                        # 处理零钱通转出
                        case lqt_out if type(lqt_out) is str and lqt_out.startswith(
                            "零钱通转出"
                        ):
                            if counterparty == "/":
                                counterparty = "零钱"

                            posting1_account_type = AccountType.Assets.value
                            posting1_account = get_account_by_keyword("微信零钱通")
                            posting1_account_amount = -1 * posting1_account_amount

                            posting2_account_type = AccountType.Assets.value
                            posting2_account = get_account_by_keyword(counterparty)
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

    # 存储df到json和html文件
    # TODO 直接生成beancount文件
    # TODO 写一个2.6.4的https://beancount.github.io/docs/importing_external_data.html#writing-an-importer
    def save_to_file(
        self,
        json_path="secret\\wx1.json",
        html_path="secret\\wx1.html",
        csv_path="secret\\new_wx1.csv",
        beancount_html_path="secret\\wxdf1.html",
        beancount_csv_path="secret\\new_wxdf1.csv",
        unprocessed_html_path="secret\\unprocessed_wxdf1.html",
        unprocessed_csv_path="secret\\new_unprocessed_wxdf1.csv",
    ):
        """
        将df保存到json和html文件
        """
        self.df.to_json(json_path, orient="records", force_ascii=False, lines=True)
        self.df.to_html(html_path, index=True)
        self.df.to_csv(csv_path, index=True, encoding="utf-8-sig")

        self.beancount_df.to_html(beancount_html_path, index=True)
        self.beancount_df.to_csv(beancount_csv_path, index=True, encoding="utf-8-sig")
        if self.unprocessed_df is not None and not self.beancount_df.empty:
            self.unprocessed_df.to_html(unprocessed_html_path, index=True)
            self.unprocessed_df.to_csv(
                unprocessed_csv_path, index=True, encoding="utf-8-sig"
            )

    def check_data(self):
        """

        检查金额列的数据是否合理（例如，金额不应该为负）
        """
        if "金额(元)" in self.df.columns:
            if (self.df["金额(元)"] < 0).any():
                print("发现负数金额，这可能是不合理的。")
                raise ValueError("发现负数金额，这可能是不合理的。")
        else:
            print("未找到金额列，请检查数据。")
            raise ValueError("未找到金额列，请检查数据。")
