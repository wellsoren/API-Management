# API密钥管理器

本地一站式管理你的所有大模型 API 接口和密钥，支持快速录入、搜索筛选、一键复制密钥，省去每次都要打开官网找的麻烦。

## 核心功能

- **密钥管理**：集中管理所有 API Key，支持增删改查
- **26 个预置提供商**：预填 DeepSeek、OpenAI、Anthropic、智谱AI、月之暗面等主流提供商配置
- **智能填充**：选择预置提供商时自动填充 OpenAI 兼容地址和 Anthropic 原生地址
- **模型拉取**：填写 API Key 后，一键从提供商拉取可用模型列表并点选填充
- **搜索筛选**：按提供商、模型名、名称、所属应用搜索，支持多维度筛选
- **一键复制**：点击复制模型名、OPenAI 地址、Anthropic 地址、API Key、官网到剪贴板
- **密钥保护**：默认隐藏密钥，点击眼睛图标查看
- **浅色主题**：清晰明亮的界面设计

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 + FastAPI + SQLModel |
| 数据库 | SQLite |
| 前端渲染 | Jinja2 模板 |
| 交互 | HTMX（异步片段替换）+ Alpine.js（客户端 UI 状态） |
| 样式 | Tailwind CSS（零 Node 依赖） |
| 主题 | 浅色主题 |

## 快速启动

### 方式一：源码运行（需要 Python 3.10+）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000

# 访问
# http://localhost:8000
```

### 方式二：便携版（零安装，解压即用）

适合不想接触命令行的用户，每台电脑只需 Python 3.10+。

```bash
# 1. 打包便携版（在项目目录执行）
python scripts/distribute_portable.py

# 输出：dist/API密钥管理器_Portable_v1.0.zip

# 2. 用户解压 zip 后：
#    Windows: 双击 start.bat
#    macOS/Linux: 终端执行 chmod +x start.sh && ./start.sh
#    浏览器自动打开 http://localhost:8000
```

### 方式三：独立可执行文件（无需 Python）

适合完全不想装 Python 的用户，需要先在对应平台用 PyInstaller 打包。

```bash
# 安装打包工具
pip install pyinstaller

# 打包当前平台可执行文件
python scripts/build.py

# 输出目录（根据平台不同）：
#   Windows: dist/API密钥管理器_v1.0_windows/API密钥管理器.exe
#   macOS:   dist/API密钥管理器_v1.0_darwin/API密钥管理器.app
#   Linux:   dist/API密钥管理器_v1.0_linux/API密钥管理器
```

PyInstaller **不支持交叉编译**，需要在 Windows / macOS / Linux 上分别执行打包。

---

## 项目结构

```
api_management/
├── app/
│   ├── main.py           # FastAPI 入口（首页路由）
│   ├── db.py             # SQLite 引擎初始化
│   ├── models.py         # ApiInfo 数据模型
│   ├── routers/
│   │   ├── __init__.py   # 路由聚合
│   │   └── apis.py       # API 管理 CRUD 路由
│   ├── templates/
│   │   ├── base.html     # 基础布局（科幻主题）
│   │   ├── index.html    # 首页（统计 + 搜索 + 表格）
│   │   └── fragments/
│   │       ├── api_form.html   # 新增/编辑表单
│   │       └── api_table.html  # 表格片段（HTMX 局部刷新）
│   └── static/
│       ├── css/
│       │   ├── input.css  # Tailwind 输入文件
│       │   └── app.css    # Tailwind 编译产物（自动生成）
│       └── vendor/        # 第三方 JS（自动填充）
├── data/
│   └── app.db             # SQLite 数据库
├── scripts/
│   ├── distribute_portable.py  # 便携版打包脚本
│   ├── build.py                # 可执行文件打包脚本
│   └── build.spec              # PyInstaller 打包配置
├── start.bat              # [便携版] Windows 一键启动
├── start.sh               # [便携版] macOS/Linux 一键启动
├── .gitignore
├── requirements.txt
├── tailwind.config.js
└── README.md
```

## 数据模型

| 字段 | 说明 | 示例 |
|---|---|---|
| `provider` | 模型提供商 | OpenAI, Anthropic, DeepSeek (26 个预设，支持自定义输入) |
| `model_name` | 模型名（必填） | gpt-4o, claude-3-opus |
| `url_openai` | OpenAI 兼容接口地址 | https://api.openai.com/v1 |
| `url_anthropic` | Anthropic 原生接口地址 | https://api.anthropic.com |
| `api_key` | API Key | sk-... |
| `name` | API 名称（选填） | 工作用 GPT-4o |
| `app_usage` | 所属应用 | 个人助手, 工作项目 |
| `website` | 官网地址 | https://platform.openai.com |
| `model_attr` | 模型属性 | 文本, 图像, 语音, 向量嵌入, 代码, 推理, 多模态 |

## 变更日志

### v1.0（正式版）
- 26 个预置提供商及完整配置（接口地址 + 官网 + API 类型）
- OpenAI 兼容地址 / Anthropic 原生地址两行独立展示
- 拉取模型列表功能，支持点选填充
- 按提供商、模型名、名称、所属应用搜索筛选
- 浅色主题，密钥默认隐藏
- 一键复制模型名、双地址、API Key、官网
- 模型属性分类（文本/图像/语音/向量嵌入/代码/推理/多模态）
- 完整 CRUD：新增、编辑、删除 API 记录

### 发行版

#### 便携版（Portable）
- `start.bat`：Windows 一键启动脚本，自动创建虚拟环境、安装依赖、启动服务
- `start.sh`：macOS/Linux 一键启动脚本，功能同上
- `scripts/distribute_portable.py`：将项目打包为便携式 zip 包，解压即用
- `scripts/build.spec`：PyInstaller 打包配置（含控制台版和隐藏窗口版）
- `scripts/build.py`：跨平台可执行文件打包脚本
