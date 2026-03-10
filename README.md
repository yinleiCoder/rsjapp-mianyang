# 《绵阳市专业技术人员继续教育公需科目培训平台》刷课逆向工程

一款专为绵阳市各教师及专业技术工作人员减轻负担的刷课软件。

代码仅做学习交流使用，更多请了解**JavaScript逆向**!!!

## 功能

- 官网：https://rsjapp.mianyang.cn/jxjy/pc/index.jhtml
- 实时查课
- 一键选课
- 一键刷课
- 自动化考试（查询考试成绩）

## 下载及使用方式


### 本地构建

- git clone 本仓库 / fork
- uv run main.py 启动图形界面
- uv run course.py 单独启动刷课（不带图形界面）

## 编程环境

- vscode
- chrome
- python
- uv
- [爬虫工具库](https://spidertools.cn/#/curl2Request)

### 程序架构设计说明

```
子线程
   ↓
queue
   ↓
主线程 after() 轮询
   ↓
更新UI
```

- 刷课在子线程threading.Thread（和Android类似，主线程又称为UI线程，不应该阻塞，否则会造成界面”卡死“）
- queue向主线程发送消息（队列承担主线程、子线程消息传送的媒介）
- after()在Tkinter主线程轮询队列

### bug

- [execjs: AttributeError: 'NoneType' object has no attribute 'replace'](https://blog.csdn.net/c271696748/article/details/139020552?ops_request_misc=elastic_search_misc&request_id=c29470df41713781ac15ec0466359b1d&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-139020552-null-null.142^v102^pc_search_result_base7&utm_term=execjs%20AttributeError%3A%20NoneType%20object%20has%20no%20attribute%20replace&spm=1018.2226.3001.4187)，请安装**PyExecjs2**解决此问题（uv add PyExecjs2）

## 感谢

如果您觉得有用，不妨请我喝杯咖啡？我将持续维护代码，保证软件可用（仅作学习交流使用！！！）。