from decimal import Decimal, InvalidOperation
import os
import pandas as pd

from BeancountAccountType import AccountType

class WeChatPayBillToDataFrame:
    """
    微信支付账单转DataFrame
    default_account = f"{AccountType.Expenses.value}:Live日常生活:小额默认账本"

    """
    DEFAULT_ACCOUNT_EXPENSES = "Live日常生活:小额支出默认账本"
    """
        默认账本，用于类型是支出时，找不到账本的情况下
    """
    DEFAULT_ACCOUNT_INCOME = "小额收入:默认账本"

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

    def __init__(
        self,
        file_path: str = "secret",
        file_data_with_descriptions_and_account="secret\\data_with_descriptions_and_ledgers.json",
    ):
        self.file_list = [
            os.path.join(file_path, f)
            for f in os.listdir(file_path)
            if f.startswith("微信") and f.endswith(".csv")
        ]
        self.df = None
        self.beancount_df = None
        self.unprocessed_df = None

        self.default_account_max_amount = 100.00
        """
        定义交易时支出,找不到账本情况下,低于最大的金额,则使用默认账本
        """

        self.file_data_with_descriptions_and_account = (
            file_data_with_descriptions_and_account
        )

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
