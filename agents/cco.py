from .base import Agent


class CCOAgent(Agent):
    """CCO（Chief Content Officer）- 編集責任者エージェント"""

    def __init__(self, config: dict):
        super().__init__("cco", config)

    def edit_content(self, content: str, style_notes: str = "") -> str:
        """コンテンツを編集・改善する"""
        style_section = f"\nスタイル指示: {style_notes}" if style_notes else ""
        prompt = f"""
以下のコンテンツを編集してください。{style_section}

--- 原文 ---
{content}
--- 原文ここまで ---

以下の観点から編集してください:
1. 文章の明瞭さと読みやすさ
2. 見出し・構成の最適化
3. SEOキーワードの自然な使用
4. 誤字脱字・文法の修正
5. CTAの明確化

編集後のコンテンツと、主な修正点を提示してください。
"""
        return self.ask(prompt)

    def review_seo(self, content: str, target_keywords: list[str]) -> str:
        """SEO観点でコンテンツをレビューする"""
        keywords_str = ", ".join(target_keywords)
        prompt = f"""
以下のコンテンツをSEO観点でレビューしてください。

ターゲットキーワード: {keywords_str}

--- コンテンツ ---
{content}
--- コンテンツここまで ---

以下を評価してください:
1. キーワードの使用状況（自然さ・頻度）
2. タイトル・見出しの最適化状況
3. メタディスクリプションの提案
4. 内部・外部リンクの機会
5. 改善優先度順の推奨アクション
"""
        return self.ask(prompt)

    def create_style_guide(self, brand_values: str, target_audience: str) -> str:
        """スタイルガイドを作成する"""
        prompt = f"""
以下の情報に基づいて、コンテンツスタイルガイドを作成してください。

ブランド価値観: {brand_values}
ターゲットオーディエンス: {target_audience}

スタイルガイドに含めてください:
1. トーン&マナー（文体・語調）
2. 表記ルール（漢字・ひらがな・カタカナの使い分け）
3. 禁止表現・使用注意ワード
4. 見出し・段落の書き方
5. 数字・単位の表記方法
"""
        return self.ask(prompt)
