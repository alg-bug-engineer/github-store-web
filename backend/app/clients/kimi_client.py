import httpx
from typing import Dict, Any, List, Optional

from app.core.config import settings


class KimiAIAssistant:
    def __init__(self):
        self.api_key = settings.KIMI_API_KEY
        self.endpoint = f"{settings.KIMI_API_BASE}/v1/chat/completions"

    async def chat(
        self,
        user_message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        对话接口
        """
        system_prompt = self._build_system_prompt(context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        payload = {"model": "moonshot-v1-8k", "messages": messages, "temperature": 0.7}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.endpoint, headers=headers, json=payload, timeout=60
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise e

    def _build_system_prompt(self, context: Optional[str]) -> str:
        prompt = """你是一个开源应用助手,帮助用户发现和使用GitHub上的优质应用。

你的职责:
1. 理解用户需求,推荐合适的应用
2. 用通俗易懂的语言解释技术概念
3. 提供下载和安装指导
4. 回答应用相关问题

回答原则:
- 语言简洁友好,避免技术术语
- 优先推荐安全、活跃的项目
- 如果不确定,诚实说明
- 每次最多推荐3个应用
"""
        if context:
            prompt += f"\n当前页面项目:\n{context}"
        return prompt


kimi_client = KimiAIAssistant()
