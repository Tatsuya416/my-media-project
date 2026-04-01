from .base import Agent


class CPOAgent(Agent):
    """CPO（Chief Production Officer）- 制作責任者エージェント"""

    def __init__(self, config: dict):
        super().__init__("cpo", config)

    def write_article(self, title: str, outline: str, target_length: str = "800〜1200文字") -> str:
        """記事を制作する"""
        prompt = f"""
以下のタイトルとアウトラインで記事を制作してください。

タイトル: {title}
目標文字数: {target_length}
アウトライン:
{outline}

以下の要素を含めてください:
1. 読者を引き込む導入文
2. 各セクションの具体的な内容
3. データや具体例の活用
4. 自然なCTA（行動喚起）
5. まとめ
"""
        return self.ask(prompt)

    def write_social_post(self, platform: str, topic: str, key_message: str) -> str:
        """SNS投稿を制作する"""
        prompt = f"""
以下の条件でSNS投稿を制作してください。

プラットフォーム: {platform}
トピック: {topic}
キーメッセージ: {key_message}

プラットフォームの特性に合わせ、エンゲージメントを最大化する投稿を作成してください。
ハッシュタグの提案も含めてください。
"""
        return self.ask(prompt)

    def write_video_script(self, topic: str, duration: str, style: str = "説明系") -> str:
        """動画スクリプトを制作する"""
        prompt = f"""
以下の条件で動画スクリプトを制作してください。

トピック: {topic}
動画の長さ: {duration}
スタイル: {style}

スクリプトに含めてください:
1. 冒頭3秒のフック（視聴者を引き込む一言）
2. 本編（セクション分け）
3. 明確なCTA
4. アウトロ

シーン描写やテロップ指示も含めてください。
"""
        return self.ask(prompt)

    def create_content_calendar(self, month: str, theme: str, frequency: str) -> str:
        """コンテンツカレンダーを作成する"""
        prompt = f"""
以下の条件でコンテンツカレンダーを作成してください。

対象月: {month}
月間テーマ: {theme}
配信頻度: {frequency}

各コンテンツについて以下を含めてください:
- 配信日
- コンテンツタイトル（案）
- フォーマット（記事/動画/SNS等）
- 主要トピック
- 担当者（CSO/CCO/CPO/CDO）
"""
        return self.ask(prompt)
