import numpy as np
import pandas as pd

if __name__ == "__main__":

    sa = pd.Series([1, 2, 3], index=list(["aaa", "bbb", "ccc"]))
    print(sa)

    # Series
    names = ["aa1", "bb2", "cc3"]
    exems = ["期中", "期末"]
    index = pd.MultiIndex.from_product([names, exems], names=["names", "exems"])
    df = pd.Series([100, 81, 90, 91, 70, 80], index=index)
    print(df)
    print(df["aa1"])
    # 显示df的level
    print(df.index.levels)

    names = ["a", "b", "c"]
    exems = ["期中", "期末"]
    columns = ["语文", "英语", "数学"]
    index = pd.MultiIndex.from_product([names, exems], names=["姓名", "学期成绩"])
    data1 = np.array(range(3 * 2 * 3))
    data2 = data1.reshape(6, 3)
    df2 = pd.DataFrame(data2, index=index, columns=columns)
    print(df2.index.levels)
    print(df2)
    print(df2.loc["a"])
    print(df2.loc["a", "期中"])

    names = ["张工", "李经理"]
    columns = ["语文", "英语", "数学"]
    index = pd.MultiIndex.from_product([names], names=["姓名"])
    # 生成从61开始的2*3个数字
    data1 = np.array(range(61, 61 + 2 * 3))

    data2 = data1.reshape(2, 3)
    df2 = pd.DataFrame(data2, index=index, columns=columns)
    print(df2.index.levels)
    print(df2)
    print(df2.loc["张工"])
    # 显示’张工‘的语文成绩
    print(df2.loc["张工", "语文"].values)
    print(df2.loc["张工", "语文"].values[0])

    # 假设row1和row2是两个Series对象
    row1 = pd.Series({"a": 1, "b": 2, "c": 3})
    row2 = pd.Series({"x": 4, "y": 5, "z": 6})

    # 使用concat合并row1和row2,row2插入到row1的第2列后面
    # axis=1表示按列合并

    merged_row = pd.concat(
        [row1.iloc[:2], row2, row1.iloc[2:]],
        axis=0,
    )

    merged_row2 = pd.concat(
        [row1, row2],
        axis=1,
    )
    # 查看合并后的Series
    print(merged_row)
    print(pd.DataFrame([merged_row]))
    print("go:")
    print(
        pd.DataFrame(
            pd.concat(
                [row1, row2],
                axis=0,
            )
        ).T
    )
    print(
        pd.DataFrame(
            pd.concat(
                [row1, row2],
                axis=1,
            )
        )
    )
