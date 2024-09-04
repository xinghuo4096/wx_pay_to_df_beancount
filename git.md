`git filter-repo` 是一个用于重写 Git 仓库历史的工具，它可以更高效地执行 `git-filter-branch` 的许多功能，同时提供更友好的使用界面。这个工具可以用来删除文件、文件夹、大型二进制文件，以及清理整个仓库历史中的敏感数据。以下是使用 `git filter-repo` 的基本步骤：

### 安装 git-filter-repo

首先，需要安装 `git filter-repo`。可以使用 pip 安装：

```bash
pip install git-filter-repo
```

### 使用 git filter-repo

以下是一些使用 `git filter-repo` 的基本示例：

#### 删除文件或文件夹

删除所有历史记录中的 `sensitive-file.txt` 文件：

```bash
git filter-repo --path sensitive-file.txt --invert-paths
```

删除所有历史记录中的 `sensitive-folder/` 文件夹：

```bash
git filter-repo --path sensitive-folder/ --invert-paths
```

#### 删除大于特定大小的文件

删除所有大于 50MB 的文件：

```bash
git filter-repo --size-gt 50M --invert-paths
```

#### 修改作者信息

修改历史记录中的作者信息，将 `old@email.com` 替换为 `new@email.com`：

```bash
git filter-repo --email-callback '
    if old_email == "old@email.com":
        return "new@email.com"
    return old_email
'
```

### 推送更改到远程仓库

完成过滤操作后，需要推送更改到远程仓库：

```bash
git push origin --force --all
git push origin --force --tags
```

### 注意事项

- 在执行任何重写历史的操作之前，请确保备份了你的仓库。
- `git filter-repo` 会重写历史，所以所有分支和标签的历史都会被改变。确保通知所有合作者，并让他们更新他们的本地副本。
- 如果你的仓库是公开的，或者有多个贡献者，强制推送可能会引起问题。务必谨慎操作。
`git filter-repo` 是一个功能强大且灵活的工具，但它也有能力重写你的仓库历史，所以使用时请小心。更多详细信息和高级用法，请参考 `git filter-repo` 的官方文档。

要查看远程仓库的详细信息，可以使用以下 Git 命令：

### 列出远程仓库

要查看配置的远程仓库列表，可以使用：

```bash
git remote -v
```

这个命令会显示远程仓库的名称和对应的 URL。

### 查看远程仓库信息

要查看特定远程仓库的详细信息，可以使用：

```bash
git remote show <remote-name>
```

将 `<remote-name>` 替换为你想要查看的远程仓库的名称（通常是 `origin`）。这个命令会显示远程仓库的 URL、跟踪分支的信息、以及本地分支与远程分支的对应关系。

### 获取远程仓库的最新信息

如果你想获取远程仓库的最新信息，可以使用：

```bash
git fetch <remote-name>
```

这会下载所有你还没有的数据，但不合并任何分支。这可以让你看到最新的远程提交。

### 查看远程仓库的分支

要查看远程仓库有哪些分支，可以使用：

```bash
git branch -r
```

或者，如果你只想查看特定的远程仓库的分支，可以使用：

```bash
git branch -r --remote=<remote-name>
```

通过这些命令，你可以有效地管理和监控你的远程仓库。如果你在使用这些命令时遇到任何问题，或者需要更详细的帮助，请查看 Git 的官方文档或使用 `git help` 命令获取更多帮助信息。

在Git历史库中找回被删除的文件，可以使用以下步骤：

1. **使用`git log`查找文件历史**：
   首先，你需要找到文件被删除之前的提交。可以使用`git log`命令来查看文件的修改历史。

   ```bash
   git log -- <file_path>
   ```

   这里的`<file_path>`是你想要恢复的文件路径。这个命令会列出所有与该文件相关的提交。
2. **确定文件删除前的提交**：
   在`git log`的输出中，找到文件被删除之前的提交。注意提交的哈希值（一个长的字符串，如`a1b2c3d4...`）。
3. **恢复文件**：
   一旦你找到了文件被删除之前的提交哈希，就可以使用以下命令来恢复文件：

   ```bash
   git checkout <commit_hash>^ -- <file_path>
   ```

   请注意，`<commit_hash>^`指的是删除文件的那个提交之前的提交。Git使用`^`来表示父提交。
   如果文件是在某个特定提交中被删除的，你也可以直接使用该提交的哈希值，并加上`~`来指定恢复到该提交之前的状态：

   ```bash
   git checkout <commit_hash>~1 -- <file_path>
   ```

   这里的`~1`表示前一个提交。
4. **添加并提交恢复的文件**：
   恢复文件后，你可能需要将它重新添加到暂存区，并创建一个新的提交：

   ```bash
   git add <file_path>
   git commit -m "Restore <file_path>"
   ```

如果你不确定文件的确切路径，或者想要更简单地找回文件，可以使用`git reflog`或`git fsck --lost-found`（尽管这个命令在较新的Git版本中已经不推荐使用了）来查找丢失的文件。
还有图形界面的工具，如`gitk`、`Git Extensions`、`SourceTree`等，可以帮助你更直观地浏览历史并找回文件。
请记得，一旦文件被恢复，你可能需要处理任何合并冲突，特别是如果自文件删除以来已经有很多更改的情况下。
