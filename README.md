# copymanga-nasdownloader

![social-media](./assets/social-media.png)

<p align="center">
  <!--<a href="https://pypi.org/project/copymanga-downloader/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/copymanga-downloader?style=for-the-badge&logo=PyPI"></a>-->
  <a href="https://github.com/misaka10843/copymanga-nasdownloader/graphs/contributors" target="_blank"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors/misaka10843/copymanga-nasdownloader?style=for-the-badge&logo=github"></a>
  <a href="https://github.com/misaka10843/copymanga-nasdownloader/stargazers" target="_blank"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/misaka10843/copymanga-nasdownloader?style=for-the-badge&label=%E2%AD%90STAR"></a>
</p>

## 前言💭

此仓库是[copymanga-downloader](https://github.com/misaka10843/copymanga-downloader)的重构版本，专门为Nas系统进行设计

请注意，因为是为Nas设计的所以可能会优化很多功能

如果是桌面使用建议使用copymanga-downloader而不是nasdownlaoder

建议使用青龙面板等来自定义触发时间与管理

## 如何使用

本仓库是为了nas系统下载而进行优化，所以下载器本身并没有任何的交互/配置界面

下载器的配置是通过环境变量进行设置，更新列表是通过json进行设置

在运行下载器之前请确保bash的目录在程序目录下

### 配置下载器

请将本仓库中的`.env.sample`更名为`.env`放在cmd的运行目录下

其中各个变量的内容如下

```dotenv
CMNAS_TOKEN= # token填写，防止有需要登录的漫画(字符串)
CMNAS_DOWNLOAD_PATH= # 下载路径(暂存路径，将在cbz打包完成后删除)(字符串)
CMNAS_CBZ_PATH= # CBZ存放路径(字符串)
CMNAS_DATA_PATH= # 配置文件相关存放路径(字符串)
CMNAS_USE_CM_CNAME= # 是否使用copymanga的章节名，如果不使用将按照kavita的格式进行命名(True/False)
CMNAS_API_URL= # API服务器地址(字符串)
CMNAS_LOG_LEVEL= # 日志等级(DEBUG,INFO,WARNING,ERROR)
```

### 配置更新列表

当前只能自行进行配置(之后会做一个web界面进行配置管理)

请在命令运行的目录下创建`updater.json`，其中内部的结构如下：

```json
[
  {
    "name": "漫画名称(指定保存的系列名/文件夹名)",
    "path_word": "copymanga的path_word",
    "group_word": "copymanga的group_word，默认为default",
    "latest_chapter": "最后下载的章节，可以用来限制下载范围(为空则直接下载所有的内容)",
    "last_download_date": "最后下载章节的完成日期"
  },
  {
    "name": "漫画名称(指定保存的系列名/文件夹名)",
    "path_word": "copymanga的path_word",
    "group_word": "copymanga的group_word，默认为default",
    "latest_chapter": "最后下载的章节，可以用来限制下载范围(为空则直接下载所有的内容)",
    "last_download_date": "最后下载章节的完成日期"
  }
]
```

在配置完成之后直接运行程序即可