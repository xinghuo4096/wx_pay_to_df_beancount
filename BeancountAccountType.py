import enum


class AccountType(enum.Enum):
    """
    枚举类型，用于表示账户类型
    五种Assets Liabilities Equity Income Expenses，每行都注释

    """

    # Assets 资产
    Assets = "Assets"
    """
     Assets 资产
    """

    # Liabilities 负债
    Liabilities = "Liabilities"
    # Equity 所有者权益
    Equity = "Equity"
    # Income 收入
    Income = "Income"
    # Expenses 花费
    Expenses = "Expenses"
