## rtool安装

rtool是一套使用python3开发的资源处理框架，请在使用前配置python3环境

### 安装pip

+ 检查安装pip是否安装

	打开命令行工具, 执行 `pip -V`, 如果显示pip版本说明已经有pip, 直接执行后面的内容。

+ 安装pip

	+ 到[这个地址](https://pip.pypa.io/en/latest/installing/#python-os-support)下载get-pip.py
	+ 执行 python get-pip.py
	+ 添加环境变量：这个路径是pip可执行文件所在路径，一般在python的安装目录下，python\scripts

### 安装rtool库

+ 下载rtool

```
	git clone git-path-to-rtool/rtool.git
```

+ 安装rtool,切换到rtool目录, 执行

```
	pip install -e .
```

> 如果遇到Permission denied报错，一般是因为系统路径的读写权限问题，使用sudo执行
	>> sudo pip install -e . 

### 配置

+ 复制rtool目录下config.example.yaml为config.yaml

+ 配置以下内容:

```
	project_name: <项目名称>

	project_root: <项目库路径>
```

### 调用方式

直接在命令行任意位置执行 `rtl`

### 使用示例

+ 线下开发模式处理美术资源

```
	rtl task_dev
```


### 重装rtool步骤:

+ 卸载原有版本

```
	pip uninstall rtool
```

+ 重新安装,切换到rtool工具所在目录，执行,同样如果遇到权限问题，使用sudo执行

```
	pip install -e .
```
