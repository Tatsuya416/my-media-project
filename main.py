"""
メディアプロジェクト AIエージェントオーケストレーター

CSO（戦略）、CCO（編集）、CPO（制作）、CDO（分析）の4エージェントを管理する。
"""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from agents import CSOAgent, CCOAgent, CPOAgent, CDOAgent
from reporter import Reporter

load_dotenv()


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    return json.loads(config_path.read_text(encoding="utf-8"))


def demo_workflow():
    """デモ: 4エージェントが連携してコンテンツを制作するワークフロー"""
    config = load_config()
    reporter = Reporter(reports_dir=Path(__file__).parent / "reports", label="demo")
    output = reporter.output

    # エージェントを初期化
    cso = CSOAgent(config)
    cco = CCOAgent(config)
    cpo = CPOAgent(config)
    cdo = CDOAgent(config)

    output("=" * 60)
    output("メディアプロジェクト AIエージェントシステム 起動")
    output("=" * 60)
    output(f"✓ {cso.name} - {cso.description}")
    output(f"✓ {cco.name} - {cco.description}")
    output(f"✓ {cpo.name} - {cpo.description}")
    output(f"✓ {cdo.name} - {cdo.description}")
    output()

    # Step 1: CSO が戦略を立案
    output("━" * 60)
    output("【STEP 1】CSO: コンテンツ戦略の立案")
    output("━" * 60)
    strategy = cso.create_strategy(
        topic="AIツールを使った業務効率化",
        goals="月間PV 10万達成、メルマガ登録者1,000人獲得"
    )
    output(strategy)
    output()

    # Step 2: CPO が記事を制作
    output("━" * 60)
    output("【STEP 2】CPO: 記事コンテンツの制作")
    output("━" * 60)
    article = cpo.write_article(
        title="ChatGPTで会議時間を50%削減する5つの方法",
        outline="""
- 導入: AIツール活用の現状
- 方法1: 議事録の自動生成
- 方法2: アジェンダ作成の効率化
- 方法3: 事前資料の要約
- 方法4: フォローアップメールの自動化
- 方法5: 決定事項のタスク化
- まとめとCTA
"""
    )
    output(article)
    output()

    # Step 3: CCO が記事を編集
    output("━" * 60)
    output("【STEP 3】CCO: 記事の編集・品質チェック")
    output("━" * 60)
    edited = cco.edit_content(
        content=article,
        style_notes="ビジネスパーソン向け、専門用語は平易に説明する"
    )
    output(edited)
    output()

    # Step 4: CDO がパフォーマンスを分析
    output("━" * 60)
    output("【STEP 4】CDO: パフォーマンス分析レポート")
    output("━" * 60)
    analysis = cdo.analyze_performance(
        metrics={
            "月間PV": "45,320",
            "ユニークユーザー数": "32,100",
            "平均滞在時間": "2分34秒",
            "直帰率": "68%",
            "メルマガ登録数": "234件",
            "SNSシェア数": "892回"
        },
        period="2024年3月"
    )
    output(analysis)
    output()

    output("=" * 60)
    output("ワークフロー完了")
    output("=" * 60)

    reporter.save()


def interactive_mode():
    """対話モード: エージェントを選んで対話する"""
    config = load_config()

    agents = {
        "1": CSOAgent(config),
        "2": CCOAgent(config),
        "3": CPOAgent(config),
        "4": CDOAgent(config),
    }

    print("=" * 60)
    print("対話モード - エージェントを選択してください")
    print("=" * 60)
    for key, agent in agents.items():
        print(f"  {key}. {agent.name}")
    print("  0. 終了")
    print()

    selected_agent = None

    while True:
        if selected_agent is None:
            choice = input("エージェントを選択 (0-4): ").strip()
            if choice == "0":
                print("終了します。")
                break
            if choice not in agents:
                print("無効な選択です。")
                continue
            selected_agent = agents[choice]
            print(f"\n{selected_agent.name} との対話を開始します。(exitで終了、resetで会話リセット)\n")

        user_input = input(f"あなた → {selected_agent.name.split('（')[0]}: ").strip()

        if user_input.lower() == "exit":
            selected_agent = None
            print("\nエージェント選択に戻ります。\n")
            continue
        elif user_input.lower() == "reset":
            selected_agent.reset_conversation()
            print("会話をリセットしました。\n")
            continue
        elif not user_input:
            continue

        response = selected_agent.chat(user_input)
        print(f"\n{selected_agent.name}:\n{response}\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_workflow()
    else:
        interactive_mode()
