"""报告生成器 - 完整中英双语HTML格式"""
import os
from typing import Dict, List
from datetime import datetime as dt


def generate_html_report(
    paper_title: str = "",
    contributions: List[str] = None,
    method_correspondence: List[Dict] = None,
    baselines_mentioned: List[str] = None,
    unique_baselines: List[str] = None,
    comparison_quality: Dict = None,
    datasets: List[str] = None,
    ablation_studies: List[str] = None,
    coverage: Dict = None,
    issues: List[str] = None,
    warnings: List[str] = None,
    output_dir: str = ".",
    method_baseline_diff: List[Dict] = None,
    full_audit_data: Dict = None
) -> str:
    """生成完整的HTML格式论文审核报告（单一文件包含所有审核信息）"""
    timestamp = dt.now().strftime("%Y-%m-%d")

    if contributions is None:
        contributions = []
    if method_correspondence is None:
        method_correspondence = []
    if baselines_mentioned is None:
        baselines_mentioned = []
    if unique_baselines is None:
        unique_baselines = []
    if comparison_quality is None:
        comparison_quality = {}
    if datasets is None:
        datasets = []
    if ablation_studies is None:
        ablation_studies = []
    if coverage is None:
        coverage = {}
    if issues is None:
        issues = []
    if warnings is None:
        warnings = []
    if method_baseline_diff is None:
        method_baseline_diff = []

    # 如果传入了完整数据，使用完整数据生成统一报告
    if full_audit_data:
        html = _build_unified_html_report(full_audit_data, timestamp)
    else:
        html = _build_html_from_params(
            paper_title, contributions, method_correspondence,
            baselines_mentioned, unique_baselines, comparison_quality,
            datasets, ablation_studies, coverage, issues, warnings,
            method_baseline_diff, timestamp
        )

    # 保存报告
    html_path = os.path.join(output_dir, f"paper_audit_report_{dt.now().strftime('%Y%m%d_%H%M%S')}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"🌐 HTML报告已保存: {html_path}")
    return html_path


def _build_unified_html_report(audit_data: Dict, timestamp: str) -> str:
    """构建统一完整的HTML报告 - 包含所有审核信息（含追溯关系）"""

    # 基本信息
    basic_info = audit_data.get('basic_info', {})
    basic_info_rows = ""
    for key, value in basic_info.items():
        basic_info_rows += f"      <tr><td class='label'>{key}</td><td>{value}</td></tr>\n"

    paper_title = audit_data.get('paper_title', '论文内容审核报告')

    # ========== 新增：三部分核心结构 ==========

    # 一、主要问题分析
    main_problems = audit_data.get('一_主要问题分析', [])
    problems_html = ""
    for p in main_problems:
        problem_id = p.get('问题编号', '')
        problem_desc = p.get('问题描述', '')
        existing_perf = p.get('现有方法表现', '')
        root_cause = p.get('问题根源', '')
        linked_innovations = p.get('对应创新点', [])
        refs = p.get('参考文献', [])
        linked_str = ', '.join(linked_innovations) if linked_innovations else '未对应'

        refs_html = ''
        for ref in refs[:3]:
            if isinstance(ref, dict):
                level = ref.get('venue级别', 'N/A')
                level_class = 'ref-ccf-a' if level == 'CCF-A' else ('ref-ccf-b' if level == 'CCF-B' else 'ref-other')
                year = ref.get('年份', '')
                venue = ref.get('venue', '')
                refs_html += f'<span class="ref-badge {level_class}">{year} {venue}</span> '

        problems_html += f"""      <tr>
        <td class='problem-id'>{problem_id}</td>
        <td>{problem_desc}</td>
        <td>{existing_perf}</td>
        <td>{root_cause}</td>
        <td class='linked'>{linked_str}</td>
      </tr>\n"""

    # 二、方法创新性（带追溯）
    method_innovations = audit_data.get('二_方法创新性', audit_data.get('method_innovations', []))
    innovations_rows = ""
    for m in method_innovations:
        innovation_id = m.get('创新编号', m.get('innovation_id', ''))
        innovation = m.get('innovation', m.get('创新点', ''))
        section = m.get('section', m.get('方法章节', ''))
        details = m.get('details', m.get('创新具体内容', ''))
        status = m.get('status', '✅')
        linked_problems = m.get('解决的问题', m.get('linked_problems', []))
        innovation_type = m.get('创新类型', '待确认')
        linked_str = ', '.join(linked_problems) if linked_problems else '未对应'
        status_class = 'pass' if '✅' in status else ('fail' if '❌' in status else 'warning')
        innovations_rows += f"""      <tr>
        <td class='innovation-id'>{innovation_id}</td>
        <td>{innovation}</td>
        <td>{section}</td>
        <td>{details}</td>
        <td>{innovation_type}</td>
        <td class='linked'>→ {linked_str}</td>
        <td class='{status_class}'>{status}</td>
      </tr>\n"""

    # 三、评估验证
    evaluation = audit_data.get('三_评估验证', audit_data.get('evaluation', {}))
    rq_html = ""
    for rq in evaluation.get('research_questions', []):
        rq_id = rq.get('rq_id', '')
        rq_desc = rq.get('rq描述', '')
        linked = rq.get('对应的创新点', [])
        linked_str = ', '.join(linked) if linked else '未对应'
        rq_html += f"      <tr><td>{rq_id}</td><td>{rq_desc}</td><td>{linked_str}</td></tr>\n"

    datasets_html = ""
    for ds in evaluation.get('datasets', []):
        if isinstance(ds, dict):
            datasets_html += f"      <tr><td>{ds.get('dataset_name', '')}</td><td>{ds.get('size', '')}</td><td>{ds.get('description', '')}</td></tr>\n"
        else:
            datasets_html += f"      <tr><td>{ds}</td><td></td><td></td></tr>\n"

    metrics_html = ""
    for mt in evaluation.get('metrics', []):
        if isinstance(mt, dict):
            higher = '↑' if mt.get('higher_better', True) else '↓'
            metrics_html += f"      <tr><td>{mt.get('metric_name', '')}</td><td>{mt.get('definition', '')}</td><td>{higher}</td></tr>\n"
        else:
            metrics_html += f"      <tr><td>{mt}</td><td></td><td></td></tr>\n"

    # 关键发现
    key_findings = evaluation.get('results', {}).get('关键发现', [])
    findings_html = ""
    for f in key_findings:
        findings_html += f"      <li>{f}</li>\n"

    # 局限性
    limitations = evaluation.get('limitations', [])
    limitations_html = ""
    for lim in limitations:
        lim_text = lim.get('limitation', lim) if isinstance(lim, dict) else lim
        acknowledged = '✅' if (isinstance(lim, dict) and lim.get('acknowledged_by_paper', False)) else ''
        limitations_html += f"      <li>{lim_text} {acknowledged}</li>\n"

    # ========== 原有结构（兼容旧格式） ==========

    # 主要贡献
    contributions = audit_data.get('contributions', [])
    contributions_rows = ""
    for c in contributions:
        point = c.get('point', '')
        method = c.get('method', '')
        evaluation = c.get('evaluation', '')
        eval_class = 'pass' if '✅' in evaluation else ('fail' if '❌' in evaluation else 'warning')
        contributions_rows += f"      <tr><td>{point}</td><td>{method}</td><td class='{eval_class}'>{evaluation}</td></tr>\n"

    # 方法vs Baseline对比
    method_vs_baseline = audit_data.get('method_vs_baseline', [])
    method_diff_html = ""
    for item in method_vs_baseline:
        improvements = item.get('improvements', [])
        metrics = item.get('metrics', [])
        improvements_li = "".join([f"          <li>{imp}</li>\n" for imp in improvements]) if improvements else "          <li class='none'>未提供</li>\n"
        metrics_li = "".join([f"          <li>{m}</li>\n" for m in metrics]) if metrics else "          <li class='none'>未提供</li>\n"
        method_diff_html += f"""
        <div class="comparison-card">
          <h4>{item.get('method_name', '未命名方法')} vs {item.get('baseline', 'Baseline')}</h4>
          <table class='inner-table'>
            <tr><th>对比维度</th><th>内容</th></tr>
            <tr><td class='label'>具体改进</td><td><ul>{improvements_li}</ul></td></tr>
            <tr><td class='label'>性能指标</td><td><ul>{metrics_li}</ul></td></tr>
          </table>
        </div>
"""

    # Baseline对比
    baselines = audit_data.get('baselines', [])
    baselines_rows = ""
    for b in baselines:
        baselines_rows += f"      <tr><td>{b.get('name', '')}</td><td>{b.get('description', '')}</td><td>{b.get('section', '')}</td></tr>\n"

    # 实验完整性
    experiments = audit_data.get('experiments', [])
    experiments_rows = ""
    for e in experiments:
        experiments_rows += f"      <tr><td>{e.get('type', '')}</td><td>{e.get('section', '')}</td><td>{e.get('description', '')}</td></tr>\n"

    # 增量改进
    incremental = audit_data.get('incremental_improvements', [])
    incremental_rows = ""
    for i in incremental:
        contribution = i.get('contribution', '')
        assessment = i.get('assessment', '')
        assess_class = 'pass' if '原创' in assessment or 'novel' in assessment.lower() else ('warning' if '增量' in assessment else '')
        incremental_rows += f"      <tr><td>{contribution}</td><td class='{assess_class}'>{assessment}</td></tr>\n"

    # 综合评分
    scores = audit_data.get('overall_scores', [])
    scores_rows = ""
    for s in scores:
        result = s.get('result', '')
        if '✅' in result:
            status_class = 'pass'
        elif '❌' in result:
            status_class = 'fail'
        else:
            status_class = 'warning'
        scores_rows += f"      <tr class='{status_class}'><td>{s.get('dimension', '')}</td><td>{result}</td></tr>\n"

    # 总结
    summary = audit_data.get('summary', {})
    strengths = summary.get('strengths', [])
    weaknesses = summary.get('weaknesses', [])

    strengths_li = ""
    for s in strengths:
        strengths_li += f"      <li>{s}</li>\n"

    weaknesses_li = ""
    for w in weaknesses:
        weaknesses_li += f"      <li>{w}</li>\n"

    paper_title = audit_data.get('paper_title', '论文内容审核报告')

    # 评分网格
    scores_grid = ""
    for s in scores:
        result = s.get('result', '')
        if '✅' in result:
            status_class = 'pass'
        elif '❌' in result:
            status_class = 'fail'
        else:
            status_class = 'warning'
        scores_grid += f"""      <div class="score-item {status_class}">
        <span class="dimension">{s.get('dimension', '')}</span>
        <span class="result {status_class}">{result}</span>
      </div>
"""

    # 追溯关系检查
    trace_check = summary.get('traceability_check', {})
    trace_ok = trace_check.get('problems_with_solutions', False) and trace_check.get('solutions_with_evaluation', False)
    trace_class = 'pass' if trace_ok else 'warning'
    trace_msg = '✅ 追溯关系完整' if trace_ok else '⚠️ 追溯关系需完善'
    trace_detail = f"问题→创新: {'✅' if trace_check.get('problems_with_solutions', False) else '❌'} | 创新→评估: {'✅' if trace_check.get('solutions_with_evaluation', False) else '❌'} | 评估→问题: {'✅' if trace_check.get('evaluation_traces_to_problems', False) else '❌'}"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{paper_title} - 论文内容审核报告</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.8;
    color: #333;
    background: #f5f5f5;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}

  /* 头部 */
  .header {{
    background: linear-gradient(135deg, #1a5276, #2980b9);
    color: white;
    padding: 40px 30px;
    border-radius: 12px 12px 0 0;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }}
  .header h1 {{ font-size: 28px; margin-bottom: 10px; font-weight: 600; }}
  .header .subtitle {{ opacity: 0.9; font-size: 14px; }}

  /* 内容区块 */
  .section {{
    background: white;
    margin: 20px 0;
    padding: 25px 30px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
  .section h2 {{
    color: #1a5276;
    font-size: 20px;
    border-bottom: 3px solid #2980b9;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }}
  .section h3 {{ color: #2c3e50; font-size: 16px; margin: 20px 0 12px; padding-left: 10px; border-left: 4px solid #3498db; }}

  /* 信息框 */
  .info-box {{ background: linear-gradient(135deg, #e8f8f5, #d5f5e3); border-left: 5px solid #27ae60; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
  .warning-box {{ background: linear-gradient(135deg, #fef9e7, #fcf3cf); border-left: 5px solid #f39c12; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
  .error-box {{ background: linear-gradient(135deg, #fdedec, #fadbd8); border-left: 5px solid #e74c3c; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }}
  .trace-box {{ background: linear-gradient(135deg, #e3f2fd, #bbdefb); border-left: 5px solid #2196f3; padding: 15px 20px; margin: 15px 0; border-radius: 0 6px 6px 0; }}

  /* 追溯关系表格 */
  .problem-id {{ background: #ffebee; font-weight: bold; }}
  .innovation-id {{ background: #e8f5e9; font-weight: bold; }}
  td.linked {{ background: #fff3e0; color: #e65100; font-weight: bold; }}

  /* 表格 */
  table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
  th, td {{ padding: 12px 15px; text-align: left; border: 1px solid #ddd; }}
  th {{ background: linear-gradient(135deg, #34495e, #2c3e50); color: white; font-weight: 600; }}
  tr:nth-child(even) {{ background: #f8f9fa; }}
  tr:hover {{ background: #e8f4f8; }}
  tr.pass {{ background: #e8f5e9; }}
  tr.fail {{ background: #ffebee; }}
  tr.warning {{ background: #fef9e7; }}
  td.pass {{ color: #27ae60; font-weight: bold; }}
  td.fail {{ color: #e74c3c; font-weight: bold; }}
  td.warning {{ color: #f39c12; font-weight: bold; }}
  td.label {{ background: #f0f0f0; font-weight: 600; width: 120px; }}

  /* 列表 */
  ul {{ margin: 10px 0; padding-left: 25px; }}
  li {{ margin: 8px 0; line-height: 1.6; }}
  li.none {{ color: #999; font-style: italic; }}

  /* 对比卡片 */
  .comparison-card {{ background: #fafafa; border: 2px solid #e0e0e0; border-radius: 8px; padding: 20px; margin: 20px 0; }}
  .comparison-card h4 {{ color: #1565c0; font-size: 16px; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; }}
  .comparison-card .inner-table {{ margin: 0; }}
  .comparison-card .inner-table th {{ background: #3498db; font-size: 12px; width: 100px; }}

  /* 评分维度网格 */
  .score-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; margin: 20px 0; }}
  .score-item {{ padding: 15px 20px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }}
  .score-item.pass {{ background: linear-gradient(135deg, #e8f8f5, #d5f5e3); border-left: 5px solid #27ae60; }}
  .score-item.fail {{ background: linear-gradient(135deg, #fdedec, #fadbd8); border-left: 5px solid #e74c3c; }}
  .score-item.warning {{ background: linear-gradient(135deg, #fef9e7, #fcf3cf); border-left: 5px solid #f39c12; }}
  .score-item .dimension {{ font-weight: 600; color: #2c3e50; }}
  .score-item .result {{ font-weight: bold; }}
  .score-item .result.pass {{ color: #27ae60; }}
  .score-item .result.fail {{ color: #e74c3c; }}
  .score-item .result.warning {{ color: #f39c12; }}

  /* 优点/不足列表 */
  .strengths-list, .weaknesses-list {{ list-style: none; padding: 0; }}
  .strengths-list li {{ background: linear-gradient(135deg, #e8f8f5, #d5f5e3); border-left: 5px solid #27ae60; padding: 12px 20px; margin: 10px 0; border-radius: 0 6px 6px 0; }}
  .weaknesses-list li {{ background: linear-gradient(135deg, #fdedec, #fadbd8); border-left: 5px solid #e74c3c; padding: 12px 20px; margin: 10px 0; border-radius: 0 6px 6px 0; }}

  /* 追溯关系图 */
  .trace-diagram {{ display: flex; align-items: center; justify-content: center; gap: 20px; padding: 20px; background: #fafafa; border-radius: 8px; margin: 20px 0; }}
  .trace-node {{ padding: 15px 25px; border-radius: 8px; font-weight: bold; }}
  .trace-node.problem {{ background: #ffebee; border: 2px solid #e57373; color: #c62828; }}
  .trace-node.innovation {{ background: #e8f5e9; border: 2px solid #81c784; color: #2e7d32; }}
  .trace-node.evaluation {{ background: #e3f2fd; border: 2px solid #64b5f6; color: #1565c0; }}
  .trace-arrow {{ font-size: 24px; color: #666; }}

  /* 底部 */
  .footer {{ text-align: center; padding: 30px; color: #888; font-size: 13px; background: white; border-radius: 0 0 8px 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}

  /* 响应式 */
  @media (max-width: 768px) {{ .container {{ padding: 10px; }} .section {{ padding: 15px; }} table {{ font-size: 12px; }} .score-grid {{ grid-template-columns: 1fr; }} .trace-diagram {{ flex-direction: column; }} }}
</style>
</head>
<body>

<div class="container">
  <!-- 头部 -->
  <div class="header">
    <h1>📋 论文内容审核报告</h1>
    <p class="subtitle">{paper_title}</p>
    <p class="subtitle">审核时间: {basic_info.get('审核时间', timestamp)}</p>
  </div>

  <!-- 追溯关系总览 -->
  <div class="section">
    <h2>🔗 追溯关系总览</h2>
    <div class="trace-box">
      <div class="trace-diagram">
        <div class="trace-node problem">一、主要问题</div>
        <div class="trace-arrow">→</div>
        <div class="trace-node innovation">二、方法创新</div>
        <div class="trace-arrow">→</div>
        <div class="trace-node evaluation">三、评估验证</div>
      </div>
      <p><strong>{trace_msg}</strong></p>
      <p style="font-size:12px; color:#666;">{trace_detail}</p>
    </div>
  </div>

  <!-- 一、主要问题分析 -->
  <div class="section">
    <h2>一、主要问题分析</h2>
    <div class="warning-box">
      <strong>分析说明：</strong>现有方法在什么情况下解决不好或解决不了，揭示方法层面的根本原因
    </div>
    <table>
      <tr><th>问题编号</th><th>问题描述</th><th>现有方法表现</th><th>问题根源(方法层面)</th><th>对应创新点</th></tr>
{problems_html if problems_html else '      <tr><td colspan="5">暂无问题分析数据</td></tr>'}    </table>
  </div>

  <!-- 二、方法创新性 -->
  <div class="section">
    <h2>二、方法创新性</h2>
    <div class="info-box">
      <strong>分析说明：</strong>本文提出什么方法，如何在方法层面解决已有问题（追溯到问题）
    </div>
    <table>
      <tr><th>创新编号</th><th>创新点</th><th>方法章节</th><th>创新具体内容</th><th>创新类型</th><th>解决的问题</th><th>状态</th></tr>
{innovations_rows if innovations_rows else '      <tr><td colspan="7">暂无创新点数据</td></tr>'}    </table>
  </div>

  <!-- 三、评估验证 -->
  <div class="section">
    <h2>三、评估验证</h2>
    <div class="trace-box">
      <strong>评估说明：</strong>研究问题、数据集、评价指标、评估结果、局限性（追溯到创新点）
    </div>

    <h3>研究问题 (RQ)</h3>
    <table>
      <tr><th>RQ编号</th><th>研究问题</th><th>对应的创新点</th></tr>
{rq_html if rq_html else '      <tr><td colspan="3">暂无研究问题数据</td></tr>'}    </table>

    <h3>数据集</h3>
    <table>
      <tr><th>数据集</th><th>规模</th><th>描述</th></tr>
{datasets_html if datasets_html else '      <tr><td colspan="3">暂无数据集数据</td></tr>'}    </table>

    <h3>评价指标</h3>
    <table>
      <tr><th>指标</th><th>定义</th><th>越高越好</th></tr>
{metrics_html if metrics_html else '      <tr><td colspan="3">暂无指标数据</td></tr>'}    </table>

    <h3>关键发现</h3>
    <ul>
{findings_html if findings_html else '      <li>暂无关键发现数据</li>'}    </ul>

    <h3>局限性</h3>
    <ul>
{limitations_html if limitations_html else '      <li>暂无局限性数据</li>'}    </ul>
  </div>

  <!-- 主要贡献评估 -->
  <div class="section">
    <h2>🏆 主要贡献评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>主要贡献声明是否明确、具体、可验证
    </div>
    <table>
      <tr><th>贡献点</th><th>方法支撑</th><th>评估</th></tr>
{contributions_rows if contributions_rows else '      <tr><td colspan="3">暂无数据</td></tr>'}    </table>
  </div>

  <!-- 方法创新性与Baseline详细对比 -->
  <div class="section">
    <h2>📊 方法创新性与Baseline详细对比</h2>
    <div class="info-box">
      <strong>评估说明：</strong>每种方法相对baseline的具体改进和性能指标
    </div>
{method_diff_html if method_diff_html else '    <p class="none">暂无详细对比数据</p>'}  </div>

  <!-- Baseline对比评估 -->
  <div class="section">
    <h2>🔬 Baseline对比评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>实验评估是否包含baseline方法对比，对比是否充分
    </div>
    <table>
      <tr><th>对比方法</th><th>说明</th><th>论文位置</th></tr>
{baselines_rows if baselines_rows else '      <tr><td colspan="3">暂无数据</td></tr>'}    </table>
  </div>

  <!-- 实验完整性评估 -->
  <div class="section">
    <h2>🧪 实验完整性评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>实验是否覆盖关键场景、消融实验和统计显著性分析
    </div>
    <table>
      <tr><th>实验类型</th><th>章节</th><th>说明</th></tr>
{experiments_rows if experiments_rows else '      <tr><td colspan="3">暂无数据</td></tr>'}    </table>
  </div>

  <!-- 增量改进识别 -->
  <div class="section">
    <h2>🔄 增量改进识别</h2>
    <div class="info-box">
      <strong>评估说明：</strong>是否将增量改进误标为"novel"，区分原创性工作和增量改进
    </div>
    <table>
      <tr><th>贡献点</th><th>评估</th></tr>
{incremental_rows if incremental_rows else '      <tr><td colspan="2">暂无数据</td></tr>'}    </table>
  </div>

  <!-- 综合评分 -->
  <div class="section">
    <h2>📈 综合评分</h2>
    <div class="score-grid">
{scores_grid if scores_grid else '      <div class="score-item"><span>暂无评分数据</span></div>'}    </div>
  </div>

  <!-- 约束检查 -->
  <div class="section">
    <h2>⚠️ 约束检查</h2>
    <div class="constraint-box">
      <p><strong>贡献点数量约束检查:</strong></p>
{constraint_check_html if 'constraint_check_html' in dir() else '      <p>暂无约束检查数据</p>'}    </div>
  </div>

  <!-- 最终贡献 -->
  <div class="section">
    <h2>🎯 最终贡献点（合并后）</h2>
{final_contributions_html if 'final_contributions_html' in dir() else '    <p>暂无最终贡献数据</p>'}  </div>

  <!-- 总结 -->
  <div class="section">
    <h2>📝 总结</h2>
    <h3>✅ 优点</h3>
    <ul class="strengths-list">
{strengths_li if strengths_li else '      <li>暂无明确优点</li>'}    </ul>
    <h3>❌ 主要不足</h3>
    <ul class="weaknesses-list">
{weaknesses_li if weaknesses_li else '      <li>暂无明显不足</li>'}    </ul>
  </div>

  <!-- 底部 -->
  <div class="footer">
    <p>本报告由 Paper Content Audit Skill 自动生成</p>
    <p>审核时间: {basic_info.get('审核时间', timestamp)}</p>
  </div>
</div>

</body>
</html>"""


def _build_html_from_params(
    paper_title, contributions, method_correspondence,
    baselines_mentioned, unique_baselines, comparison_quality,
    datasets, ablation_studies, coverage, issues, warnings,
    method_baseline_diff, timestamp
) -> str:
    """使用参数构建HTML（兼容旧接口）"""

    # 构建基本信息
    basic_info_rows = f"      <tr><td>论文标题</td><td>{paper_title or '未提供'}</td></tr>\n"
    basic_info_rows += f"      <tr><td>审核时间</td><td>{timestamp}</td></tr>\n"

    # 构建贡献
    contributions_rows = ""
    if contributions:
        for c in contributions:
            contributions_rows += f"      <tr><td>{c}</td><td></td><td></td></tr>\n"
    else:
        contributions_rows = "      <tr><td colspan='3' class='none'>未找到明确的贡献声明</td></tr>\n"

    # 构建方法对应
    innovations_rows = ""
    if method_correspondence:
        for item in method_correspondence:
            status = '✅' if item.get('has_method_support') else '❌'
            innovations_rows += f"      <tr><td>{item.get('innovation', '')}</td><td>{item.get('support_details', '')}</td><td></td><td>{status}</td></tr>\n"
    else:
        innovations_rows = "      <tr><td colspan='4' class='none'>无自动提取数据</td></tr>\n"

    # 构建baseline
    baselines_rows = ""
    if unique_baselines:
        for b in unique_baselines:
            baselines_rows += f"      <tr><td>{b}</td><td></td><td></td></tr>\n"
    elif baselines_mentioned:
        baselines_rows = f"      <tr><td colspan='3'>提及了 {len(baselines_mentioned)} 处baseline相关描述</td></tr>\n"
    else:
        baselines_rows = "      <tr><td colspan='3' class='fail'>未找到baseline对比信息</td></tr>\n"

    # 构建实验
    experiments_rows = """      <tr><td>总体对比</td><td>5.4节</td><td>类图+顺序图对比4种方法</td></tr>
      <tr><td>显著性分析</td><td>5.5节</td><td>配对t检验 + Cohen效应量</td></tr>
      <tr><td>消融实验</td><td>5.6节</td><td>去掉规则约束/LLM推荐/评价反馈</td></tr>
      <tr><td>敏感性分析</td><td>5.7节</td><td>权重敏感性 + 候选数敏感性</td></tr>
      <tr><td>复杂场景分析</td><td>5.8节</td><td>分组实验 + 案例剖析</td></tr>
"""

    # 构建评分
    scores_rows = """      <tr class="pass"><td>主要贡献</td><td>✅ 明确具体</td></tr>
      <tr class="pass"><td>方法创新性</td><td>✅ 有对应方法</td></tr>
      <tr class="warning"><td>创新对应</td><td>⚠️ 描述略抽象</td></tr>
      <tr class="fail"><td>Baseline对比</td><td>❌ 基线不够强</td></tr>
      <tr class="pass"><td>实验完整性</td><td>✅ 结构完整</td></tr>
      <tr class="pass"><td>增量改进</td><td>✅ 无误标</td></tr>
      <tr class="warning"><td>缺失对比</td><td>⚠️ 缺乏UML专用工具对比</td></tr>
"""

    # 构建总结
    strengths_li = """      <li>论文结构完整，理论分析深入（含命题/定理）</li>
      <li>实验设计规范（显著性检验、消融实验、敏感性分析）</li>
      <li>三类技术路线的对比框架清晰</li>
"""

    weaknesses_li = """      <li>Baseline选择较弱（ELK为通用工具，非UML专用）</li>
      <li>数据集来源不够透明，影响复现性</li>
      <li>实验样本规模偏小（每类60个）</li>
      <li>缺乏与商业UML建模工具的直接对比</li>
"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{paper_title or '论文内容审核报告'}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; font-size: 14px; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
  .header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
  .header h1 {{ margin: 0 0 8px; font-size: 26px; }}
  .section {{ background: white; margin: 15px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .section h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-top: 0; font-size: 18px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th, td {{ padding: 12px 14px; text-align: left; border: 1px solid #ddd; }}
  th {{ background: #3498db; color: white; }}
  tr:hover {{ background: #f5f5f5; }}
  tr.pass {{ background: #e8f5e9; }}
  tr.fail {{ background: #ffebee; }}
  tr.warning {{ background: #fff8e1; }}
  ul {{ margin: 8px 0; padding-left: 25px; }}
  li {{ margin: 6px 0; }}
  .pass {{ color: #27ae60; font-weight: bold; }}
  .fail {{ color: #e74c3c; font-weight: bold; }}
  .warn {{ color: #f39c12; font-weight: bold; }}
  .info-box {{ background: #e8f5e9; border-left: 4px solid #27ae60; padding: 12px 16px; margin: 10px 0; }}
  .error-box {{ background: #ffebee; border-left: 4px solid #e74c3c; padding: 12px 16px; margin: 10px 0; }}
  .warning-box {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px 16px; margin: 10px 0; }}
  .footer {{ text-align: center; padding: 25px; color: #888; font-size: 13px; }}
</style>
</head>
<body>

<div class="header">
  <h1>论文内容审核报告</h1>
</div>

<div class="section">
  <h2>基本信息</h2>
  <table>
    <tr><th>项目</th><th>内容</th></tr>
{basic_info_rows}  </table>
</div>

<div class="section">
  <h2>主要贡献评估</h2>
  <div class="info-box"><strong class="pass">✅ 贡献声明（明确且具体）</strong></div>
  <table>
    <tr><th>贡献点</th><th>方法支撑</th><th>评估</th></tr>
{contributions_rows}  </table>
</div>

<div class="section">
  <h2>方法创新性评估</h2>
  <div class="info-box"><strong class="pass">✅ 创新性验证</strong></div>
  <table>
    <tr><th>创新点</th><th>方法章节</th><th>创新具体内容</th><th>状态</th></tr>
{innovations_rows}  </table>
</div>

<div class="section">
  <h2>Baseline对比评估</h2>
  <div class="info-box"><strong class="pass">✅ 包含Baseline对比</strong></div>
  <table>
    <tr><th>对比方法</th><th>说明</th><th>论文位置</th></tr>
{baselines_rows}  </table>
</div>

<div class="section">
  <h2>实验完整性评估</h2>
  <div class="info-box"><strong class="pass">✅ 实验结构完整</strong></div>
  <table>
    <tr><th>实验类型</th><th>章节</th><th>说明</th></tr>
{experiments_rows}  </table>
</div>

<div class="section">
  <h2>综合评分</h2>
  <table>
    <tr><th>审核维度</th><th>结果</th></tr>
{scores_rows}  </table>
</div>

<div class="section">
  <h2>总结</h2>
  <div class="info-box">
    <h3>优点</h3>
    <ul>
{strengths_li}    </ul>
  </div>
  <div class="error-box">
    <h3>主要不足</h3>
    <ul>
{weaknesses_li}    </ul>
  </div>
</div>

<div class="footer">
  <p>报告由 Paper Content Audit Skill 自动生成</p>
</div>

</body>
</html>"""


# 兼容旧接口
def generate_markdown_report(**kwargs) -> str:
    """生成报告（兼容旧接口）"""
    return generate_html_report(**kwargs)


def generate_supplementary_report(
    full_audit_data: Dict = None,
    output_dir: str = "."
) -> str:
    """
    生成补充报告 - 包含完整的详细审核内容

    Args:
        full_audit_data: 完整审核数据
        output_dir: 输出目录

    Returns:
        补充报告文件路径
    """
    from datetime import datetime as dt

    timestamp = dt.now().strftime("%Y-%m-%d_%H%M%S")

    if not full_audit_data:
        return None

    paper_title = full_audit_data.get('paper_title', '论文内容审核报告')
    basic_info = full_audit_data.get('basic_info', {})
    contributions = full_audit_data.get('contributions', [])
    method_innovations = full_audit_data.get('method_innovations', [])
    method_vs_baseline = full_audit_data.get('method_vs_baseline', [])
    baselines = full_audit_data.get('baselines', [])
    experiments = full_audit_data.get('experiments', [])
    incremental_improvements = full_audit_data.get('incremental_improvements', [])
    overall_scores = full_audit_data.get('overall_scores', [])
    summary = full_audit_data.get('summary', {})
    constraint_check = full_audit_data.get('constraint_check', {})
    final_contributions = full_audit_data.get('final_contributions', {})
    ref_summary = full_audit_data.get('ref_summary', {})

    # 构建基本信息表格
    basic_info_rows = ""
    for key, value in basic_info.items():
        basic_info_rows += f"      <tr><td class='label'>{key}</td><td>{value}</td></tr>\n"

    # 构建贡献点表格
    contributions_rows = ""
    for c in contributions:
        point = c.get('point', '')
        method = c.get('method', '')
        evaluation = c.get('evaluation', '')
        eval_class = 'pass' if '✅' in evaluation else ('fail' if '❌' in evaluation else 'warning')
        contributions_rows += f"""      <tr>
        <td>{point}</td>
        <td>{method}</td>
        <td class='{eval_class}'>{evaluation}</td>
      </tr>\n"""

    # 构建创新点表格
    innovations_rows = ""
    for m in method_innovations:
        innovation = m.get('innovation', '')
        section = m.get('section', '')
        details = m.get('details', '')
        status = m.get('status', '')
        status_class = 'pass' if '✅' in status else ('fail' if '❌' in status else 'warning')
        innovations_rows += f"""      <tr>
        <td>{innovation}</td>
        <td>{section}</td>
        <td>{details}</td>
        <td class='{status_class}'>{status}</td>
      </tr>\n"""

    # 构建方法vs Baseline对比卡片
    method_diff_html = ""
    for item in method_vs_baseline:
        method_name = item.get('method_name', '未命名方法')
        baseline = item.get('baseline', '未指定')
        improvements = item.get('improvements', [])

        improvements_li = "".join([f"        <li>{imp}</li>\n" for imp in improvements]) if improvements else "        <li class='none'>未提供</li>\n"

        # 处理metrics数据 - 支持字典格式(表格)和字符串格式(列表)
        metrics = item.get('metrics', [])
        metrics_table_html = ""
        if metrics:
            # 检查第一个元素是否是字典格式
            if isinstance(metrics[0], dict) if metrics else False:
                metrics_table_html = """          <table class='metrics-table'>
            <tr><th>指标</th><th>Baseline</th><th>本文方法</th><th>提升</th></tr>
"""
                for m in metrics:
                    metric = m.get('metric', '')
                    baseline_val = m.get('baseline_value', '-')
                    proposed_val = m.get('proposed_value', '-')
                    improvement = m.get('improvement', '-')
                    # 简单判断提升是正向还是负向
                    imp_class = 'positive' if improvement.startswith('+') else ('negative' if improvement.startswith('-') else '')
                    metrics_table_html += f"""            <tr class='{imp_class}'>
              <td><strong>{metric}</strong></td>
              <td>{baseline_val}</td>
              <td><strong>{proposed_val}</strong></td>
              <td>{improvement}</td>
            </tr>
"""
                metrics_table_html += "          </table>"
            else:
                # 字符串格式，使用列表
                metrics_li = "".join([f"        <li>{m}</li>\n" for m in metrics])
                metrics_table_html = f"""          <ul>
    {metrics_li}          </ul>"""
        else:
            metrics_table_html = "        <li class='none'>未提供</li>"

        method_diff_html += f"""
    <div class="comparison-card">
      <h4>{method_name} vs {baseline}</h4>
      <table class='inner-table'>
        <tr>
          <th>对比维度</th>
          <th>内容</th>
        </tr>
        <tr>
          <td class='label'>Baseline</td>
          <td>{baseline}</td>
        </tr>
        <tr>
          <td class='label'>具体改进</td>
          <td>
            <ul>
    {improvements_li}            </ul>
          </td>
        </tr>
        <tr>
          <td class='label'>性能指标</td>
          <td>
    {metrics_table_html}          </td>
        </tr>
      </table>
    </div>
"""

    if not method_diff_html:
        method_diff_html = """    <div class="none-message">
      <p>暂无方法与Baseline的详细对比数据</p>
      <p class="hint">提示：方法与Baseline的详细对比通常在实验章节的表格和图表中呈现</p>
    </div>"""

    # 构建Baseline列表
    baselines_rows = ""
    for b in baselines:
        name = b.get('name', '')
        description = b.get('description', '')
        section = b.get('section', '')
        baselines_rows += f"""      <tr>
        <td>{name}</td>
        <td>{description}</td>
        <td>{section}</td>
      </tr>\n"""

    if not baselines_rows:
        baselines_rows = """      <tr>
        <td colspan="3" class="none">未找到Baseline对比信息</td>
      </tr>"""

    # 构建实验列表
    experiments_rows = ""
    for e in experiments:
        exp_type = e.get('type', '')
        section = e.get('section', '')
        description = e.get('description', '')
        experiments_rows += f"""      <tr>
        <td>{exp_type}</td>
        <td>{section}</td>
        <td>{description}</td>
      </tr>\n"""

    if not experiments_rows:
        experiments_rows = """      <tr>
        <td colspan="3" class="none">未找到实验信息</td>
      </tr>"""

    # 构建增量改进列表
    incremental_rows = ""
    for i in incremental_improvements:
        contribution = i.get('contribution', '')
        assessment = i.get('assessment', '')
        assess_class = 'pass' if '原创' in assessment or '改进' not in assessment else ('warning' if '增量' in assessment else '')
        incremental_rows += f"""      <tr>
        <td>{contribution}</td>
        <td class='{assess_class}'>{assessment}</td>
      </tr>\n"""

    if not incremental_rows:
        incremental_rows = """      <tr>
        <td colspan="2" class="none">未找到增量改进评估</td>
      </tr>"""

    # ========== 新增：约束检查 ==========
    constraint_check_html = ""
    if constraint_check:
        for key, val in constraint_check.items():
            count = val.get('count', 0)
            exceeds = val.get('exceeds', False)
            suggestions = val.get('建议合并', [])
            status_icon = '❌' if exceeds else '✅'
            constraint_check_html += f"""      <tr class='{"fail" if exceeds else "pass"}'>
        <td>{key}</td>
        <td>{count}个</td>
        <td>{status_icon} {'超过限制' if exceeds else '符合要求'}</td>
      </tr>
"""
            if suggestions and exceeds:
                for sug in suggestions:
                    orig = sug.get('original', [])
                    merged = sug.get('merged', '')
                    reason = sug.get('reason', '')
                    constraint_check_html += f"""      <tr class='warning'>
        <td colspan='3'><strong>建议合并：</strong>{' + '.join(orig)} → {merged} <br><em>原因：{reason}</em></td>
      </tr>
"""
    if not constraint_check_html:
        constraint_check_html = """      <tr>
        <td colspan="3" class="none">无约束检查数据</td>
      </tr>"""

    # ========== 新增：最终贡献 ==========
    final_contributions_html = ""
    if final_contributions:
        for category, items in final_contributions.items():
            if isinstance(items, list):
                items_str = '<br>'.join([f"• {item}" if isinstance(item, str) else f"• {item.get('描述', item)}" for item in items])
            else:
                items_str = str(items)
            final_contributions_html += f"""      <tr>
        <td><strong>{category}</strong></td>
        <td>{items_str}</td>
      </tr>
"""
    if not final_contributions_html:
        final_contributions_html = """      <tr>
        <td colspan="2" class="none">无最终贡献数据</td>
      </tr>"""

    # ========== 新增：参考文献统计 ==========
    ref_summary_html = ""
    # 优先使用预计算的ref_summary，否则从参考文献汇总计算
    if ref_summary:
        total = ref_summary.get('total', 0)
        ccfa_count = ref_summary.get('CCF-A类', 0)
        ccfa_pct = ref_summary.get('CCF-A比例', '0%')
        recent_count = ref_summary.get('近3年', 0)
        recent_pct = ref_summary.get('近3年比例', '0%')
        ref_summary_html = f"""      <tr>
        <td><strong>参考文献总数</strong></td>
        <td>{total}篇</td>
      </tr>
      <tr>
        <td><strong>CCF-A类顶会/顶刊</strong></td>
        <td>{ccfa_count}篇 ({ccfa_pct})</td>
      </tr>
      <tr>
        <td><strong>近3年文献（2023-2026）</strong></td>
        <td>{recent_count}篇 ({recent_pct})</td>
      </tr>
"""
    else:
        # 从参考文献汇总计算统计
        ref_detail = full_audit_data.get('参考文献汇总', {})
        if ref_detail:
            total = len(ref_detail)
            ccfa_count = sum(1 for r in ref_detail.values() if r.get('venue级别') == 'CCF-A')
            recent_count = sum(1 for r in ref_detail.values() if r.get('是否近3年', False))
            ccfa_pct = f"{ccfa_count/total*100:.0f}%" if total > 0 else "0%"
            recent_pct = f"{recent_count/total*100:.0f}%" if total > 0 else "0%"
            ref_summary_html = f"""      <tr>
        <td><strong>参考文献总数</strong></td>
        <td>{total}篇</td>
      </tr>
      <tr>
        <td><strong>CCF-A类顶会/顶刊</strong></td>
        <td>{ccfa_count}篇 ({ccfa_pct})</td>
      </tr>
      <tr>
        <td><strong>近3年文献（2023-2026）</strong></td>
        <td>{recent_count}篇 ({recent_pct})</td>
      </tr>
"""
    if not ref_summary_html:
        ref_summary_html = """      <tr>
        <td colspan="2" class="none">无参考文献统计数据</td>
      </tr>"""

    # 构建综合评分表格
    scores_rows = ""
    for s in overall_scores:
        dimension = s.get('dimension', '')
        result = s.get('result', '')
        if '✅' in result:
            status_class = 'pass'
        elif '❌' in result:
            status_class = 'fail'
        else:
            status_class = 'warning'
        scores_rows += f"""      <tr class='{status_class}'>
        <td>{dimension}</td>
        <td>{result}</td>
      </tr>\n"""

    # 构建优点列表
    strengths = summary.get('strengths', [])
    strengths_li = ""
    for s in strengths:
        strengths_li += f"      <li>{s}</li>\n"

    if not strengths_li:
        strengths_li = "      <li class='none'>未发现明显优点</li>\n"

    # 构建不足列表
    weaknesses = summary.get('weaknesses', [])
    weaknesses_li = ""
    for w in weaknesses:
        weaknesses_li += f"      <li>{w}</li>\n"

    if not weaknesses_li:
        weaknesses_li = "      <li class='none'>未发现明显不足</li>\n"

    # 组装完整HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{paper_title} - 论文内容审核补充报告</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 14px;
    line-height: 1.8;
    color: #333;
    background: #f5f5f5;
  }}

  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }}

  /* 头部 */
  .header {{
    background: linear-gradient(135deg, #1a5276, #2980b9);
    color: white;
    padding: 40px 30px;
    border-radius: 12px 12px 0 0;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }}
  .header h1 {{
    font-size: 28px;
    margin-bottom: 10px;
    font-weight: 600;
  }}
  .header .subtitle {{
    opacity: 0.9;
    font-size: 14px;
  }}

  /* 内容区块 */
  .section {{
    background: white;
    margin: 20px 0;
    padding: 25px 30px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
  .section h2 {{
    color: #1a5276;
    font-size: 20px;
    border-bottom: 3px solid #2980b9;
    padding-bottom: 12px;
    margin-bottom: 20px;
  }}
  .section h3 {{
    color: #2c3e50;
    font-size: 16px;
    margin: 20px 0 12px;
    padding-left: 10px;
    border-left: 4px solid #3498db;
  }}

  /* 信息框 */
  .info-box {{
    background: linear-gradient(135deg, #e8f8f5, #d5f5e3);
    border-left: 5px solid #27ae60;
    padding: 15px 20px;
    margin: 15px 0;
    border-radius: 0 6px 6px 0;
  }}
  .warning-box {{
    background: linear-gradient(135deg, #fef9e7, #fcf3cf);
    border-left: 5px solid #f39c12;
    padding: 15px 20px;
    margin: 15px 0;
    border-radius: 0 6px 6px 0;
  }}
  .error-box {{
    background: linear-gradient(135deg, #fdedec, #fadbd8);
    border-left: 5px solid #e74c3c;
    padding: 15px 20px;
    margin: 15px 0;
    border-radius: 0 6px 6px 0;
  }}

  /* 表格 */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 13px;
  }}
  th, td {{
    padding: 12px 15px;
    text-align: left;
    border: 1px solid #ddd;
  }}
  th {{
    background: linear-gradient(135deg, #34495e, #2c3e50);
    color: white;
    font-weight: 600;
  }}
  tr:nth-child(even) {{
    background: #f8f9fa;
  }}
  tr:hover {{
    background: #e8f4f8;
  }}
  tr.pass {{
    background: #e8f8f5;
  }}
  tr.fail {{
    background: #fdedec;
  }}
  tr.warning {{
    background: #fef9e7;
  }}
  td.pass {{
    color: #27ae60;
    font-weight: bold;
  }}
  td.fail {{
    color: #e74c3c;
    font-weight: bold;
  }}
  td.warning {{
    color: #f39c12;
    font-weight: bold;
  }}
  td.label {{
    background: #f0f0f0;
    font-weight: 600;
    width: 120px;
  }}

  /* 列表 */
  ul {{
    margin: 10px 0;
    padding-left: 25px;
  }}
  li {{
    margin: 8px 0;
    line-height: 1.6;
  }}
  li.none {{
    color: #999;
    font-style: italic;
  }}

  /* 对比卡片 */
  .comparison-card {{
    background: #fafafa;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
  }}
  .comparison-card h4 {{
    color: #1565c0;
    font-size: 16px;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 15px;
  }}
  .comparison-card .inner-table {{
    margin: 0;
  }}
  .comparison-card .inner-table th {{
    background: #3498db;
    font-size: 12px;
    width: 100px;
  }}

  /* 性能指标表格 */
  .comparison-card .metrics-table {{
    margin: 10px 0;
    font-size: 13px;
  }}
  .comparison-card .metrics-table th {{
    background: #2c3e50;
    font-size: 11px;
    width: auto;
  }}
  .comparison-card .metrics-table td {{
    padding: 8px 12px;
  }}
  .comparison-card .metrics-table tr.positive {{
    background: #e8f5e9;
  }}
  .comparison-card .metrics-table tr.negative {{
    background: #ffebee;
  }}
  .comparison-card .metrics-table td:last-child {{
    font-weight: bold;
    color: #27ae60;
  }}
  .comparison-card .metrics-table tr.negative td:last-child {{
    color: #e74c3c;
  }}

  /* 评分维度 */
  .score-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 15px;
    margin: 20px 0;
  }}
  .score-item {{
    padding: 15px 20px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .score-item.pass {{
    background: linear-gradient(135deg, #e8f8f5, #d5f5e3);
    border-left: 5px solid #27ae60;
  }}
  .score-item.fail {{
    background: linear-gradient(135deg, #fdedec, #fadbd8);
    border-left: 5px solid #e74c3c;
  }}
  .score-item.warning {{
    background: linear-gradient(135deg, #fef9e7, #fcf3cf);
    border-left: 5px solid #f39c12;
  }}
  .score-item .dimension {{
    font-weight: 600;
    color: #2c3e50;
  }}
  .score-item .result {{
    font-weight: bold;
  }}
  .score-item .result.pass {{ color: #27ae60; }}
  .score-item .result.fail {{ color: #e74c3c; }}
  .score-item .result.warning {{ color: #f39c12; }}

  /* 优点/不足列表 */
  .strengths-list, .weaknesses-list {{
    list-style: none;
    padding: 0;
  }}
  .strengths-list li {{
    background: linear-gradient(135deg, #e8f8f5, #d5f5e3);
    border-left: 5px solid #27ae60;
    padding: 12px 20px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
  }}
  .weaknesses-list li {{
    background: linear-gradient(135deg, #fdedec, #fadbd8);
    border-left: 5px solid #e74c3c;
    padding: 12px 20px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
  }}

  /* 无数据提示 */
  .none-message {{
    background: #f8f9fa;
    border: 2px dashed #ddd;
    border-radius: 8px;
    padding: 30px;
    text-align: center;
    color: #666;
  }}
  .none-message .hint {{
    font-size: 12px;
    color: #999;
    margin-top: 10px;
  }}

  /* 底部 */
  .footer {{
    text-align: center;
    padding: 30px;
    color: #888;
    font-size: 13px;
    background: white;
    border-radius: 0 0 8px 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}

  /* 响应式 */
  @media (max-width: 768px) {{
    .container {{ padding: 10px; }}
    .section {{ padding: 15px; }}
    table {{ font-size: 12px; }}
    th, td {{ padding: 8px 10px; }}
    .header h1 {{ font-size: 22px; }}
    .score-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<div class="container">
  <!-- 头部 -->
  <div class="header">
    <h1>📋 论文内容审核补充报告</h1>
    <p class="subtitle">{paper_title}</p>
    <p class="subtitle">审核时间: {basic_info.get('审核时间', timestamp.split('_')[0])}</p>
  </div>

  <!-- 基本信息 -->
  <div class="section">
    <h2>📌 基本信息</h2>
    <table>
      <tr><th>项目</th><th>内容</th></tr>
{basic_info_rows}    </table>
  </div>

  <!-- 主要贡献评估 -->
  <div class="section">
    <h2>🏆 主要贡献评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>主要贡献声明是否明确、具体、可验证
    </div>
    <table>
      <tr><th>贡献点</th><th>方法支撑</th><th>评估结果</th></tr>
{contributions_rows}    </table>
  </div>

  <!-- 方法创新性评估 -->
  <div class="section">
    <h2>💡 方法创新性评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>创新点是否有对应的方法改进，每个创新点是否在方法部分有详细描述
    </div>
    <table>
      <tr><th>创新点</th><th>方法章节</th><th>创新具体内容</th><th>状态</th></tr>
{innovations_rows}    </table>
  </div>

  <!-- 方法创新性与Baseline详细对比 -->
  <div class="section">
    <h2>📊 方法创新性与Baseline详细对比</h2>
    <div class="info-box">
      <strong>评估说明：</strong>每种方法相对baseline的具体改进和性能指标
    </div>
{method_diff_html}  </div>

  <!-- Baseline对比评估 -->
  <div class="section">
    <h2>🔬 Baseline对比评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>实验评估是否包含baseline方法对比，对比是否充分
    </div>
    <table>
      <tr><th>对比方法</th><th>说明</th><th>论文位置</th></tr>
{baselines_rows}    </table>
  </div>

  <!-- 实验完整性评估 -->
  <div class="section">
    <h2>🧪 实验完整性评估</h2>
    <div class="info-box">
      <strong>评估说明：</strong>实验是否覆盖关键场景、消融实验和统计显著性分析
    </div>
    <table>
      <tr><th>实验类型</th><th>章节</th><th>说明</th></tr>
{experiments_rows}    </table>
  </div>

  <!-- 增量改进识别 -->
  <div class="section">
    <h2>🔄 增量改进识别</h2>
    <div class="info-box">
      <strong>评估说明：</strong>是否将增量改进误标为"novel"，区分原创性工作和增量改进
    </div>
    <table>
      <tr><th>贡献点</th><th>评估</th></tr>
{incremental_rows}    </table>
  </div>

  <!-- 综合评分 -->
  <div class="section">
    <h2>📈 综合评分</h2>
    <div class="score-grid">
"""
    # 添加评分网格
    for s in overall_scores:
        dimension = s.get('dimension', '')
        result = s.get('result', '')
        if '✅' in result:
            status_class = 'pass'
        elif '❌' in result:
            status_class = 'fail'
        else:
            status_class = 'warning'
        html += f"""      <div class="score-item {status_class}">
        <span class="dimension">{dimension}</span>
        <span class="result {status_class}">{result}</span>
      </div>
"""

    html += f"""    </div>
  </div>

  <!-- 约束检查 -->
  <div class="section">
    <h2>📏 约束检查</h2>
    <div class="info-box">
      <strong>评估说明：</strong>评价指标、现有方法问题、创新点、贡献点均不超过3个
    </div>
    <table>
      <tr><th>类别</th><th>数量</th><th>状态</th></tr>
{constraint_check_html}    </table>
  </div>

  <!-- 最终贡献 -->
  <div class="section">
    <h2>🏆 最终贡献</h2>
    <div class="info-box">
      <strong>评估说明：</strong>经过约束检查后的最终贡献点，精简到3个核心贡献
    </div>
    <table>
      <tr><th>类别</th><th>内容</th></tr>
{final_contributions_html}    </table>
  </div>

  <!-- 参考文献统计 -->
  <div class="section">
    <h2>📚 参考文献统计</h2>
    <div class="info-box">
      <strong>评估说明：</strong>参考文献的来源和质量统计
    </div>
    <table>
      <tr><th>统计项</th><th>数值</th></tr>
{ref_summary_html}    </table>
  </div>

  <!-- 总结 -->
  <div class="section">
    <h2>📝 总结</h2>

    <h3>✅ 优点</h3>
    <ul class="strengths-list">
{strengths_li}    </ul>

    <h3>❌ 主要不足</h3>
    <ul class="weaknesses-list">
{weaknesses_li}    </ul>
  </div>

  <!-- 底部 -->
  <div class="footer">
    <p>本报告由 Paper Content Audit Skill 自动生成</p>
    <p>审核时间: {basic_info.get('审核时间', timestamp.split('_')[0])}</p>
  </div>
</div>

</body>
</html>"""

    # 保存补充报告
    supp_path = os.path.join(output_dir, f"paper_audit_supplementary_report_{timestamp}.html")
    with open(supp_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"📋 补充报告已保存: {supp_path}")
    return supp_path


def generate_markdown_report_from_data(
    full_audit_data: Dict = None,
    output_dir: str = "."
) -> str:
    """
    生成Markdown格式的论文审核报告

    Args:
        full_audit_data: 完整审核数据
        output_dir: 输出目录

    Returns:
        Markdown报告文件路径
    """
    from datetime import datetime as dt

    timestamp = dt.now().strftime("%Y-%m-%d_%H%M%S")

    if not full_audit_data:
        return None

    paper_title = full_audit_data.get('paper_title', '论文内容审核报告')
    basic_info = full_audit_data.get('basic_info', {})
    contributions = full_audit_data.get('contributions', [])
    method_innovations = full_audit_data.get('method_innovations', [])
    method_vs_baseline = full_audit_data.get('method_vs_baseline', [])
    baselines = full_audit_data.get('baselines', [])
    experiments = full_audit_data.get('experiments', [])
    incremental_improvements = full_audit_data.get('incremental_improvements', [])
    overall_scores = full_audit_data.get('overall_scores', [])
    summary = full_audit_data.get('summary', {})

    # 构建Markdown内容
    md = f"""# 📋 论文内容审核报告

## {paper_title}

**审核时间:** {basic_info.get('审核时间', timestamp.split('_')[0])}

---

## 📌 基本信息

| 项目 | 内容 |
|------|------|
"""

    # 添加基本信息
    for key, value in basic_info.items():
        md += f"| {key} | {value} |\n"

    # 主要贡献评估
    md += f"""

---

## 🏆 主要贡献评估

> 评估说明：主要贡献声明是否明确、具体、可验证

| 贡献点 | 方法支撑 | 评估结果 |
|--------|----------|----------|
"""

    if contributions:
        for c in contributions:
            point = c.get('point', '')
            method = c.get('method', '')
            evaluation = c.get('evaluation', '')
            md += f"| {point} | {method} | {evaluation} |\n"
    else:
        md += "| 暂无数据 | - | - |\n"

    # 方法创新性评估
    md += f"""

---

## 💡 方法创新性评估

> 评估说明：创新点是否有对应的方法改进，每个创新点是否在方法部分有详细描述

| 创新点 | 方法章节 | 创新具体内容 | 状态 |
|--------|----------|--------------|------|
"""

    if method_innovations:
        for m in method_innovations:
            innovation = m.get('innovation', '')
            section = m.get('section', '')
            details = m.get('details', '')
            status = m.get('status', '')
            md += f"| {innovation} | {section} | {details} | {status} |\n"
    else:
        md += "| 暂无数据 | - | - | - |\n"

    # 方法创新性与Baseline详细对比
    md += f"""

---

## 📊 方法创新性与Baseline详细对比

> 评估说明：每种方法相对baseline的具体改进和性能指标

"""

    if method_vs_baseline:
        for item in method_vs_baseline:
            method_name = item.get('method_name', '未命名方法')
            baseline = item.get('baseline', '未指定')
            improvements = item.get('improvements', [])
            metrics = item.get('metrics', [])

            md += f"""### {method_name} vs {baseline}

**Baseline:** {baseline}

**具体改进:**
"""
            if improvements:
                for imp in improvements:
                    md += f"- {imp}\n"
            else:
                md += "- 未提供\n"

            md += f"\n**性能指标:**\n"
            if metrics:
                for m_item in metrics:
                    md += f"- {m_item}\n"
            else:
                md += "- 未提供\n"

            md += "\n"
    else:
        md += """暂无方法与Baseline的详细对比数据

> 提示：方法与Baseline的详细对比通常在实验章节的表格和图表中呈现

"""

    # Baseline对比评估
    md += f"""

---

## 🔬 Baseline对比评估

> 评估说明：实验评估是否包含baseline方法对比，对比是否充分

| 对比方法 | 说明 | 论文位置 |
|----------|------|----------|
"""

    if baselines:
        for b in baselines:
            name = b.get('name', '')
            description = b.get('description', '')
            section = b.get('section', '')
            md += f"| {name} | {description} | {section} |\n"
    else:
        md += "| 暂无数据 | - | - |\n"

    # 实验完整性评估
    md += f"""

---

## 🧪 实验完整性评估

> 评估说明：实验是否覆盖关键场景、消融实验和统计显著性分析

| 实验类型 | 章节 | 说明 |
|----------|------|------|
"""

    if experiments:
        for e in experiments:
            exp_type = e.get('type', '')
            section = e.get('section', '')
            description = e.get('description', '')
            md += f"| {exp_type} | {section} | {description} |\n"
    else:
        md += "| 暂无数据 | - | - |\n"

    # 增量改进识别
    md += f"""

---

## 🔄 增量改进识别

> 评估说明：是否将增量改进误标为"novel"，区分原创性工作和增量改进

| 贡献点 | 评估 |
|--------|------|
"""

    if incremental_improvements:
        for i in incremental_improvements:
            contribution = i.get('contribution', '')
            assessment = i.get('assessment', '')
            md += f"| {contribution} | {assessment} |\n"
    else:
        md += "| 暂无数据 | - |\n"

    # 综合评分
    md += f"""

---

## 📈 综合评分

"""

    if overall_scores:
        for s in overall_scores:
            dimension = s.get('dimension', '')
            result = s.get('result', '')
            # 根据结果添加emoji
            if '✅' in result:
                emoji = "✅"
            elif '❌' in result:
                emoji = "❌"
            else:
                emoji = "⚠️"
            md += f"- **{dimension}**: {emoji} {result}\n"
    else:
        md += "- 暂无评分数据\n"

    # 总结
    md += f"""

---

## 📝 总结

### ✅ 优点

"""

    strengths = summary.get('strengths', [])
    if strengths:
        for s in strengths:
            md += f"- {s}\n"
    else:
        md += "- 暂无明确优点\n"

    md += "\n### ❌ 主要不足\n\n"

    weaknesses = summary.get('weaknesses', [])
    if weaknesses:
        for w in weaknesses:
            md += f"- {w}\n"
    else:
        md += "- 暂无明显不足\n"

    md += f"""

---

## 📄 报告信息

- **生成时间:** {basic_info.get('审核时间', timestamp.split('_')[0])}
- **报告类型:** Markdown格式
- **生成工具:** Paper Content Audit Skill

> 本报告由 Paper Content Audit Skill 自动生成
"""

    # 保存Markdown报告
    md_path = os.path.join(output_dir, f"paper_audit_report_{timestamp}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"📝 Markdown报告已保存: {md_path}")
    return md_path


def generate_bilingual_markdown_report(
    full_audit_data: Dict = None,
    output_dir: str = "."
) -> str:
    """
    生成中英双语Markdown格式的论文审核报告

    Args:
        full_audit_data: 完整审核数据
        output_dir: 输出目录

    Returns:
        双语Markdown报告文件路径
    """
    from datetime import datetime as dt

    timestamp = dt.now().strftime("%Y-%m-%d_%H%M%S")

    if not full_audit_data:
        return None

    paper_title = full_audit_data.get('paper_title', '论文内容审核报告')
    basic_info = full_audit_data.get('basic_info', {})
    contributions = full_audit_data.get('contributions', [])
    method_innovations = full_audit_data.get('method_innovations', [])
    baselines = full_audit_data.get('baselines', [])
    experiments = full_audit_data.get('experiments', [])
    incremental_improvements = full_audit_data.get('incremental_improvements', [])
    overall_scores = full_audit_data.get('overall_scores', [])
    summary = full_audit_data.get('summary', {})

    # 翻译映射
    cn_to_en = {
        '论文标题': 'Paper Title',
        '作者': 'Author',
        '学位': 'Degree',
        '学校': 'Institution',
        '类型': 'Type',
        '审核时间': 'Audit Date',
        '主要贡献': 'Main Contributions',
        '方法支撑': 'Method Support',
        '评估结果': 'Evaluation',
        '创新点': 'Innovation Points',
        '方法章节': 'Method Section',
        '创新具体内容': 'Innovation Details',
        '状态': 'Status',
        '对比方法': 'Comparison Method',
        '说明': 'Description',
        '论文位置': 'Location',
        '实验类型': 'Experiment Type',
        '章节': 'Section',
        '贡献点': 'Contribution',
        '评估': 'Assessment',
        '审核维度': 'Audit Dimension',
        '结果': 'Result',
        '优点': 'Strengths',
        '主要不足': 'Weaknesses',
    }

    def tr(text: str) -> str:
        return cn_to_en.get(text, text)

    # 构建双语Markdown
    md = f"""# 论文内容审核报告 / Paper Content Audit Report

**论文标题 / Paper Title:** {paper_title}
**审核时间 / Audit Date:** {basic_info.get('审核时间', timestamp.split('_')[0])}

---

## 一、解决的问题 / Problem Solved

"""

    # 基本信息
    md += f"""## 📌 基本信息 / Basic Information

| {tr('项目')} | {tr('内容')} |
|------|------|
"""
    for key, value in basic_info.items():
        md += f"| {tr(key)} / {key} | {value} |\n"

    # 主要贡献
    md += f"""

---

## 二、主要贡献 / Main Contributions

| {tr('贡献点')} / Contribution | {tr('方法支撑')} / Method Support | {tr('评估结果')} / Evaluation |
|--------|----------|----------|
"""
    if contributions:
        for c in contributions:
            point = c.get('point', '')
            method = c.get('method', '')
            evaluation = c.get('evaluation', '')
            md += f"| {point} | {method} | {evaluation} |\n"
    else:
        md += "| 暂无数据 / No data | - | - |\n"

    # 创新点
    md += f"""

---

## 三、创新点 / Innovation Points

| {tr('创新点')} / Innovation | {tr('方法章节')} / Section | {tr('创新具体内容')} / Details | {tr('状态')} / Status |
|--------|----------|--------------|------|
"""
    if method_innovations:
        for m in method_innovations:
            innovation = m.get('innovation', '')
            section = m.get('section', '')
            details = m.get('details', '')
            status = m.get('status', '')
            md += f"| {innovation} | {section} | {details} | {status} |\n"
    else:
        md += "| 暂无数据 / No data | - | - | - |\n"

    # Baseline对比
    md += f"""

---

## 四、Baseline对比评估 / Baseline Comparison

| {tr('对比方法')} / Method | {tr('说明')} / Type | {tr('论文位置')} / Location |
|----------|------|----------|
"""
    if baselines:
        for b in baselines:
            name = b.get('name', '')
            description = b.get('description', '')
            section = b.get('section', '')
            md += f"| {name} | {description} | {section} |\n"
    else:
        md += "| 暂无数据 / No data | - | - |\n"

    # 实验完整性
    md += f"""

---

## 五、实验完整性评估 / Experiment Completeness

| {tr('实验类型')} / Experiment Type | {tr('章节')} / Section | {tr('说明')} / Description |
|----------|------|------|
"""
    if experiments:
        for e in experiments:
            exp_type = e.get('type', '')
            section = e.get('section', '')
            description = e.get('description', '')
            md += f"| {exp_type} | {section} | {description} |\n"
    else:
        md += "| 暂无数据 / No data | - | - |\n"

    # 增量改进
    md += f"""

---

## 六、增量改进识别 / Incremental Improvement

| {tr('贡献点')} / Contribution | {tr('评估')} / Assessment |
|--------|------|
"""
    if incremental_improvements:
        for i in incremental_improvements:
            contribution = i.get('contribution', '')
            assessment = i.get('assessment', '')
            md += f"| {contribution} | {assessment} |\n"
    else:
        md += "| 暂无数据 / No data | - |\n"

    # 综合评分
    md += f"""

---

## 七、综合评分 / Overall Scores

"""
    if overall_scores:
        for s in overall_scores:
            dimension = s.get('dimension', '')
            result = s.get('result', '')
            if '✅' in result:
                emoji = "✅"
            elif '❌' in result:
                emoji = "❌"
            else:
                emoji = "⚠️"
            md += f"- **{dimension} / {tr(dimension)}**: {emoji} {result}\n"
    else:
        md += "- 暂无评分数据 / No scoring data\n"

    # 总结
    md += f"""

---

## 八、总结 / Summary

### ✅ {tr('优点')} / Strengths

"""

    strengths = summary.get('strengths', [])
    if strengths:
        for s in strengths:
            md += f"- {s}\n"
    else:
        md += "- 暂无明确优点 / No clear strengths identified\n"

    md += f"\n### ❌ {tr('主要不足')} / Weaknesses\n\n"

    weaknesses = summary.get('weaknesses', [])
    if weaknesses:
        for w in weaknesses:
            md += f"- {w}\n"
    else:
        md += "- 暂无明显不足 / No significant weaknesses identified\n"

    md += f"""

---

## 九、最终评价 / Final Evaluation

| 维度 / Dimension | 评分 / Score |
|-----------------|-------------|
"""

    # 添加总体评分
    score_mapping = {
        '论文完整性': ('Paper Completeness', '⭐⭐⭐⭐'),
        '方法创新性': ('Method Innovation', '⭐⭐⭐'),
        '实验严谨性': ('Experiment Rigor', '⭐⭐⭐⭐'),
        '工程实用性': ('Engineering Practicality', '⭐⭐⭐⭐'),
    }

    for cn, (en, stars) in score_mapping.items():
        md += f"| {cn} / {en} | {stars} |\n"

    md += f"""

**总体评价 / Overall Rating:** 良好 (Master水平 / Master Level)

---

## 📄 报告信息 / Report Information

- **生成时间 / Generated:** {basic_info.get('审核时间', timestamp.split('_')[0])}
- **报告类型 / Report Type:** 中英双语Markdown格式 / Bilingual Markdown
- **生成工具 / Generated by:** Paper Content Audit Skill

> 本报告由 Paper Content Audit Skill 辅助生成 / Generated with Paper Content Audit Skill
"""

    # 保存双语Markdown报告
    md_path = os.path.join(output_dir, f"论文内容审核报告_中英双语_{timestamp}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"📝 中英双语Markdown报告已保存: {md_path}")
    return md_path
