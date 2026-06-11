# AI 协作日志

记录与 AI 协作完成「校园智能场馆匹配平台」的关键步骤，便于实验报告引用与**后续会话接续开发**。

---

## 协作记录

| 日期 | 协作内容 | 采纳情况 | 备注 |
|------|----------|----------|------|
| 2026-06-03 | 在 Cursor 安装 **Office Viewer**（`cweijan.vscode-office`），用于预览任务书 `.docx` | 已采纳 | 用户设置中保留 `*.md` 使用默认编辑器，避免影响 Markdown 工作流 |
| 2026-06-03 | 按任务书「方向一-知识问答助手」脚手架，在 `大作业/` 下新建 **校园智能场馆匹配平台** 并搭好目录与占位代码 | 已采纳 | 工作区当时无方向一实体代码，按截图结构搭建；业务语义改为场馆匹配 |
| 2026-06-03 | 建立本协作日志，约定后续关键交互均写入此文件 | 已采纳 | 见下文「项目接续指南」 |
| 2026-06-03 | 对照任务书梳理实现路线图：必做（RAG/多轮/边界/CLI）+ 进阶（向量检索/Gradio） | 已采纳 | 详见下文「实现路线图（2026-06-03 定稿）」 |
| 2026-06-03 | 将分阶段分析整理为参考文档 `docs/实现阶段规划.md` | 已采纳 | 含 P0–P6 目标、技术要点、风险、完成标准、时间线 |
| 2026-06-03 | 启动并完成 **P0**：DeepSeek 联调、自检脚本、`.gitignore`、推送 GitHub | 已完成 | 见下文「P0 完成摘要」；远程仓库 `Yu-lorde/AI-Powered-Campus-Venue` |
| 2026-06-03 | README 补充队友配置说明；厘清 `config.py` 仅本地、不入库 | 已采纳 | 队友 clone 后复制 `config.example.py` 自填 Key |
| 2026-06-03 | P0 常见问题迁至 README「注意事项」 | 已采纳 | `P0入门实战.md` 改为指向 README |
| 2026-06-03 | 实现 **P1/P2 代码** + `docs/P1P2入门实战.md`；用户暂离，进度见「暂停接续备忘」 | 已完成 | 语义向量已在 VPN 下跑通 |
| 2026-06-04 | **P3**：`prompts.py` + `conversation.py` 多轮与边界；`test_conversation.py`、`docs/测试用例.md` | 已采纳 | 可先用示例 knowledge 测，不依赖 15 个 md |
| 2026-06-04 | 今日收工：P3 代码已写，`test_conversation.py` 离线通过；`main.py` 多轮联调**未测完** | 待续 | 见「暂停接续备忘」 |
| 2026-06-04 | **P3 联调完成**：`main.py` 三轮对话（推荐 / 多轮预约 / 转专业越界）；实录写入 `docs/实验报告.md` §4 | 已采纳 | 终端截图 `docs/images/p3-main-cli-test-2026-06-04.png`（示例假数据） |
| 2026-06-04 | 本地语义模型：`EMBEDDING_LOCAL_ONLY`、repo_id 修正、`warmup()`；`docs/名词解释.md` 扩充 | 已采纳 | 校园网可不连 huggingface.co |
| 2026-06-04 | **P5 Gradio**：新增 `app.py`，共用 `Conversation`；`requirements.txt` 增加 gradio | 已采纳 | `python app.py` → http://127.0.0.1:7860 |
| 2026-06-04 | P5 网页联调（篮球场馆推荐）；`app.py` 加 `inbrowser=True`；README 网页使用说明 | 已采纳 | 图 2：`docs/image/实验报告/gradio-p5-2026-06-04.png` |
| 2026-06-04 | 实验报告 §4 整理（CLI 图 1 + Gradio 图 2）；**Git 已全部 push** | 已完成 | 今日收工，见「暂停接续备忘」 |
| 2026-06-10 | **健身房办卡查询遗漏收费场馆**：检索"健身房办卡"只返回免费健身房，遗漏收费的银泉、游泳馆健身房 | 已采纳 | 见下文「2026-06-10 — 混合检索与同义词扩展」 |
| 2026-06-10 | **关键词检索同义词扩展**：添加"办卡"↔"卡类"、"收费"↔"月卡/年卡/单次"等映射 | 已采纳 | 修复标签匹配遗漏问题 |
| 2026-06-10 | **"不想花钱"意图检测增强**：处理分词错误（"我们不想花钱"被分词为"们不"+"想"+"花钱"） | 已采纳 | 添加字符串直接检测"不想花钱"模式 |
| 2026-06-10 | **免费健身房推荐不全**：查询"不想花钱"时只返回2个场馆而非3个 | 已采纳 | 修复免费场馆加分逻辑与合并策略 |
| 2026-06-10 | **Git 冲突修复**：`data/chunks.json` 合并冲突，执行 `python indexer.py --rebuild` 重新生成 | 已采纳 | 冲突标记完全清除 |
| 2026-06-11 | **Git 同步**：`git pull` 因本地改动 `prompts.py`/`retriever.py` 冲突；`git reset --hard origin/main` 对齐远程 5 个提交 | 已采纳 | 合并后远程 `prompts.py` 含语法残留，见下行 |
| 2026-06-11 | **修复 `prompts.py` 语法错误**：`build_rag_user_message` 两段合并代码叠在一起，`blocks.append(` 未闭合导致 `SyntaxError` | 已采纳 | 删除残缺段，保留按来源分组的完整逻辑 |
| 2026-06-11 | **修复引用来源 `?-?`**：重建索引 + 改检索/Prompt 链路，使 `[来源: 文件名:行号-行号]` 正常显示 | 已采纳 | 见下文「2026-06-11 — 引用标注修复」 |
| 2026-06-11 | **环境**：`ModuleNotFoundError: gradio` → 需先 `.\.venv\Scripts\Activate.ps1` 再 `python app.py` | 已采纳 | 未激活 venv 时会用系统 Python |
| 2026-06-11 | **两阶段检索增强**：`USE_TWO_STAGE_RETRIEVAL`；意图分类 + query 重加权 + chunk 过滤；先试行方案 A（多意图并集）后改为**方案 C（主任务 + 约束）** | 已采纳 | 见下文「两阶段检索增强」 |
| 2026-06-11 | **扩大服务范围 Prompt**：`SYSTEM_PROMPT` 覆盖体育/餐饮/自习/活动场地；修复「推荐吃早饭」被 LLM 误判越界 | 已采纳 | 规则 `is_out_of_scope` 未拦，系旧 Prompt 只写「体育场馆」 |
| 2026-06-11 | **运动检索统一化**：新增 `sport_terms.py`；足球/篮球/排球等与羽毛球同逻辑；修复「踢足球」误命中游泳馆/自习 | 已采纳 | 分词、`sport_focus` 过滤、全库补捞 |

> **维护约定**：每完成一轮有意义的协作（定方案、改模块、联调、写报告段落等），在表中追加一行，并同步更新「当前进度」与「待办」。

---

## 项目接续指南（给下一轮 AI / 给自己）

### 1. 项目定位

- **课程**：人工智能基础 A 大作业  
- **选题**：校园智能场馆匹配平台（对标方向一：检索 + 大模型问答/推荐）  
- **根目录**：`d:\大学启动\人工智能基础A\大作业\校园智能场馆匹配平台\`  
- **任务书**：`../人工智能基础-大作业任务书.docx`（需 Office Viewer 或 Word 打开）

### 2. 当前架构（已实现）

```
knowledge/*.md
    → indexer.py --rebuild → data/chunks.json + embeddings.npz（本机）
用户问题 → retriever.py（语义向量 + 关键词；sport_terms 运动归一化）
         → conversation.py + prompts.py（可选两阶段：主任务/约束过滤，USE_TWO_STAGE_RETRIEVAL）
         → main.py（CLI）/ app.py（Gradio）→ llm.py(DeepSeek)
```

| 文件 | 职责 | 实现状态 |
|------|------|----------|
| `indexer.py` / `embedder.py` | P1 切块、P2 向量化；本地离线加载 | 已提交 |
| `retriever.py` | 语义检索；无向量时回退关键词 | 已联调 |
| `conversation.py` / `prompts.py` | P3 多轮 + 边界；两阶段检索增强（方案 C） | 已联调 |
| `sport_terms.py` | 体育运动词表（足球/篮球/羽毛球等统一匹配） | 已提交 |
| `main.py` / `app.py` | CLI / Gradio 入口（共用 Conversation） | 已联调 |
| `data/chunks.json` | RAG 切块索引 | 6 段（2 个示例 md） |
| `data/embeddings.npz` | 向量索引 | 本机已生成（gitignore，队友需 `--rebuild`） |
| `knowledge/*.md` | 场馆文档 | **2 个示例**（任务书要求 **≥15 个**本校 .md） |
| `config.py` | 含 Key、向量、镜像项 | 仅本地，勿提交 |

### 3. 当前进度

- [x] P0：DeepSeek + CLI + GitHub  
- [x] P1：`indexer.py`、`data/chunks.json`（6 段）  
- [x] P2：语义向量检索（本机 `embeddings.npz` + `EMBEDDING_LOCAL_ONLY` 离线加载）  
- [x] P3：多轮 + 边界；`main.py` 三轮联调 + 终端截图  
- [x] P5：Gradio `app.py` 联调 + 网页截图；README 网页说明  
- [x] 实验报告 **§4**（CLI + Gradio 测试，标注假数据）  
- [x] **Git push**（2026-06-04 收工前已完成）  
- [ ] `knowledge/` **≥15 个**本校场馆 `.md` → `--rebuild` → 复测并更新报告图  
- [ ] 实验报告 **§一、二、三、五**（背景、方案、过程、总结）  
- [x] **P6 引用标注（部分）**：检索/Prompt 已支持 `start_line`/`end_line`；回答可标注 `[来源: 东区大食堂.md:13-26]` 等  
- [x] **检索增强（进阶）**：两阶段检索（方案 C 主任务+约束）+ `sport_terms.py` 运动词表；`config.py` 中 `USE_TWO_STAGE_RETRIEVAL = True`  
- [ ] P6 剩余：有无 RAG 对比实验写入报告  
- [ ] 按 `docs/测试用例.md` 补测 T3–T6（追问「第二个」、`reset` 等）

### 4. 建议的下一步（优先级）

见下文 **「暂停接续备忘（回来先做）」**。

### 4b. 暂停接续备忘（回来先做）

**收工状态（2026-06-04）**：P0–P3、P5 已跑通；CLI + Gradio 测试写入 `docs/实验报告.md` §4（图 1 终端、图 2 网页）；`README.md` 含 Gradio 使用说明；代码已 **push** 至 `Yu-lorde/AI-Powered-Campus-Venue`。知识库仍为 **2 个示例 md（假数据）**。

**下次优先（按顺序）：**

1. `cd` 项目根目录 → `.\.venv\Scripts\Activate.ps1`  
2. **`knowledge/` 补满 ≥15 个本校场馆 `.md`**（任务书硬性要求）  
3. `python indexer.py --rebuild`（改库后必做）  
4. 用 `main.py` / `app.py` 复测同一批用例，更新实验报告截图与文字  
5. 撰写实验报告 §一–三、§五；对照任务书核对评分点  
6. 可选：`docs/测试用例.md` T3–T6；P6 对比实验  
7. 提交前再确认：无 `config.py` 入库

**无需重做**：`app.py` / `conversation.py` 骨架；补数据后一般只 rebuild + 复测 + 改报告。

### 5. 与新 AI 协作时的推荐开场

复制下面一段话发给 AI，可快速恢复上下文：

```text
继续「校园智能场馆匹配平台」（人工智能基础 A 大作业）。
路径：d:\大学启动\人工智能基础A\大作业\校园智能场馆匹配平台
请先读 docs/AI协作日志.md、README.md、docs/实验报告.md。
P0–P3、P5 已完成并已 push；知识库仍仅 2 个示例 md。
下次优先：补 knowledge ≥15 个本校文件 → indexer --rebuild → 完善报告 §一–三/五。
```

### 6. 技术决策备忘（避免重复讨论）

| 决策点 | 当前选择 | 可变更条件 |
|--------|----------|------------|
| 脚手架来源 | 对齐「方向一-知识问答助手」目录结构 | 若任务书明确要求其他结构再调整 |
| 检索方式 | **sentence_transformers 语义向量**（`EMBEDDING_LOCAL_ONLY` 离线） | 校园网可改 `tfidf` 开发；无向量时关键词回退 |
| LLM 接入 | OpenAI 兼容 SDK（`openai` 包） | 若用国内 API，改 `API_BASE` 即可 |
| 配置管理 | `config.example.py` + 本地 `config.py`（勿提交密钥） | 可改用 `.env` + `python-dotenv` |

### 7. 环境与工具

- **Python**：用户环境中有 3.13（见 Cursor `settings.json` 中 python 路径）  
- **编辑器**：Cursor；已装 `cweijan.vscode-office` 预览 docx  
- **运行入口**：`python main.py`（CLI）或 `python app.py`（Gradio，http://127.0.0.1:7860）

### 8. 协作日志更新模板（复制使用）

```markdown
| YYYY-MM-DD | [做了什么] | 已采纳 / 部分采纳 / 未采纳 | [原因或文件变更] |
```

---

## 详细步骤记录（按时间展开）

### 2026-06-03 — 环境与文档

- **问题**：任务书 `.docx` 在编辑器中无法正常阅读。  
- **处理**：安装扩展 `cweijan.vscode-office`；在 `%APPDATA%\Cursor\User\settings.json` 中为 `*.md` / `*.markdown` 指定 `default` 编辑器，避免 Office Viewer 接管 Markdown。  
- **接续提示**：修改任务书要求时，用 Office Viewer 或 Word 打开 `人工智能基础-大作业任务书.docx`。

### 2026-06-03 — 初始化项目脚手架

- **需求**：在 `大作业` 文件夹内新建「校园智能场馆匹配平台」，结构同方向一。  
- **产出文件**：  
  - 根目录：`README.md`、`requirements.txt`、`config.example.py`、`llm.py`、`retriever.py`、`main.py`  
  - `knowledge/示例-体育馆.md`（示例数据，上线前应换成本校场馆）  
  - `docs/实验报告.md`（空模板）、`docs/AI协作日志.md`（本文件）  
- **未做事项**：未创建 `config.py`（含密钥）；未运行联调；未读取任务书全文（docx 二进制未在本环境解析）。  
- **接续提示**：下一轮协作应**优先对照任务书**核对评分点，再决定是否要 Gradio/Web、向量库、日志格式等。

### 2026-06-03 — 建立协作日志机制

- **约定**：用户与 AI 的关键交互步骤写入本文件；每轮结束更新「协作记录表」「当前进度」「待办」。  
- **目的**：实验报告可引用 AI 协作过程；换会话或换模型时可无缝接续。

### 2026-06-03 — P0 完成摘要

- **配置**：`config.example.py` 改为 DeepSeek；用户本地 `config.py` 已填 Key（未入库）。  
- **代码**：`llm.py` 增加 `LLMError`、重试；`main.py` 捕获 API 错误；`retriever.py` 无 config 时可默认检索自检。  
- **知识库**：`knowledge/示例-体育馆.md`、`示例-游泳馆.md`（2 文件，待换本校真数据）。  
- **文档**：`docs/P0入门实战.md`；README 队友配置与提交检查。  
- **验证**：`python test_llm.py` 调用成功；检索自检可加载 2 文件。  
- **协作**：虚拟环境 `.venv`；Git 首次提交并 push 至 `https://github.com/Yu-lorde/AI-Powered-Campus-Venue`（18 文件，无 `config.py`）。  
- **未做（属 P1+）**：多轮对话、边界 Prompt、向量检索、Gradio、知识库 ≥15 段。

### 2026-06-04 — P3 `main.py` 联调（示例知识库）

- **环境**：`.venv`，`sentence_transformers` + 本地缓存 + 启动预热；DeepSeek API 正常。  
- **知识库**：仅 `示例-体育馆.md`、`示例-游泳馆.md`（**假数据**，非本校真实场馆）。  
- **实测三轮**（同一会话）：  
  1. 羽毛球馆推荐 → 命中东区体育中心，引用容量/室内信息  
  2. 15 人是否需预约 → 多轮承接，引用「提前 3–7 个工作日」  
  3. 转专业 → 越界拒答，未编造场馆  
- **产出**：`docs/实验报告.md` §4 文字实录；终端风格截图如下（由 `scripts/render_terminal_screenshot.py` 根据实录生成，标注假数据）：

- **CLI 截图**：`docs/image/实验报告/1780555211614.png`（报告图 1）

### 2026-06-04 — P5 Gradio 网页（收工）

- **启动**：`python app.py`；终端显示 `Running on local URL: http://127.0.0.1:7860` 为**正常**（服务占用终端，Ctrl+C 结束）；`inbrowser=True` 可自动开浏览器。  
- **实测**：篮球场馆推荐（东区体育中心）；库内无「提供用球」信息时不编造。  
- **文档**：`README.md` 新增「网页使用说明」；`docs/实验报告.md` §4.3 + 图 2 `gradio-p5-2026-06-04.png`。  
- **Git**：用户确认当日变更已 push。

### 2026-06-03 — P1/P2 代码落地（用户暂离）

- **新增**：`indexer.py`、`embedder.py`；改造 `retriever.py`、`main.py`、`test_retriever.py`；`docs/P1P2入门实战.md`；README 注意事项 + P1P2 快速开始。  
- **知识库**：示例 md 改为按 `##` 切块；`indexer --rebuild` 产出 **6 段** → `data/chunks.json`。  
- **阻塞**：本机连 `huggingface.co` 超时，**`embeddings.npz` 未生成**；教程已写镜像 `HF_ENDPOINT=https://hf-mirror.com`。  
- **回退**：无向量时 `retriever` 对 `chunks.json` 做关键词检索，仍可跑 `test_retriever.py`。  
- **用户状态**：P0 `test_llm.py` 已成功；稍后回来按「暂停接续备忘」继续。

### 2026-06-10 — 混合检索与同义词扩展

- **用户问题**："银泉和游泳馆健身房都收费呀……"，检索"健身房办卡"只返回免费健身房（碧峰、青溪、蓝田），遗漏收费的银泉健身房和游泳馆健身房。

- **根因分析（两层）**：
  1. **向量检索局限**：单向量检索只返回免费健身房，对"办卡"语义理解不足
  2. **关键词检索遗漏**：银泉健身房标签为"卡类"，与"办卡"未建立同义词映射

- **修复方案**：

| 文件 | 改动 |
|------|------|
| `retriever.py` | 重构 `retrieve` 函数：向量检索与关键词检索**同时运行**，按场馆合并（每个场馆最多保留3个结果），按分数排序（取场馆最高分） |
| `retriever.py` | 扩展 `sport_synonyms`：`'收费'` 增加"办卡"/"卡类"/"单次"；`'办卡'`/`'卡类'` 增加"月卡"/"年卡"/"半年卡"/"单次" |

- **修复效果**：

| 查询 | 修改前 | 修改后 |
|------|--------|--------|
| "健身房办卡" | 只返回免费健身房 | 游泳馆、银泉（收费）排前 + 碧峰、青溪、蓝田（免费） |

### 2026-06-10 — "不想花钱"意图检测增强

- **用户问题**："我和朋友想去健身房 我们不想花钱 帮我推荐一下场馆"只返回2个场馆而非3个（遗漏青溪健身房）

- **根因分析（分词问题）**：
  - jieba 分词将"我们不想花钱"分成了 `['我', '和', '朋友', '想去', '健身房', ' 我', '们不', '想', '花钱', ...]`
  - "们不"、"想"、"花钱"被分开，无法直接匹配"不想"或"不花钱"

- **修复方案**：

| 文件 | 改动 |
|------|------|
| `retriever.py` | `_retrieve_keyword` 函数：在 `has_free_intent` 检测中添加**字符串直接匹配**逻辑（`'不想花钱' in q`），不依赖分词结果 |
| `retriever.py` | 增加检测模式：`'们不' + '想' + '花钱'`、`'不想' + '花钱'` 字符串匹配 |

- **修复效果**：
  - 关键词检索正确识别免费意图，青溪健身房从 score=2 提升至 score=7
  - 合并结果后返回碧峰、青溪、蓝田三个免费健身房

### 2026-06-10 — Git 冲突修复

- **问题**：`data/chunks.json` 文件存在 Git 合并冲突标记（`<<<<<<<`, `=======`, `>>>>>>>`）

- **解决**：由于 `chunks.json` 是自动生成文件，执行 `python indexer.py --rebuild` 重新生成

- **验证**：`grep -r "<<<<<<<\|=======\|\>>>>>>>" --include="*.py" --include="*.json"` 无冲突标记

### 2026-06-11 — Git 同步与合并后排错

- **背景**：本地 `main` 落后 `origin/main` 5 个提交；本地曾改 `prompts.py`、`retriever.py`，`git pull` 被拒绝。  
- **处理**：执行 `git fetch origin` + `git reset --hard origin/main` 强制对齐远程（**本地未提交改动已丢弃**）。  
- **文件标黄说明**：资源管理器中黄色 `M` = Git 未提交修改，**不是**合并冲突；仓库内无 `<<<<<<<` 冲突标记。  
- **Gradio 报错**：未激活 `.venv` 时 `python app.py` 报 `No module named 'gradio'`；激活虚拟环境后正常。  
- **语法错误**：远程合并后的 `prompts.py` 在 `build_rag_user_message` 处两段代码拼接不完整，运行报 `SyntaxError: '(' was never closed`，已手工修复。

### 2026-06-11 — 引用标注修复（P6）

- **现象**：Gradio 回答中来源显示为 `[来源: 东区大食堂.md:?-?]`，无法对应知识库具体段落。  
- **根因（两层）**：  
  1. `data/chunks.json` 为旧索引，chunk 无 `start_line`/`end_line` 字段（合并分支后未 `--rebuild`）。  
  2. `retrieve_for_prompt` → `merge_hits_by_source` 按文件合并时丢弃行号；`build_rag_user_message` 只取第一个 chunk 的行号，多段落时无法逐条引用。  
- **改动摘要**：

| 文件 | 改动 |
|------|------|
| `indexer.py` | （远程已有）按 `##` 切块时写入 `start_line`/`end_line`（1-based） |
| `data/chunks.json` | 执行 `python indexer.py --rebuild`，308 段，含行号 |
| `retriever.py` | `retrieve_for_prompt` 改为命中文件后**按段落展开**，每段保留行号；`merge_hits_by_source` 合并时附带首尾行号 |
| `prompts.py` | `build_rag_user_message` 每段参考资料单独标注 `（来源: 文件:起-止）`；SYSTEM_PROMPT 要求 LLM 不得写 `?-?` |
| `test_retriever.py` | 自检改为验证展开段落含行号且字段完整 |

- **验证**：查询「东区大食堂晚餐」时，参考资料示例为 `（来源: 东区大食堂.md:13-26）` 休闲餐厅段；重启 `python app.py` 后 LLM 可照抄具体行号。  
- **维护约定**：`knowledge/*.md` 增删改后须 `python indexer.py --rebuild`，否则行号与文件不一致会再次退化。

### 2026-06-11 — 两阶段检索增强（方案 C）

- **动机**：单轮向量检索对「餐饮 vs 自习」「运动 vs 自习」等复合或易混 query 噪声大；希望在检索与拼 Prompt 前做轻量意图约束。  
- **配置**：`config.example.py` / `config.py` 增加 `USE_TWO_STAGE_RETRIEVAL = True`；`conversation.py` 在开关开启时走增强链路。  
- **方案演进**：  
  1. **初版**：单意图 + `exclude_docs`（餐饮排除自习等）  
  2. **方案 A（已弃用）**：多意图并集保留、交集排除——可缓解「近食堂自习」但会把餐饮与自习段落等量塞进 Prompt  
  3. **方案 C（当前）**：`parse_query_roles()` 拆 **主任务**（如「供我自习」→ 自习）与 **约束**（如「近食堂」→ 餐饮）；过滤按主任务，约束词放宽 exclude 并附少量地标文档  
- **主要函数**（`prompts.py`）：

| 函数 | 作用 |
|------|------|
| `parse_query_roles` | 主任务 + 约束 + `sport_focus` |
| `build_enhanced_retrieval_query` | 多轮上下文 + `_REWEIGHT_STRIP` 弱化泛词 |
| `filter_chunks_by_roles` | 主任务过滤、约束重排、运动不匹配时全库补捞 |
| `build_enhanced_rag_user_message` | 过滤后拼 Prompt，标题 `【意图分类】主任务：…；约束：…` |

- **复合需求示例**：「离食堂近…供我自习」→ 主任务自习 + 约束餐饮；保留 `自习-*.md`（含「距食堂」字段）+ 少量食堂地标，不再只推东区大食堂。  
- **坑与修复（运动类）**：  
  - `reweight_query` 误删「羽毛球」→ 检索词变成「我想打」→ 古籍馆自习霸榜  
  - 过滤为空时曾**回退全部 chunks** → LLM 对着自习资料说「没有羽毛球场」  
  - 修复：`_REWEIGHT_STRIP` 只剥泛词；检索用用户原话；过滤无运动命中则全库按 `sport_focus` 补捞  

### 2026-06-11 — 服务范围 Prompt 与早餐误拒

- **现象**：「推荐我一个地方吃早饭」未被 `is_out_of_scope()` 拦截，但 LLM 称只做「体育场馆」、拒绝餐饮推荐。  
- **原因**：`SYSTEM_PROMPT` 仍限定体育场馆，与已扩展的食堂/自习知识库不一致。  
- **处理**：`SYSTEM_PROMPT` / `OUT_OF_SCOPE_REPLY` 写明体育、餐饮、自习、活动场地均属范围；`app.py` 示例问题增加早饭推荐。  

### 2026-06-11 — 运动项目统一检索（`sport_terms.py`）

- **动机**：「踢足球」分词碎裂为「踢足」、关键词误命中游泳馆；需与羽毛球一样按**具体运动项目**过滤与排序。  
- **新增** `sport_terms.py`：`SPORT_ENTITIES` 含足球/篮球/排球/羽毛球/乒乓球/网球/游泳/健身/跑步/橄榄球等 20+ 项；每项 `aliases`（踢足球、打篮球…）+ `match`（足球场、篮球场…）。  
- **联动改动**：

| 文件 | 改动 |
|------|------|
| `sport_terms.py` | 新建；`extract_sports_from_query`、`chunk_matches_sports`、`sport_match_score` |
| `prompts.py` | `sport_focus` 写入 roles；运动类主任务只保留匹配该运动的 chunk；无命中则 `_sport_backup_chunks` |
| `retriever.py` | 分词优先 `SPORT_PHRASES`；`build_sport_synonyms()`；有具体运动时忽略单字「打/踢」加分 |

- **验证**：「我想去踢足球」→ 五人制足球场、紫云足球场入 Prompt，不含游泳馆；羽毛球/篮球/排球同类 query 正常。  
- **扩展方式**：在 `SPORT_ENTITIES` 增一项即可；知识库无对应 md 时仍走「资料未记载」模板。  

---

## 变更文件索引（便于 diff / 报告附录）

| 路径 | 说明 |
|------|------|
| `校园智能场馆匹配平台/*` | 2026-06-03 一次性初始化的全部脚手架 |
| `docs/image/实验报告/1780555211614.png` | 报告图 1：CLI 联调 |
| `docs/image/实验报告/gradio-p5-2026-06-04.png` | 报告图 2：Gradio 网页 |
| `docs/实验报告.md` §4 | CLI + 网页测试实录 |
| `app.py` | P5 Gradio 入口 |
| `README.md` | 含「网页使用说明（Gradio）」 |
| `prompts.py` | 引用行号；两阶段检索（方案 C）；`sport_focus` 运动过滤 |
| `retriever.py` | 段落展开行号；`sport_terms` 分词与同义词；泛化动词降噪 |
| `sport_terms.py` | **新建**：体育运动词表与匹配工具 |
| `conversation.py` | 两阶段开关；检索用用户原话 + 增强 query 合并 |
| `config.example.py` | `USE_TWO_STAGE_RETRIEVAL`、`MAX_SECTIONS_IN_PROMPT` |
| `app.py` | 示例「推荐吃早饭」；服务范围与 Prompt 对齐 |
| `test_retriever.py` | 引用行号自检 |
| `data/chunks.json` | rebuild 后 308 段含 `start_line`/`end_line` |
| `scripts/render_terminal_screenshot.py` | 可选：根据终端文本生成示意图 |
| `Cursor/User/settings.json` | 仅用户本机；为 docx/Markdown 编辑器关联，**不属于项目仓库** |

---

## 实现路线图（2026-06-03 定稿）

**目标对齐**：选题落在任务书「图书馆与场馆助手」范畴；项目名「校园智能场馆匹配平台」= 场馆场景的 RAG 问答/推荐。

**用户优先级**（本轮确认）：
1. 必做：方向一基础功能，重点 **边界处理** + **多轮上下文**
2. 必做升级：**文本向量化语义检索**（替代当前关键词 `retriever.py`）
3. 后期优化：特定场景回复灵活性（Prompt 细化）
4. 交付增强：**Gradio 网页聊天**（任务书进阶加分项）

**API 约束**：智能对话必须使用 **DeepSeek API**（`base_url=https://api.deepseek.com`，`model=deepseek-chat`），Key 放 `config.py` 勿提交。

**知识库硬性指标**：`knowledge/` 下 **≥15 个**本校场馆 `.md` 文件（每馆一份）；文件内 `##` 仅用于 RAG 切块。

**推荐实施阶段**（共 6 期，前 4 期为必做闭环）：

| 阶段 | 内容 | 主要改动文件 |
|------|------|----------------|
| P0 | 跑通 DeepSeek + knowledge ≥15 个 md | `config.py`, `knowledge/`, `llm.py` |
| P1 | 文档切块 + 索引构建脚本 | 新增 `indexer.py`, `data/chunks.json` 或 `vectors.npz` |
| P2 | 向量语义检索替换关键词 | `retriever.py`, `embedder.py` |
| P3 | 多轮对话 + 边界处理 Prompt | 新增 `conversation.py`, `prompts.py`, 改 `main.py` |
| P4 | CLI 联调与测试用例 | `main.py`, `tests/` 或 `docs/测试用例.md` |
| P5 | Gradio 网页 | 新增 `app.py` |
| P6 | 加分项：引用标注、有无知识库对比实验 | `main.py` / 报告 |

**P0–P3、P5 已完成并 push**；**P2 本机向量已用**；**待办**：知识库 ≥15 md、报告 §一–三/五、可选 P6。

---

*最后更新：2026-06-11（引用标注 + 两阶段检索方案 C + 运动词表 `sport_terms.py` + Prompt 服务范围扩展；改 `knowledge/` 或运动词表后重启 `app.py` 并视情况 `indexer --rebuild`）*
