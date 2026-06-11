# 使用说明：复制本文件为 config.py，填入你的 DeepSeek API Key
# 命令（在项目根目录 PowerShell）：
#   Copy-Item config.example.py config.py

# ========== DeepSeek 大模型（任务书要求）==========
API_BASE = "https://api.deepseek.com"
API_KEY = "在这里粘贴你的-key"
MODEL_NAME = "deepseek-chat"

TEMPERATURE = 0.3
API_TIMEOUT = 60
API_MAX_RETRIES = 2

# ========== 知识库路径 ==========
KNOWLEDGE_DIR = "knowledge"

# ========== P1 切块 / P2 向量索引 ==========
DATA_DIR = "data"
CHUNKS_FILE = "chunks.json"
EMBEDDINGS_FILE = "embeddings.npz"
CHUNK_MIN_CHARS = 30
BUILD_EMBEDDINGS_ON_INDEX = True

# 向量化方式：
#   tfidf                 — 离线可用，不下载模型（校园网推荐先用）
#   sentence_transformers — 语义向量，需联网下载模型
EMBEDDING_BACKEND = "tfidf"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
# 国内网络：用 hf-mirror；模型已下全后可配合 EMBEDDING_LOCAL_ONLY 离线加载
HF_ENDPOINT = "https://hf-mirror.com"
# True=只读本地缓存（不 ping huggingface.co）；首次下载或缓存坏了改 False
EMBEDDING_LOCAL_ONLY = True
USE_VECTOR_INDEX = True
# tfidf 相似度分数偏低，约 0.1~0.3；sentence_transformers 可用 0.3~0.5
SIMILARITY_THRESHOLD = 0.1

# ========== 检索与 Prompt ==========
TOP_K = 5
# 向量检索先取若干 chunk，再按 md 文件合并后送入 Prompt
RETRIEVE_POOL_SIZE = 20
MAX_VENUES_IN_PROMPT = 3
MAX_SECTIONS_IN_PROMPT = 12

# 两阶段检索增强：意图分类预筛选 + query 重加权（见 prompts.py）
USE_TWO_STAGE_RETRIEVAL = True

# ========== 对比实验开关 ==========
# True = 正常使用知识库（RAG 模式）
# False = 不使用知识库（纯 LLM 模式，用于对比实验）
USE_KNOWLEDGE_BASE = True
