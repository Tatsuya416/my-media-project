from .base import Agent


class CDOAgent(Agent):
    """CDO（Chief Data Officer）- データ分析責任者エージェント"""

    def __init__(self, config: dict):
        super().__init__("cdo", config)

    def analyze_performance(self, metrics: dict, period: str) -> str:
        """パフォーマンスデータを分析する"""
        metrics_str = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
        prompt = f"""
以下の指標データを分析し、インサイトと改善提案を提供してください。

分析期間: {period}
指標データ:
{metrics_str}

以下の形式で報告してください:
1. 主要な発見（3〜5点）
2. 好調な点とその要因
3. 課題と原因仮説
4. 優先改善アクション（トップ3）
5. 次のアクションの推奨
"""
        return self.ask(prompt)

    def identify_top_content(self, content_data: list[dict]) -> str:
        """パフォーマンスの高いコンテンツを特定・分析する"""
        data_lines = []
        for item in content_data:
            data_lines.append(
                f"- タイトル: {item.get('title', 'N/A')}, "
                f"PV: {item.get('pv', 0)}, "
                f"滞在時間: {item.get('avg_time', 'N/A')}, "
                f"CVR: {item.get('cvr', 'N/A')}"
            )
        data_str = "\n".join(data_lines)

        prompt = f"""
以下のコンテンツデータを分析し、成功パターンを特定してください。

{data_str}

分析してください:
1. トップパフォーマーの共通特徴
2. 成功要因の仮説
3. 低パフォーマーの改善点
4. 今後のコンテンツ制作への示唆
"""
        return self.ask(prompt)

    def design_ab_test(self, hypothesis: str, element: str) -> str:
        """A/Bテストを設計する"""
        prompt = f"""
以下の条件でA/Bテストを設計してください。

仮説: {hypothesis}
テスト対象要素: {element}

テスト設計に含めてください:
1. テスト概要（A案・B案の詳細）
2. 評価指標（主要KPI・補助指標）
3. 必要サンプルサイズの目安
4. テスト期間の推奨
5. 成功・失敗の判定基準
6. リスクと注意点
"""
        return self.ask(prompt)

    def generate_report(self, period: str, metrics: dict, goals: dict) -> str:
        """定期レポートを生成する"""
        metrics_str = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
        goals_str = "\n".join(f"- {k}: {v}" for k, v in goals.items())

        prompt = f"""
以下のデータを基に、{period}のパフォーマンスレポートを作成してください。

実績指標:
{metrics_str}

目標指標:
{goals_str}

レポートに含めてください:
1. エグゼクティブサマリー
2. 目標達成状況（達成率）
3. 主要トレンドと変化
4. 次期に向けた推奨アクション
5. 注目すべき機会とリスク
"""
        return self.ask(prompt)
