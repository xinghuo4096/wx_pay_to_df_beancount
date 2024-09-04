from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame


if __name__ == "__main__":

    # AI处理后的文件，目前必须放到secret/data_with_descriptions_and_ledgers.json

    # 指定CSV文件路径
    # 把指定目录的以'微信'开头的.cvs文件名,合并目录名称后放入列表
    file_path = "secret"

    wx_csv = WeChatPayBillToDataFrame(file_path)

    df = wx_csv.read_wx_pay_to_df()
    wx_csv.prepare_df_for_beancount()

    wx_csv.check_data()

    print(wx_csv.beancount_df.head())
    print(wx_csv.beancount_df.tail())

    wx_csv.save_to_file(
        json_path="secret\\wx_pay.json",
        html_path="secret\\wx_pay.html",
        csv_path="secret\\wx_pay.csv",
        beancount_html_path="secret\\wx_pay.beancount.html",
        beancount_csv_path="secret\\wx_pay.beancount.csv",
        unprocessed_html_path="secret\\wx_pay.unprocessed.html",
        unprocessed_csv_path="secret\\wx_pay.unprocessed.csv",
    )

    assert wx_csv.beancount_df is not None, "beancount_df is None"
    assert wx_csv.beancount_df.head() is not None, "beancount_df.head() is None"
