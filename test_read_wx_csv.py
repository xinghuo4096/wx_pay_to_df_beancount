from WeChatPayBillToDataFrame import WeChatPayBillToDataFrame


if __name__ == "__main__":

    # 指定CSV文件路径
    file_path = "secret"
    # 把指定目录的以'微信'开头的.cvs文件名,合并目录名称后放入列表

    wx_csv = WeChatPayBillToDataFrame(file_path)

    df = wx_csv.read_wx_pay_to_df()
    wx_csv.prepare_df_for_beancount()

    wx_csv.check_data()

    wx_csv.save_to_file()

    print(wx_csv.beancount_df.head())
    print(wx_csv.beancount_df.tail())

    assert wx_csv.beancount_df is not None, "beancount_df is None"
    assert wx_csv.beancount_df.head() is not None, "beancount_df.head() is None"
