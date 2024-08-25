from DataFrameToBeancount import get_account_by_keyword

if __name__ == "__main__":
    account = get_account_by_keyword("微信")
    assert account == "微信"
