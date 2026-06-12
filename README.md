# 校园智能场馆匹配平台

基于大模型与检索的校园场馆智能匹配系统：根据用户需求（活动类型、人数、时间、设备等）推荐合适的校园场馆。

## 项目结构

```
校园智能场馆匹配平台/
├── README.md
├── requirements.txt
├── config.example.py    # 配置示例（复制为 config.py 后填写密钥）
├── llm.py               # 大模型 API 封装
├── embedder.py          # 文本向量化（P2）
├── indexer.py           # 知识库切块与建索引（P1/P2）
├── retriever.py         # 语义检索
├── prompts.py           # 系统 Prompt、边界判断（P3）
├── conversation.py      # 多轮对话 history（P3）
├── main.py              # 命令行入口
├── app.py               # Gradio 网页入口（P5）
├── knowledge/           # 场馆知识库原始 Markdown
├── data/                # chunks.json、embeddings.npz（索引产物）
└── docs/
    ├── 实现阶段规划.md   # 分阶段实现分析（参考）
    ├── 名词解释.md       # RAG / Embedding / Gradio 简述
    ├── P0入门实战.md     # 从零带跑（建议先看）
    ├── P1P2入门实战.md   # 切块 + 向量检索
    ├── 小组分工建议.md   # 3 人分工与答辩准备
    ├── 实验报告.md
    └── AI协作日志.md
```

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 配置：`Copy-Item config.example.py config.py`（DeepSeek Key + 向量相关项见 example）
3. 构建索引：`python indexer.py --rebuild`（改 knowledge 后都要重做）
4. 测试检索：`python test_retriever.py`
5. 测试 API：`python test_llm.py`
6. 命令行：`python main.py`（`reset` 清空历史）
7. 网页演示：见下文 [网页使用说明（Gradio）](#网页使用说明gradio)

## 网页使用说明（Gradio）

与命令行 `main.py` **共用同一套** `Conversation`（RAG + 多轮 + 边界）

### 启动

在项目根目录、已激活 `.venv` 的前提下：

```powershell
cd "D:\大学启动\人工智能基础A\大作业\校园智能场馆匹配平台"
.\.venv\Scripts\Activate.ps1
python app.py
```

1. 终端会先 **预热** 向量模型（出现 `[embedder] 预热完成`）。  
2. 随后显示 `Running on local URL: http://127.0.0.1:7860` —— **这是正常现象**，表示网页服务在运行，终端会一直停在这里，不是卡死。  
3. 浏览器打开 **http://127.0.0.1:7860**（若已配置 `inbrowser=True` 会自动弹出）。  
4. 用完后在终端按 **Ctrl+C** 结束服务。

### 页面操作

| 区域 | 作用 |
|------|------|
| 对话区 | 显示你与助手的多轮记录 |
| **你的问题** | 输入需求后点 **发送** 或按 Enter |
| **清空会话** | 清空网页记录，并调用 `Conversation.reset()` |
| **示例问题** | 点击可填入输入框（含场馆推荐、预约、越界「转专业」等） |
| 底部状态 | 显示「已进行 N 轮有效对话」 |

### 与 CLI 的对应关系

| CLI（`main.py`） | 网页（`app.py`） |
|------------------|------------------|
| 输入 `reset` | 点 **清空会话** |
| 输入 `quit` | 关闭网页 + 终端 Ctrl+C |
| 终端打字 | 浏览器聊天框 |

### 更新知识库后

在 `knowledge/` 增加或修改本校场馆 `.md` 后，执行：

```powershell
python indexer.py --rebuild
```

**无需修改** `app.py`，刷新网页即可使用新索引。

### 常见问题

- **终端一直停在 7860 那行**：服务在跑，去浏览器访问即可。  
- **端口被占用**：改 `app.py` 末尾 `server_port=7860` 为其他端口（如 `7861`）。  
- **回答很慢**：需调用 DeepSeek API，请检查 `config.py` 中 Key 与网络。

## 注意事项

- **虚拟环境**：新开终端需再执行 `.\.venv\Scripts\Activate.ps1`，看到 `(.venv)` 再运行命令。
- **解释器**：在 Cursor 中运行脚本时，请选项目 `.venv` 里的 Python。
- **Gradio**：若 7860 端口被占用，可在 `app.py` 末尾把 `server_port` 改为其他端口。
- **检索不准**：可调 `config.py` 中 `SIMILARITY_THRESHOLD`（如 0.25～0.45）；修改 `knowledge/` 后必须 `python indexer.py --rebuild`。

## 配置同步脚本

拉取代码后，需要运行同步脚本将 `config.example.py` 中的新配置同步到本地 `config.py`：

```bash
python sync_config.py
```

脚本会自动检测并添加缺失的配置项（如 `USE_KNOWLEDGE_BASE`、`USE_TWO_STAGE_RETRIEVAL` 等），**不会覆盖已有的配置**（如 API Key）。

## 对比实验

本项目提供了自动化对比实验脚本，用于验证 RAG 知识库对回答质量的影响。

### 运行对比实验

```bash
python run_comparison.py
```

脚本会自动对 15 个测试问题分别以「带知识库」和「不带知识库」两种模式运行，并生成：
- `comparison_results_时间戳.json` - 原始实验数据
- `comparison_results_时间戳_report.md` - 详细对比报告

### 手动对比测试

也可以手动切换模式测试：

```python
# config.py
USE_KNOWLEDGE_BASE = True   # 带知识库（RAG 模式）
# USE_KNOWLEDGE_BASE = False  # 不带知识库（纯 LLM 模式）
```

改完后运行 `python app.py` 即可测试。

### 测试问题集

测试问题定义在 `test_questions.json` 中，包含 15 个覆盖不同维度的问题：

| 类型 | 说明 |
|------|------|
| 事实性 | 开放时间、收费标准等具体信息 |
| 推荐性 | 根据需求推荐场馆 |
| 对比性 | 对比不同场馆的特点 |
| 约束性 | 带条件限制的查询 |
| 综合性 | 需要综合多个方面回答 |
| 细节性 | 询问具体细节 |
| 边界性 | 测试系统边界能力 |

如需修改测试问题，直接编辑 `test_questions.json` 即可。

## 环境要求

- Python 3.10+

## 给队友 / 新克隆项目的人

代码可以 Git 共享，**API Key 不能**。仓库里的 `.gitignore` 已忽略 `config.py`，每人需在本机单独配置：

1. 克隆或复制项目后，进入项目根目录。
2. 安装依赖（建议使用虚拟环境，见 [`docs/P0入门实战.md`](docs/P0入门实战.md) 第 2–3 步）。
3. 创建本地配置（Windows PowerShell）：
   ```powershell
   Copy-Item config.example.py config.py
   ```
4. 打开 `config.py`，将 `API_KEY` 改为你自己在 [DeepSeek 开放平台](https://platform.deepseek.com) 申请的 Key。
5. 依次自检：`python test_retriever.py` → `python test_llm.py` → `python main.py` → `python app.py`。

**请勿**把 `config.py` 提交到 Git、发群聊或打进作业 zip。可提交的只有 `config.example.py`（模板，无真实密钥）。

若教师统一发放课程 Key，由组长私下发给组员填入各自 `config.py`，同样不要写入仓库。

## 提交作业前检查

- [ ] 压缩包 / 仓库中**没有** `config.py`、`.env`
- [ ] 含有 `README.md`、`requirements.txt`、`config.example.py`、完整源代码与 `knowledge/`
- [ ] 他人按本 README 复制 `config.example.py` 并填入自己的 Key 后可运行
