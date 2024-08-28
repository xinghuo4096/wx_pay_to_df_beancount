
# 记录用到的pip命令

## 1. 列出指定包的所有版本

```shell
pip index versions some-package
```

## 2. 安装

```shell
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

## 3. 卸载

```shell
pip uninstall some-package
```

## 4. 更新

```shell
pip install --upgrade some-package
```

## 5. 查看已安装的包

```shell
pip list
```

## 6. 查看某个包的版本

```shell
pip show some-package
```

## 7. 查看可升级的包

```shell
pip list -o
```

## 8. 查看某个包的详细信息

```shell
pip show some-package
```
