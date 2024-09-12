from WeChatPayBillTools import get_account_by_keyword

if __name__ == "__main__":
    account = get_account_by_keyword("微信零钱通支付")
    assert account == "WeChat:E零钱通"

    account = get_account_by_keyword("网易云音乐年卡")
    assert account == "Entertainment娱乐:E数字"

    account = get_account_by_keyword("黄原牛肉拉面支付")
    assert account == "Food食物:E餐饮"

    account = get_account_by_keyword("没有的项目")
    assert account == None
