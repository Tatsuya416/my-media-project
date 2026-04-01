"""
Reporter: TXT / HTML レポートを生成・保存するユーティリティ

demo_workflow() および将来の interactive mode から共用できる設計。
"""

import html as html_lib
import subprocess
from datetime import datetime
from pathlib import Path


class Reporter:
    def __init__(self, reports_dir: Path, label: str = "demo"):
        self.lines: list[str] = []
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.label = label
        self.txt_path = self.reports_dir / f"{ts}_{label}.txt"
        self.html_path = self.reports_dir / f"{ts}_{label}.html"
        self.started_at = datetime.now()

    def output(self, text: str = "") -> None:
        """標準出力に表示しつつ、内部バッファに蓄積する"""
        print(text)
        self.lines.append(text)

    def save(self, open_browser: bool = False) -> tuple[Path, Path]:
        """TXT と HTML を両方保存し、インデックスを更新する"""
        self.txt_path.write_text("\n".join(self.lines), encoding="utf-8")
        self.html_path.write_text(self._build_html(), encoding="utf-8")
        self._update_index()

        print(f"\n📄 TXT  : {self.txt_path}")
        print(f"🌐 HTML : {self.html_path}")
        print(f"📋 INDEX: {self.reports_dir / 'index.html'}")

        if open_browser:
            self.open_html()

        return self.txt_path, self.html_path

    def open_html(self) -> None:
        """保存した HTML をデフォルトブラウザで開く"""
        subprocess.run(["open", str(self.html_path)])

    # ─────────────────────────────────────────
    # HTML生成
    # ─────────────────────────────────────────

    def _build_html(self) -> str:
        generated_at = self.started_at.strftime("%Y年%m月%d日 %H:%M:%S")
        content_escaped = html_lib.escape("\n".join(self.lines))
        steps_html = self._build_steps_html()

        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AIエージェント実行レポート — {generated_at}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans",
                   "Noto Sans JP", "Yu Gothic", sans-serif;
      background: #f5f5f7;
      color: #1d1d1f;
      padding: 48px 20px 64px;
      line-height: 1.6;
    }}
    .container {{ max-width: 900px; margin: 0 auto; }}

    /* ── カード共通 ── */
    .card {{
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 2px 24px rgba(0, 0, 0, 0.07);
      padding: 36px 40px;
      margin-bottom: 24px;
    }}

    /* ── ヘッダーカード ── */
    .header h1 {{
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 6px;
      letter-spacing: -0.01em;
    }}
    .header .meta {{
      font-size: 0.875rem;
      color: #6e6e73;
      margin-bottom: 28px;
    }}

    /* ── 実行ステップ一覧 ── */
    .steps-label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #6e6e73;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 10px;
    }}
    .steps-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .steps-list li {{
      background: #f5f5f7;
      border-radius: 8px;
      padding: 9px 14px;
      font-size: 0.88rem;
    }}

    /* ── ログカード ── */
    .log-label {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #6e6e73;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      margin-bottom: 14px;
    }}
    pre {{
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 0.8rem;
      line-height: 1.7;
      background: #f5f5f7;
      border-radius: 10px;
      padding: 24px;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    /* ── フッター ── */
    .footer {{
      text-align: center;
      font-size: 0.78rem;
      color: #aeaeb2;
      margin-top: 4px;
    }}
  </style>
</head>
<body>
  <div class="container">

    <!-- ヘッダーカード -->
    <div class="card header">
      <h1>🤖 AIエージェント実行レポート</h1>
      <div class="meta">生成日時: {generated_at}</div>
      {steps_html}
    </div>

    <!-- ログカード -->
    <div class="card">
      <div class="log-label">実行ログ</div>
      <pre>{content_escaped}</pre>
    </div>

    <div class="footer">メディアプロジェクト AIエージェントシステム</div>
  </div>
</body>
</html>"""

    def _update_index(self) -> None:
        """reports/index.html をレポート一覧ページとして再生成する"""
        reports_dir = self.reports_dir
        html_files = sorted(reports_dir.glob("*.html"), reverse=True)
        html_files = [f for f in html_files if f.name != "index.html"]

        rows = ""
        for f in html_files:
            name = f.stem  # 例: 2026-04-01_14-21-01_demo
            parts = name.split("_", 2)
            date = parts[0] if len(parts) > 0 else ""
            time = parts[1].replace("-", ":") if len(parts) > 1 else ""
            label = parts[2] if len(parts) > 2 else ""
            rows += (
                f'<tr>'
                f'<td>{html_lib.escape(date)}</td>'
                f'<td>{html_lib.escape(time)}</td>'
                f'<td>{html_lib.escape(label)}</td>'
                f'<td><a href="{html_lib.escape(f.name)}">開く →</a></td>'
                f'</tr>\n'
            )

        index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AIエージェント レポート一覧</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans",
                   "Noto Sans JP", sans-serif;
      background: #f5f5f7;
      color: #1d1d1f;
      padding: 48px 20px 64px;
    }}
    .container {{ max-width: 760px; margin: 0 auto; }}
    .card {{
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 2px 24px rgba(0,0,0,0.07);
      padding: 36px 40px;
    }}
    h1 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 6px; }}
    .meta {{ font-size: 0.85rem; color: #6e6e73; margin-bottom: 28px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{
      text-align: left;
      font-size: 0.75rem;
      font-weight: 600;
      color: #6e6e73;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 0 12px 10px 0;
      border-bottom: 1px solid #e5e5ea;
    }}
    td {{
      padding: 12px 12px 12px 0;
      border-bottom: 1px solid #f0f0f5;
      font-size: 0.9rem;
    }}
    tr:last-child td {{ border-bottom: none; }}
    a {{ color: #0071e3; text-decoration: none; font-weight: 500; }}
    a:hover {{ text-decoration: underline; }}
    .footer {{
      text-align: center;
      font-size: 0.78rem;
      color: #aeaeb2;
      margin-top: 20px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>🤖 AIエージェント レポート一覧</h1>
      <div class="meta">メディアプロジェクト — 実行履歴</div>
      <table>
        <thead>
          <tr>
            <th>日付</th><th>時刻</th><th>種別</th><th>リンク</th>
          </tr>
        </thead>
        <tbody>
{rows}        </tbody>
      </table>
    </div>
    <div class="footer">メディアプロジェクト AIエージェントシステム</div>
  </div>
</body>
</html>"""
        (reports_dir / "index.html").write_text(index_html, encoding="utf-8")

    def _build_steps_html(self) -> str:
        """出力行から【STEP N】行を抽出してリスト化する"""
        steps = [line.strip() for line in self.lines if line.strip().startswith("【STEP")]
        if not steps:
            return ""
        items = "".join(
            f"<li>{html_lib.escape(s)}</li>" for s in steps
        )
        return f"""<div class="steps-label">実行ステップ</div>
      <ul class="steps-list">{items}</ul>"""
