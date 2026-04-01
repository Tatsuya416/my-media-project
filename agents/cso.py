from .base import Agent


class CSOAgent(Agent):
    """CSO（Chief Strategy Officer）- 戦略責任者エージェント"""

    def __init__(self, config: dict):
        super().__init__("cso", config)

    def create_strategy(self, topic: str, goals: str) -> str:
        """コンテンツ戦略を立案する"""
        prompt = f"""
以下のトピックとゴールに基づいて、コンテンツ戦略を立案してください。

トピック: {topic}
ゴール: {goals}

以下の項目を含めてください:
1. 戦略概要
2. ターゲットオーディエンス
3. 主要KPI
4. コンテンツの方向性
5. 優先アクション（3〜5個）
"""
        return self.ask(prompt)

    def analyze_competitors(self, competitors: list[str]) -> str:
        """競合分析を行う"""
        competitors_str = "\n".join(f"- {c}" for c in competitors)
        prompt = f"""
以下の競合メディアを分析し、差別化戦略を提案してください。

競合メディア:
{competitors_str}

分析項目:
1. 各競合の強み・弱み
2. 市場ポジショニングのギャップ
3. 差別化のための戦略提案
"""
        return self.ask(prompt)

    def find_amplifying_tactics(
        self,
        cdo_output: str,
        trend_data: str = "",
    ) -> str:
        """CDOの分析に外部トレンドを重ねて、効果の高い施策を導く"""
        trend_section = (
            f"外部トレンド情報:\n{trend_data}"
            if trend_data
            else "（外部トレンド情報なし — あなたの知識から市場動向を補完してください）"
        )
        prompt = f"""
CDOから以下の分析・改善提案が出ています。
この提案に対して、外部トレンドも加味した上で「さらに効く施策」を見つけてください。

【CDOの分析・改善提案】
{cdo_output}

【外部トレンド】
{trend_section}

以下の形式で出力してください:

## 1. CDOの示唆の要約
## 2. 外部トレンドから見つかった追い風
## 3. 追加で試すべき施策
## 4. なぜその施策が効くのか
## 5. 優先順位
## 6. すぐ試す案 / 中期で試す案
"""
        return self.ask(prompt)

    def set_kpis(self, timeframe: str, current_metrics: dict) -> str:
        """KPIを設定する"""
        metrics_str = "\n".join(f"- {k}: {v}" for k, v in current_metrics.items())
        prompt = f"""
以下の現状指標に基づいて、{timeframe}のKPI目標を設定してください。

現状指標:
{metrics_str}

KPI設定に含めてください:
1. 各指標の目標値と根拠
2. 優先順位
3. マイルストーン
"""
        return self.ask(prompt)
