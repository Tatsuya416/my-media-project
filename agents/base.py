import json
import os
from pathlib import Path
from typing import Optional

import anthropic


class Agent:
    """メディアプロジェクト用AIエージェントの基底クラス"""

    def __init__(self, agent_id: str, config: dict):
        self.agent_id = agent_id
        self.agent_config = config["agents"][agent_id]
        self.model = config["model"]
        self.max_tokens = config["max_tokens"]
        self.name = self.agent_config["name"]
        self.role = self.agent_config["role"]
        self.description = self.agent_config["description"]

        # システムプロンプトを読み込む
        project_root = Path(__file__).parent.parent
        prompt_path = project_root / self.agent_config["prompt_file"]
        self.system_prompt = prompt_path.read_text(encoding="utf-8")

        # Anthropicクライアントの初期化
        self.client = anthropic.Anthropic()
        self.conversation_history: list[dict] = []

    def chat(self, message: str, use_thinking: bool = False) -> str:
        """エージェントにメッセージを送り、応答を取得する"""
        self.conversation_history.append({"role": "user", "content": message})

        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self.system_prompt,
            "messages": self.conversation_history,
        }

        if use_thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        response = self.client.messages.create(**kwargs)

        # テキストブロックを取得
        reply = ""
        for block in response.content:
            if block.type == "text":
                reply = block.text
                break

        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def ask(self, message: str) -> str:
        """会話履歴を使わず、単発で質問する"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=[{"role": "user", "content": message}],
        )

        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

    def reset_conversation(self):
        """会話履歴をリセットする"""
        self.conversation_history = []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' role='{self.role}'>"
