"""
RequestInspector - LLM 请求检视插件

在所有其他插件（PromptTags、LivingMemory 等）完成注入之后，
以 priority=-1000 最后执行，打印发给模型的完整请求构成。

两种模式：
- summary（默认）：只打印 system_prompt / prompt / contexts 的字符数
- full：打印每个字段的完整内容

在 AstrBot 面板中启用/禁用此插件即可控制是否输出。
通过配置项 output_mode 切换 summary / full 模式。

F(A) = A(F)
"""

from typing import Any

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register


@register(
    "字数统计",
    "FelisAbyssalis",
    "LLM 请求检视插件 - 在所有注入完成后打印发给模型的完整请求构成",
    "1.0.0",
    "https://github.com/EmilyCheoh/astrbot_request_inspector",
)
class RequestInspectorPlugin(Star):

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._output_mode = str(config.get("output_mode", "summary")).strip()
        logger.info(
            f"请求检视插件初始化完成 (模式: {self._output_mode})"
        )

    # -------------------------------------------------------------------
    # 工具方法
    # -------------------------------------------------------------------

    @staticmethod
    def _extract_text(msg: Any) -> str:
        """从单条 context 消息中提取纯文本内容。"""
        if isinstance(msg, str):
            return msg
        if isinstance(msg, dict):
            content = msg.get("content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for part in content:
                    if (
                        isinstance(part, dict)
                        and part.get("type") == "text"
                    ):
                        parts.append(part.get("text", ""))
                return "".join(parts)
        return ""

    @staticmethod
    def _extract_role(msg: Any) -> str:
        """从单条 context 消息中提取 role。"""
        if isinstance(msg, dict):
            return msg.get("role", "?")
        return "?"

    # -------------------------------------------------------------------
    # 事件钩子
    # -------------------------------------------------------------------

    @filter.on_llm_request(priority=-1000)
    async def handle_inspect(
        self, event: AstrMessageEvent, req: ProviderRequest
    ):
        """
        在所有插件注入完成后，打印请求的完整构成。

        priority=-1000 确保在 PromptTags (-500) 之后执行，
        看到的是最终发给模型的状态。
        """
        try:
            session_id = event.unified_msg_origin or "unknown"
            mode = self._output_mode

            # --- 计算各部分长度 ---
            sp = req.system_prompt or ""
            pr = req.prompt or ""
            contexts = req.contexts or []

            sp_len = len(sp)
            pr_len = len(pr)
            ctx_count = len(contexts)
            ctx_lengths = []
            ctx_total = 0

            for msg in contexts:
                text = self._extract_text(msg)
                ctx_lengths.append(len(text))
                ctx_total += len(text)

            # --- Summary 模式：只打印字符数 ---
            logger.info(
                f"RequestInspector: "
                f"system_prompt={sp_len}字 | "
                f"prompt={pr_len}字 | "
                f"contexts={ctx_count}条/{ctx_total}字"
            )

            if mode != "full":
                return

            # --- Full 模式：打印完整内容 ---
            separator = "=" * 60

            logger.info(
                f"RequestInspector 【FULL】"
                f"{separator}"
            )

            # system_prompt
            logger.info(
                f"RequestInspector 【system_prompt】"
                f"({sp_len}字):\n{sp}"
            )

            # prompt
            logger.info(
                f"RequestInspector 【prompt】"
                f"({pr_len}字):\n{pr}"
            )

            # contexts
            if ctx_count > 0:
                for i, msg in enumerate(contexts):
                    role = self._extract_role(msg)
                    text = self._extract_text(msg)
                    logger.info(
                        f"RequestInspector "
                        f"[context #{i}] role={role} ({len(text)}字):\n"
                        f"{text}"
                    )
            else:
                logger.info(
                    f"RequestInspector [contexts] 空"
                )

            logger.info(
                f"RequestInspector 【END】"
                f"{separator}"
            )

        except Exception as e:
            logger.error(
                f"RequestInspector: 检视时发生错误: {e}",
                exc_info=True,
            )

    # -------------------------------------------------------------------
    # 生命周期
    # -------------------------------------------------------------------

    async def terminate(self):
        logger.info("请求检视插件已停止")
