"""
Reporter: 意思決定レポートを生成・保存するユーティリティ

単なる実行ログではなく、
「誰が見ても判断できる意思決定資料」を生成する。
"""

import html as html_lib
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────
# データモデル
# ─────────────────────────────────────────

@dataclass
class EvaluatedIssue:
    title: str
    score: int                    # 0–9
    verdict: str                  # "試す価値あり" | "まだ早い" | "不要"
    source_tier: str              # "A" | "B" | "C"
    issue: str                    # 核心の問い
    structure: str                # なぜ起きているか
    insight: str                  # 人間のインサイト（1文）
    future: str                   # 半歩先の未来
    actions: list[str]            # 明日からのアクション
    sources: list[str]            # 出典
    priority: int = 1


@dataclass
class ExecutiveSummary:
    conclusion: str
    top_theme: str
    key_insight: str
    immediate_action: str


@dataclass
class KeyInsight:
    title: str
    body: str
    why_now: str


@dataclass
class RecommendedActions:
    now: list[str] = field(default_factory=list)
    next_: list[str] = field(default_factory=list)
    monitor: list[str] = field(default_factory=list)


@dataclass
class CDOMetric:
    name: str
    estimate: str
    direction: str   # "up" | "down" | "neutral"
    reason: str


@dataclass
class ImprovementHypothesis:
    what: str
    why: str
    metric_impact: str
    priority: str    # "高" | "中" | "低"


@dataclass
class CDOAnalysis:
    metrics: list[CDOMetric] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    hypotheses: list[ImprovementHypothesis] = field(default_factory=list)


@dataclass
class PDCADesign:
    what_to_test: list[str] = field(default_factory=list)
    what_to_measure: list[str] = field(default_factory=list)
    how_to_judge: str = ""
    next_iteration: str = ""
    minimum_experiment: str = ""


# ─────────────────────────────────────────
# Reporter 本体
# ─────────────────────────────────────────

class Reporter:
    def __init__(self, reports_dir: Path, label: str = "report"):
        self.lines: list[str] = []
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.label = label
        self.txt_path = self.reports_dir / f"{ts}_{label}.txt"
        self.html_path = self.reports_dir / f"{ts}_{label}.html"
        self.started_at = datetime.now()

        # 構造化データ
        self.summary: Optional[ExecutiveSummary] = None
        self.issues: list[EvaluatedIssue] = []
        self.insights: list[KeyInsight] = []
        self.actions: Optional[RecommendedActions] = None
        self.cdo: Optional[CDOAnalysis] = None
        self.pdca: Optional[PDCADesign] = None
        self.report_title: str = "イシュー分析・意思決定レポート"

    # ─── 構造化データ設定 API ───

    def set_title(self, title: str) -> None:
        self.report_title = title

    def set_summary(self, conclusion: str, top_theme: str,
                    key_insight: str, immediate_action: str) -> None:
        self.summary = ExecutiveSummary(conclusion, top_theme, key_insight, immediate_action)

    def add_issue(self, title: str, score: int, verdict: str, source_tier: str,
                  issue: str, structure: str, insight: str, future: str,
                  actions: list[str], sources: list[str], priority: int = 1) -> None:
        self.issues.append(EvaluatedIssue(
            title=title, score=score, verdict=verdict, source_tier=source_tier,
            issue=issue, structure=structure, insight=insight, future=future,
            actions=actions, sources=sources, priority=priority
        ))

    def add_insight(self, title: str, body: str, why_now: str = "") -> None:
        self.insights.append(KeyInsight(title=title, body=body, why_now=why_now))

    def set_actions(self, now: list[str], next_: list[str], monitor: list[str]) -> None:
        self.actions = RecommendedActions(now=now, next_=next_, monitor=monitor)

    def set_cdo(self, metrics: list[CDOMetric] = None,
                strengths: list[str] = None, weaknesses: list[str] = None,
                hypotheses: list[ImprovementHypothesis] = None) -> None:
        self.cdo = CDOAnalysis(
            metrics=metrics or [],
            strengths=strengths or [],
            weaknesses=weaknesses or [],
            hypotheses=hypotheses or [],
        )

    def set_pdca(self, what_to_test: list[str], what_to_measure: list[str],
                 how_to_judge: str, next_iteration: str,
                 minimum_experiment: str) -> None:
        self.pdca = PDCADesign(
            what_to_test=what_to_test,
            what_to_measure=what_to_measure,
            how_to_judge=how_to_judge,
            next_iteration=next_iteration,
            minimum_experiment=minimum_experiment,
        )

    # ─── レガシー API ───

    def output(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    # ─── 保存 ───

    def save(self, open_browser: bool = False) -> tuple[Path, Path]:
        self.txt_path.write_text("\n".join(self.lines), encoding="utf-8")
        self.html_path.write_text(self._build_html(), encoding="utf-8")
        self._update_index()

        index_path = self.reports_dir / "index.html"
        print(f"\n📄 TXT   : {self.txt_path}")
        print(f"🌐 HTML  : {self.html_path}")
        print(f"📋 INDEX : {index_path}")

        if open_browser:
            self.open_html()

        return self.txt_path, self.html_path

    def open_html(self) -> None:
        subprocess.run(["open", str(self.html_path)])

    # ─────────────────────────────────────────
    # HTML 生成
    # ─────────────────────────────────────────

    def _build_html(self) -> str:
        generated_at = self.started_at.strftime("%Y年%m月%d日 %H:%M")
        e = html_lib.escape

        sections = []
        sections.append(self._html_header(generated_at))

        if self.summary:
            sections.append(self._html_executive_summary())

        if self.issues:
            sections.append(self._html_top_issues())
            sections.append(self._html_issues_table())

        if self.insights:
            sections.append(self._html_insights())

        if self.actions:
            sections.append(self._html_actions())

        if self.cdo:
            sections.append(self._html_cdo())

        if self.pdca:
            sections.append(self._html_pdca())

        if self.lines:
            sections.append(self._html_log())

        sections.append('<div class="footer">Media Company OS — 意思決定レポートシステム</div>')

        body = "\n".join(sections)

        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(self.report_title)} — {generated_at}</title>
  {self._css()}
</head>
<body>
  <div class="container">
    {body}
  </div>
</body>
</html>"""

    # ─── セクション別 HTML ───

    def _html_header(self, generated_at: str) -> str:
        e = html_lib.escape
        return f"""
    <div class="page-header">
      <div>
        <div class="page-label">MEDIA STRATEGY REPORT</div>
        <h1 class="page-title">{e(self.report_title)}</h1>
        <div class="page-meta">生成日時: {generated_at} &nbsp;|&nbsp; ラベル: {e(self.label)}</div>
      </div>
    </div>"""

    def _html_executive_summary(self) -> str:
        s = self.summary
        e = html_lib.escape
        return f"""
    <div class="card exec-card">
      <div class="section-label">Executive Summary</div>
      <div class="exec-grid">
        <div class="exec-item exec-conclusion">
          <div class="exec-item-label">結論</div>
          <div class="exec-item-value">{e(s.conclusion)}</div>
        </div>
        <div class="exec-item">
          <div class="exec-item-label">最優先テーマ</div>
          <div class="exec-item-value">{e(s.top_theme)}</div>
        </div>
        <div class="exec-item">
          <div class="exec-item-label">重要示唆</div>
          <div class="exec-item-value">{e(s.key_insight)}</div>
        </div>
        <div class="exec-item exec-action-item">
          <div class="exec-item-label">今すぐ意思決定すべきこと</div>
          <div class="exec-item-value">{e(s.immediate_action)}</div>
        </div>
      </div>
    </div>"""

    def _html_top_issues(self) -> str:
        e = html_lib.escape
        top3 = sorted(self.issues, key=lambda x: x.priority)[:3]
        cards = ""
        for i, issue in enumerate(top3):
            rank = i + 1
            verdict_cls, verdict_label = self._verdict_class(issue.verdict)
            score_pct = int(issue.score / 9 * 100)
            actions_html = "".join(f"<li>{e(a)}</li>" for a in issue.actions[:2])
            cards += f"""
        <div class="issue-card rank-{rank}">
          <div class="issue-card-top">
            <span class="issue-rank">#{rank}</span>
            <span class="verdict-badge {verdict_cls}">{e(verdict_label)}</span>
          </div>
          <h3 class="issue-title">{e(issue.title)}</h3>
          <div class="issue-insight">{e(issue.insight)}</div>
          <div class="score-row">
            <span class="score-label">信頼スコア</span>
            <div class="score-track">
              <div class="score-fill" style="width:{score_pct}%"></div>
            </div>
            <span class="score-num">{issue.score}/9</span>
            <span class="tier-badge">Tier {e(issue.source_tier)}</span>
          </div>
          <ul class="issue-actions">{actions_html}</ul>
        </div>"""

        return f"""
    <div class="section-header-row">
      <div class="section-title">優先テーマ — Top 3</div>
      <div class="section-sub">評価スコア・インサイト・即行アクション</div>
    </div>
    <div class="issues-grid">
      {cards}
    </div>"""

    def _html_issues_table(self) -> str:
        e = html_lib.escape
        rows = ""
        for issue in sorted(self.issues, key=lambda x: x.priority):
            verdict_cls, verdict_label = self._verdict_class(issue.verdict)
            score_pct = int(issue.score / 9 * 100)
            rows += f"""
          <tr>
            <td class="td-priority">#{issue.priority}</td>
            <td class="td-title">{e(issue.title)}</td>
            <td>
              <div class="table-score-row">
                <div class="score-track sm">
                  <div class="score-fill" style="width:{score_pct}%"></div>
                </div>
                <span class="score-num">{issue.score}/9</span>
              </div>
            </td>
            <td><span class="tier-badge">Tier {e(issue.source_tier)}</span></td>
            <td><span class="verdict-badge {verdict_cls}">{e(verdict_label)}</span></td>
          </tr>"""

        return f"""
    <div class="card">
      <div class="section-label">全評価対象一覧</div>
      <table class="eval-table">
        <thead>
          <tr>
            <th>優先</th><th>テーマ</th><th>信頼スコア</th><th>ソース</th><th>判定</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

    def _html_insights(self) -> str:
        e = html_lib.escape
        items = ""
        for ins in self.insights:
            why_html = f'<div class="insight-why">{e(ins.why_now)}</div>' if ins.why_now else ""
            items += f"""
        <div class="insight-item">
          <div class="insight-title">{e(ins.title)}</div>
          <div class="insight-body">{e(ins.body)}</div>
          {why_html}
        </div>"""

        return f"""
    <div class="card">
      <div class="section-label">重要インサイト</div>
      <div class="insights-list">{items}</div>
    </div>"""

    def _html_actions(self) -> str:
        e = html_lib.escape
        a = self.actions

        def col(items, cls, label):
            lis = "".join(f"<li>{e(x)}</li>" for x in items)
            return f"""
          <div class="action-col {cls}">
            <div class="action-col-header">{label}</div>
            <ul class="action-list">{lis}</ul>
          </div>"""

        return f"""
    <div class="card">
      <div class="section-label">推奨アクション</div>
      <div class="actions-grid">
        {col(a.now,     "action-now",     "今すぐ実行")}
        {col(a.next_,   "action-next",    "次に検証")}
        {col(a.monitor, "action-monitor", "監視・保留")}
      </div>
    </div>"""

    def _html_cdo(self) -> str:
        e = html_lib.escape
        c = self.cdo

        metrics_html = ""
        for m in c.metrics:
            dir_icon = {"up": "↑", "down": "↓", "neutral": "→"}.get(m.direction, "→")
            dir_cls = {"up": "metric-up", "down": "metric-down", "neutral": "metric-neutral"}.get(m.direction, "metric-neutral")
            metrics_html += f"""
          <div class="metric-card">
            <div class="metric-name">{e(m.name)}</div>
            <div class="metric-value {dir_cls}">{dir_icon} {e(m.estimate)}</div>
            <div class="metric-reason">{e(m.reason)}</div>
          </div>"""

        strengths_html = "".join(f"<li class='strength-item'>{e(s)}</li>" for s in c.strengths)
        weaknesses_html = "".join(f"<li class='weakness-item'>{e(w)}</li>" for w in c.weaknesses)

        hypo_rows = ""
        for h in c.hypotheses:
            pri_cls = {"高": "pri-high", "中": "pri-mid", "低": "pri-low"}.get(h.priority, "pri-mid")
            hypo_rows += f"""
            <tr>
              <td>{e(h.what)}</td>
              <td>{e(h.why)}</td>
              <td>{e(h.metric_impact)}</td>
              <td><span class="priority-badge {pri_cls}">{e(h.priority)}</span></td>
            </tr>"""

        return f"""
    <div class="card cdo-card">
      <div class="section-label">CDO 数値評価 &amp; 改善仮説</div>
      <div class="cdo-intro">改善をドライブする責任者視点での評価。感覚ではなく改善仮説で議論する。</div>

      <div class="cdo-metrics-grid">{metrics_html}</div>

      <div class="sw-grid">
        <div class="sw-col">
          <div class="sw-label sw-s">強いポイント</div>
          <ul class="sw-list">{strengths_html}</ul>
        </div>
        <div class="sw-col">
          <div class="sw-label sw-w">改善余地</div>
          <ul class="sw-list">{weaknesses_html}</ul>
        </div>
      </div>

      <div class="sub-section-label">改善仮説 — 優先順</div>
      <table class="eval-table">
        <thead>
          <tr><th>改善施策</th><th>なぜ効くか</th><th>影響指標</th><th>優先度</th></tr>
        </thead>
        <tbody>{hypo_rows}</tbody>
      </table>
    </div>"""

    def _html_pdca(self) -> str:
        e = html_lib.escape
        p = self.pdca

        def items_html(items):
            return "".join(f"<li>{e(x)}</li>" for x in items)

        return f"""
    <div class="card">
      <div class="section-label">PDCA 設計</div>
      <div class="pdca-grid">
        <div class="pdca-col">
          <div class="pdca-col-label">P — 何をテストするか</div>
          <ul class="pdca-list">{items_html(p.what_to_test)}</ul>
        </div>
        <div class="pdca-col">
          <div class="pdca-col-label">D — 何を計測するか</div>
          <ul class="pdca-list">{items_html(p.what_to_measure)}</ul>
        </div>
        <div class="pdca-col pdca-ca">
          <div class="pdca-col-label">C — どう判断するか</div>
          <div class="pdca-text">{e(p.how_to_judge)}</div>
          <div class="pdca-col-label" style="margin-top:16px">A — 次の改善</div>
          <div class="pdca-text">{e(p.next_iteration)}</div>
        </div>
      </div>
      <div class="pdca-min-exp">
        <span class="pdca-min-label">最小実験単位</span>
        <span>{e(p.minimum_experiment)}</span>
      </div>
    </div>"""

    def _html_log(self) -> str:
        content_escaped = html_lib.escape("\n".join(self.lines))
        return f"""
    <div class="card">
      <details>
        <summary class="log-summary">補足・実行ログ <span class="log-lines">({len(self.lines)} 行)</span></summary>
        <pre class="log-pre">{content_escaped}</pre>
      </details>
    </div>"""

    # ─── インデックス更新 ───

    def _update_index(self) -> None:
        reports_dir = self.reports_dir
        html_files = sorted(reports_dir.glob("*.html"), reverse=True)
        html_files = [f for f in html_files if f.name != "index.html"]

        cards = ""
        for i, f in enumerate(html_files):
            name = f.stem
            parts = name.split("_", 2)
            date = parts[0] if len(parts) > 0 else ""
            time = parts[1].replace("-", ":") if len(parts) > 1 else ""
            label = parts[2] if len(parts) > 2 else ""
            is_latest = i == 0
            latest_badge = '<span class="latest-badge">最新</span>' if is_latest else ""
            cards += f"""
        <div class="report-card {'report-card-latest' if is_latest else ''}">
          <div class="report-card-meta">
            {latest_badge}
            <span class="report-date">{html_lib.escape(date)}</span>
            <span class="report-time">{html_lib.escape(time)}</span>
          </div>
          <div class="report-label">{html_lib.escape(label)}</div>
          <a class="report-link" href="{html_lib.escape(f.name)}">レポートを開く →</a>
        </div>"""

        index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Media Strategy Reports — 一覧</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Noto Sans JP", sans-serif;
      background: #F1F5F9;
      color: #0F172A;
      padding: 48px 24px 80px;
      line-height: 1.6;
    }}
    .container {{ max-width: 860px; margin: 0 auto; }}
    .page-label {{
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: #64748B; margin-bottom: 6px;
    }}
    h1 {{ font-size: 1.6rem; font-weight: 700; margin-bottom: 4px; letter-spacing: -0.02em; }}
    .page-meta {{ font-size: 0.85rem; color: #64748B; margin-bottom: 36px; }}
    .reports-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 16px;
    }}
    .report-card {{
      background: #fff;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 20px 24px;
      transition: box-shadow 0.15s;
    }}
    .report-card:hover {{ box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
    .report-card-latest {{ border-color: #1E3A5F; border-width: 2px; }}
    .report-card-meta {{
      display: flex; align-items: center; gap: 8px;
      font-size: 0.78rem; color: #64748B; margin-bottom: 10px;
    }}
    .latest-badge {{
      background: #1E3A5F; color: #fff;
      font-size: 0.65rem; font-weight: 700; letter-spacing: 0.05em;
      padding: 2px 7px; border-radius: 4px; text-transform: uppercase;
    }}
    .report-label {{ font-size: 0.95rem; font-weight: 600; margin-bottom: 14px; color: #0F172A; }}
    .report-link {{
      font-size: 0.85rem; font-weight: 600; color: #1E3A5F;
      text-decoration: none; border-bottom: 1px solid #1E3A5F;
      padding-bottom: 1px;
    }}
    .report-link:hover {{ opacity: 0.7; }}
    .footer {{
      text-align: center; font-size: 0.75rem;
      color: #94A3B8; margin-top: 48px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="page-label">Media Company OS</div>
    <h1>Strategy Reports</h1>
    <div class="page-meta">全レポート一覧 — {len(html_files)} 件</div>
    <div class="reports-grid">
      {cards}
    </div>
    <div class="footer">Media Company OS — 意思決定レポートシステム</div>
  </div>
</body>
</html>"""
        (reports_dir / "index.html").write_text(index_html, encoding="utf-8")

    # ─── ヘルパー ───

    @staticmethod
    def _verdict_class(verdict: str) -> tuple[str, str]:
        mapping = {
            "試す価値あり": ("badge-go",   "試す価値あり"),
            "まだ早い":     ("badge-wait", "まだ早い"),
            "不要":         ("badge-no",   "不要"),
        }
        return mapping.get(verdict, ("badge-no", verdict))

    # ─────────────────────────────────────────
    # CSS
    # ─────────────────────────────────────────

    def _css(self) -> str:
        return """<style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans",
                   "Noto Sans JP", "Yu Gothic", sans-serif;
      background: #F1F5F9;
      color: #0F172A;
      padding: 48px 24px 80px;
      line-height: 1.65;
      font-size: 15px;
    }
    .container { max-width: 1080px; margin: 0 auto; }

    /* ── ページヘッダー ── */
    .page-header { margin-bottom: 28px; }
    .page-label {
      font-size: 0.68rem; font-weight: 700; letter-spacing: 0.14em;
      text-transform: uppercase; color: #64748B; margin-bottom: 6px;
    }
    .page-title {
      font-size: 1.75rem; font-weight: 700;
      letter-spacing: -0.025em; margin-bottom: 6px;
    }
    .page-meta { font-size: 0.82rem; color: #94A3B8; }

    /* ── カード ── */
    .card {
      background: #ffffff;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 32px 36px;
      margin-bottom: 20px;
    }
    .section-label {
      font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
      text-transform: uppercase; color: #64748B;
      margin-bottom: 20px;
      padding-bottom: 10px;
      border-bottom: 1px solid #E2E8F0;
    }
    .section-header-row {
      display: flex; justify-content: space-between; align-items: baseline;
      margin: 28px 0 14px;
    }
    .section-title { font-size: 1rem; font-weight: 700; }
    .section-sub { font-size: 0.8rem; color: #94A3B8; }
    .sub-section-label {
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #94A3B8;
      margin: 24px 0 12px;
    }

    /* ── Executive Summary ── */
    .exec-card { background: #0F172A; color: #F8FAFC; border-color: #0F172A; }
    .exec-card .section-label { color: #94A3B8; border-color: #1E293B; }
    .exec-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }
    .exec-item {
      background: #1E293B;
      border-radius: 10px;
      padding: 18px 20px;
    }
    .exec-conclusion { grid-column: 1 / -1; background: #1E3A5F; }
    .exec-action-item { background: #1C3A2A; }
    .exec-item-label {
      font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; color: #94A3B8; margin-bottom: 8px;
    }
    .exec-item-value { font-size: 0.95rem; font-weight: 500; line-height: 1.5; }
    .exec-conclusion .exec-item-value { font-size: 1.05rem; font-weight: 600; }

    /* ── 上位3テーマ カード ── */
    .issues-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 20px;
    }
    .issue-card {
      background: #fff;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 22px 24px;
    }
    .rank-1 { border-top: 3px solid #1E3A5F; }
    .rank-2 { border-top: 3px solid #475569; }
    .rank-3 { border-top: 3px solid #94A3B8; }
    .issue-card-top {
      display: flex; justify-content: space-between;
      align-items: center; margin-bottom: 12px;
    }
    .issue-rank {
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em;
      color: #64748B;
    }
    .issue-title {
      font-size: 0.9rem; font-weight: 700;
      margin-bottom: 10px; line-height: 1.45;
    }
    .issue-insight {
      font-size: 0.8rem; color: #475569;
      margin-bottom: 14px; line-height: 1.5;
      font-style: italic;
    }
    .issue-actions {
      list-style: none; margin-top: 12px;
      display: flex; flex-direction: column; gap: 5px;
    }
    .issue-actions li {
      font-size: 0.77rem; color: #475569;
      padding-left: 12px; position: relative;
    }
    .issue-actions li::before {
      content: "→"; position: absolute; left: 0; color: #94A3B8;
    }

    /* ── スコアバー ── */
    .score-row {
      display: flex; align-items: center; gap: 8px; margin-top: 4px;
    }
    .score-label { font-size: 0.72rem; color: #94A3B8; white-space: nowrap; }
    .score-track {
      flex: 1; height: 5px; background: #E2E8F0; border-radius: 99px;
    }
    .score-track.sm { height: 4px; }
    .score-fill { height: 100%; background: #1E3A5F; border-radius: 99px; }
    .score-num { font-size: 0.75rem; font-weight: 700; color: #0F172A; white-space: nowrap; }
    .table-score-row { display: flex; align-items: center; gap: 8px; }

    /* ── バッジ ── */
    .verdict-badge {
      display: inline-block; font-size: 0.68rem; font-weight: 700;
      letter-spacing: 0.04em; padding: 3px 10px; border-radius: 99px;
      white-space: nowrap;
    }
    .badge-go   { background: #D1FAE5; color: #065F46; }
    .badge-wait { background: #FEF3C7; color: #92400E; }
    .badge-no   { background: #F1F5F9; color: #475569; }
    .tier-badge {
      display: inline-block; font-size: 0.65rem; font-weight: 700;
      background: #EFF6FF; color: #1E40AF;
      padding: 2px 8px; border-radius: 4px; white-space: nowrap;
    }
    .priority-badge {
      display: inline-block; font-size: 0.7rem; font-weight: 700;
      padding: 2px 9px; border-radius: 4px;
    }
    .pri-high { background: #FEE2E2; color: #991B1B; }
    .pri-mid  { background: #FEF3C7; color: #92400E; }
    .pri-low  { background: #F1F5F9; color: #475569; }

    /* ── 評価テーブル ── */
    .eval-table { width: 100%; border-collapse: collapse; }
    .eval-table th {
      text-align: left; font-size: 0.68rem; font-weight: 700;
      color: #94A3B8; letter-spacing: 0.08em; text-transform: uppercase;
      padding: 0 16px 10px 0; border-bottom: 1px solid #E2E8F0;
    }
    .eval-table td {
      padding: 12px 16px 12px 0;
      border-bottom: 1px solid #F1F5F9;
      font-size: 0.875rem; vertical-align: middle;
    }
    .eval-table tr:last-child td { border-bottom: none; }
    .td-priority { font-weight: 700; color: #64748B; width: 48px; }
    .td-title { font-weight: 600; }

    /* ── インサイト ── */
    .insights-list { display: flex; flex-direction: column; gap: 18px; }
    .insight-item {
      padding: 18px 20px;
      background: #F8FAFC;
      border-left: 3px solid #1E3A5F;
      border-radius: 0 8px 8px 0;
    }
    .insight-title { font-size: 0.9rem; font-weight: 700; margin-bottom: 7px; }
    .insight-body  { font-size: 0.875rem; color: #334155; line-height: 1.6; }
    .insight-why   { font-size: 0.78rem; color: #94A3B8; margin-top: 8px; }

    /* ── 推奨アクション ── */
    .actions-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .action-col { padding: 18px 20px; border-radius: 10px; }
    .action-now     { background: #EFF6FF; }
    .action-next    { background: #F0FDF4; }
    .action-monitor { background: #F8FAFC; }
    .action-col-header {
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.07em;
      text-transform: uppercase; margin-bottom: 12px;
    }
    .action-now     .action-col-header { color: #1E40AF; }
    .action-next    .action-col-header { color: #065F46; }
    .action-monitor .action-col-header { color: #475569; }
    .action-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
    .action-list li { font-size: 0.82rem; padding-left: 14px; position: relative; line-height: 1.4; }
    .action-list li::before { content: "→"; position: absolute; left: 0; color: #94A3B8; }

    /* ── CDO ── */
    .cdo-card { border-left: 3px solid #1E3A5F; }
    .cdo-intro { font-size: 0.82rem; color: #64748B; margin-bottom: 20px; }
    .cdo-metrics-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 12px; margin-bottom: 24px;
    }
    .metric-card {
      background: #F8FAFC; border: 1px solid #E2E8F0;
      border-radius: 10px; padding: 14px 16px;
    }
    .metric-name   { font-size: 0.72rem; color: #64748B; margin-bottom: 6px; font-weight: 600; }
    .metric-value  { font-size: 1.05rem; font-weight: 700; margin-bottom: 5px; }
    .metric-up     { color: #059669; }
    .metric-down   { color: #DC2626; }
    .metric-neutral{ color: #475569; }
    .metric-reason { font-size: 0.72rem; color: #94A3B8; line-height: 1.4; }
    .sw-grid       { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 8px; }
    .sw-col        { padding: 16px 18px; border-radius: 10px; }
    .sw-s          { background: #D1FAE5; color: #065F46; }
    .sw-w          { background: #FEF3C7; color: #92400E; }
    .sw-label      { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 10px; }
    .sw-list       { list-style: none; display: flex; flex-direction: column; gap: 6px; }
    .sw-list li    { font-size: 0.82rem; padding-left: 14px; position: relative; }
    .sw-list li::before { content: "·"; position: absolute; left: 0; font-weight: 700; }

    /* ── PDCA ── */
    .pdca-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .pdca-col  { padding: 18px 20px; background: #F8FAFC; border-radius: 10px; }
    .pdca-col-label {
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.07em;
      text-transform: uppercase; color: #64748B; margin-bottom: 10px;
    }
    .pdca-list { list-style: none; display: flex; flex-direction: column; gap: 6px; }
    .pdca-list li  { font-size: 0.82rem; padding-left: 14px; position: relative; }
    .pdca-list li::before { content: "→"; position: absolute; left: 0; color: #94A3B8; }
    .pdca-text { font-size: 0.85rem; color: #334155; line-height: 1.5; }
    .pdca-min-exp {
      margin-top: 16px; padding: 14px 18px;
      background: #EFF6FF; border-radius: 8px;
      font-size: 0.85rem; display: flex; gap: 12px; align-items: flex-start;
    }
    .pdca-min-label {
      font-size: 0.68rem; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; color: #1E40AF; white-space: nowrap;
      padding-top: 2px;
    }

    /* ── ログ ── */
    .log-summary {
      cursor: pointer; font-size: 0.82rem; font-weight: 600;
      color: #64748B; user-select: none;
    }
    .log-lines { font-weight: 400; color: #94A3B8; }
    .log-pre {
      font-family: "SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace;
      font-size: 0.75rem; line-height: 1.7;
      background: #F8FAFC; border-radius: 8px;
      padding: 20px; overflow-x: auto;
      white-space: pre-wrap; word-break: break-word;
      margin-top: 16px;
    }

    /* ── フッター ── */
    .footer {
      text-align: center; font-size: 0.75rem;
      color: #94A3B8; margin-top: 8px;
    }
  </style>"""
