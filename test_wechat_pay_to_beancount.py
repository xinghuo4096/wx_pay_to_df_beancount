from WeChatPayBillToBeancount import WeChatPayBillToBeancount


if __name__ == "__main__":

    # AI处理后的文件，
    # 例如：secret/data_with_descriptions_and_ledgers.json
    # 或者data_with_descriptions_and_ledgers.json

    # 指定CSV文件路径
    # 把指定目录的以'微信'开头的.cvs文件名,合并目录名称后放入列表

    data_with_descriptions_and_ledgers = (
        "secret/data_with_descriptions_and_ledgers.json"
    )
    file_path = "secret"

    beancount_path = "secret/wechat_pay_test.beancount"
    beancount_account_path = "secret/wechat_pay_test.account.beancount"

    json_path = "secret\\wx_pay.json"
    html_path = "secret\\wx_pay.html"
    csv_path = "secret\\wx_pay.csv"
    beancount_html_path = "secret\\wx_pay.beancount.html"
    beancount_csv_path = "secret\\wx_pay.beancount.csv"
    unprocessed_html_path = "secret\\wx_pay.unprocessed.html"
    unprocessed_csv_path = "secret\\wx_pay.unprocessed.csv"

    wx = WeChatPayBillToBeancount(
        file_path=file_path,
        file_data_with_descriptions_and_account=data_with_descriptions_and_ledgers,
        beancount_path=beancount_path,
        beancount_account_path=beancount_account_path,
        json_path=json_path,
        html_path=html_path,
        csv_path=csv_path,
        beancount_html_path=beancount_html_path,
        beancount_csv_path=beancount_csv_path,
        unprocessed_html_path=unprocessed_html_path,
        unprocessed_csv_path=unprocessed_csv_path,
    )

    wx.wechat_pay_to_beancount()
