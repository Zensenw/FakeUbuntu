# Fake Ubuntu Screensaver (Python)

一个模仿 Ubuntu 18.04 登录界面的 Windows 屏保程序。

A Windows screensaver that mimics Ubuntu 18.04 login screen.

## 功能特点

- 模仿 Ubuntu 18.04 登录界面
- 空闲时显示时间和日期
- 密码保护
- 全屏模式
- 无需安装额外依赖（使用 Python 内置 Tkinter）

## 运行

```bash
python fake_ubuntu.py
```

或者直接双击 `fake_ubuntu.py` 文件运行。

## 配置

编辑 `fake_ubuntu.py` 文件中的 `CONFIG` 字典：

```python
CONFIG = {
    'password': 'ubuntu',      # 修改为你想要的密码
    'idle_timeout': 30000,     # 空闲超时（毫秒）
    'hint_timeout': 1300,      # 错误提示显示时间
}
```

## 使用说明

1. **空闲界面**: 程序启动后显示时间和日期
2. **登录界面**: 移动鼠标或按任意键显示登录界面
3. **输入密码**: 输入正确密码后退出屏保
4. **默认密码**: `ubuntu`

## 打包为 EXE

使用 PyInstaller 打包为独立可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name FakeUbuntu fake_ubuntu.py
```

打包后的 EXE 文件在 `dist/` 目录中。

### 安装为系统屏保

1. 将生成的 `FakeUbuntu.exe` 重命名为 `FakeUbuntu.scr`
2. 复制到 `C:\Windows\System32\` 目录
3. 在 Windows 设置中选择该屏保

## 命令行参数

- `/s` 或 `-s`: 屏保模式（全屏运行）
- `/c` 或 `-c`: 配置模式（显示当前配置）
- `/p` 或 `-p`: 预览模式

## 许可证

MIT
