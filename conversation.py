"""多轮对话管理（P3）"""

from __future__ import annotations

try:
    import config
except ImportError:

    class config:  # type: ignore
        USE_TWO_STAGE_RETRIEVAL = True

from llm import LLMError, chat
from prompts import (
    OUT_OF_SCOPE_REPLY,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_NO_KB,
    build_enhanced_rag_user_message,
    build_enhanced_retrieval_query,
    build_rag_user_message,
    build_retrieval_query,
    is_out_of_scope,
)
from retriever import retrieve_for_prompt


class Conversation:
    """维护 DeepSeek messages 历史，支持连续追问与边界处理。"""

    def __init__(self, use_kb: bool = True) -> None:
        """初始化对话。

        Args:
            use_kb: 是否使用知识库。True 使用 RAG，False 纯 LLM（用于对比实验）
        """
        self.use_kb = use_kb
        self.reset()

    def reset(self) -> None:
        # 根据是否使用知识库选择系统提示词
        system_prompt = SYSTEM_PROMPT_NO_KB if not self.use_kb else SYSTEM_PROMPT
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]
        # (用户原始输入, 助手回复)，仅用于检索 query 改写
        self.raw_history: list[tuple[str, str]] = []

    def turn(self, user_input: str) -> str:
        user_input = user_input.strip()
        if not user_input:
            return "请输入与场馆/活动相关的问题。"

        if is_out_of_scope(user_input):
            answer = OUT_OF_SCOPE_REPLY
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": answer})
            return answer

        # 根据初始化时的设置决定是否使用知识库
        if not self.use_kb:
            # 不使用知识库：直接用用户原始问题
            user_msg = user_input
        elif getattr(config, "USE_TWO_STAGE_RETRIEVAL", True):
            retrieval_q = build_enhanced_retrieval_query(user_input, self.raw_history)
            # 检索始终用用户原话，避免 reweight 削弱「羽毛球」等具体词
            chunks = retrieve_for_prompt(user_input)
            if retrieval_q != user_input:
                extra = retrieve_for_prompt(retrieval_q)
                seen = {c.get("id") for c in chunks}
                for c in extra:
                    if c.get("id") not in seen:
                        chunks.append(c)
                        seen.add(c.get("id"))
            user_msg = build_enhanced_rag_user_message(user_input, chunks)
        else:
            retrieval_q = build_retrieval_query(user_input, self.raw_history)
            chunks = retrieve_for_prompt(retrieval_q)
            user_msg = build_rag_user_message(user_input, chunks)

        self.messages.append({"role": "user", "content": user_msg})
        try:
            answer = chat(self.messages)
        except LLMError:
            self.messages.pop()
            raise

        self.messages.append({"role": "assistant", "content": answer})
        self.raw_history.append((user_input, answer))
        return answer

    @property
    def turn_count(self) -> int:
        return len(self.raw_history)
