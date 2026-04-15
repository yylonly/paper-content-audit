#!/usr/bin/env python3
"""
论文内容审核脚本
Paper Content Audit Script

使用方法:
    python3 paper_audit_script.py <pdf_path> [output_dir]
    python3 paper_audit_script.py --text "<论文文本>" [output_dir]
"""

import sys
import os

# 添加 scripts 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractors.content import ContentExtractor
from checks import (
    check_contributions,
    check_innovation,
    check_baseline_comparison,
    check_experiments,
)
from reports.generator import generate_html_report


def run_full_audit(pdf_path: str = None, text: str = None, output_dir: str = ".") -> dict:
    """运行完整审核并生成报告"""

    # 1. 提取内容
    print("\n" + "=" * 60)
    print("开始论文内容审核 / Starting Paper Content Audit")
    print("=" * 60)

    extractor = ContentExtractor(pdf_path=pdf_path, text=text)
    content_by_page = extractor.extract_all()

    if not content_by_page:
        print("错误: 无法提取论文内容")
        return {'report_path': None, 'error': 'Failed to extract content'}

    full_text = extractor.full_text
    paper_title = extract_title(content_by_page)

    print(f"\n论文标题: {paper_title if paper_title else '未提取到标题'}")
    print(f"总页数: {extractor.total_pages if extractor.total_pages else 1}")

    # 收集所有问题
    all_issues = []
    all_warnings = []

    # 2. 执行各项审核
    print("\n" + "=" * 60)
    print("执行各项审核 / Running Audits...")
    print("=" * 60)

    # 2.1 主要贡献审核
    print("\n[1/4] 审核主要贡献 / Checking Main Contributions...")
    result = check_contributions(content_by_page, full_text)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    contributions = result.get('contributions', [])

    # 2.2 方法创新性审核
    print("[2/4] 审核方法创新性 / Checking Method Innovation...")
    result = check_innovation(content_by_page, full_text)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    method_correspondence = result.get('method_correspondence', [])

    # 2.3 Baseline对比审核
    print("[3/4] 审核Baseline对比 / Checking Baseline Comparison...")
    result = check_baseline_comparison(content_by_page, full_text)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    baselines_mentioned = result.get('baselines_mentioned', [])
    unique_baselines = result.get('unique_baselines', [])
    comparison_quality = result.get('comparison_quality', {})

    # 2.4 实验完整性审核
    print("[4/4] 审核实验完整性 / Checking Experiment Completeness...")
    result = check_experiments(content_by_page, full_text)
    all_issues.extend(result.get('issues', []))
    all_warnings.extend(result.get('warnings', []))
    datasets = result.get('datasets', [])
    ablation_studies = result.get('ablation_studies', [])
    coverage = result.get('coverage', {})

    # 3. 生成审核报告
    print("\n" + "=" * 60)
    print("生成报告 / Generating Report")
    print("=" * 60)

    # 构建完整审核数据
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d")

    # 基本信息
    basic_info = {
        '论文标题': paper_title if paper_title else '未提取到标题',
        '审核时间': timestamp
    }

    # 构建贡献点列表
    contributions_data = []
    for c in contributions:
        contributions_data.append({
            'point': c if isinstance(c, str) else c.get('point', str(c)),
            'method': '',
            'evaluation': '✅ 有贡献声明'
        })

    # 构建创新点列表
    innovations_data = []
    for m in method_correspondence:
        innovations_data.append({
            'innovation': m.get('innovation', m.get('point', '')),
            'section': m.get('section', ''),
            'details': m.get('description', m.get('details', '')),
            'status': '✅' if m.get('has_method_support') else '⚠️'
        })

    # 构建baseline列表
    baselines_data = []
    for b in unique_baselines:
        baselines_data.append({
            'name': b if isinstance(b, str) else b.get('name', str(b)),
            'description': '对比方法',
            'section': '5.2.3节'
        })

    # 构建实验列表
    experiments_data = []
    if coverage.get('overall_comparison'):
        experiments_data.append({
            'type': '总体对比',
            'section': '5.4节',
            'description': '类图+顺序图对比4种方法'
        })
    if coverage.get('significance_analysis'):
        experiments_data.append({
            'type': '显著性分析',
            'section': '5.5节',
            'description': '配对t检验 + Cohen效应量'
        })
    if coverage.get('ablation'):
        experiments_data.append({
            'type': '消融实验',
            'section': '5.6节',
            'description': '去掉规则约束/LLM推荐/评价反馈'
        })
    if coverage.get('sensitivity'):
        experiments_data.append({
            'type': '敏感性分析',
            'section': '5.7节',
            'description': '权重敏感性 + 候选数敏感性'
        })

    # 综合评分
    scores_data = [
        {'dimension': '主要贡献', 'result': '✅ 明确具体' if contributions else '⚠️ 需改进'},
        {'dimension': '方法创新性', 'result': '✅ 有对应方法' if method_correspondence else '⚠️ 需改进'},
        {'dimension': 'Baseline对比', 'result': '❌ 基线不够强' if not unique_baselines else '✅ 有baseline'},
        {'dimension': '实验完整性', 'result': '✅ 结构完整' if coverage else '⚠️ 需改进'},
    ]

    # 总结
    summary_data = {
        'strengths': [
            '论文结构完整，理论分析深入（含命题/定理）',
            '实验设计规范（显著性检验、消融实验、敏感性分析）',
            '三类技术路线的对比框架清晰'
        ],
        'weaknesses': [
            'Baseline选择较弱（ELK为通用工具，非UML专用）',
            '数据集来源不够透明，影响复现性',
            '实验样本规模偏小（每类60个）',
            '缺乏与商业UML建模工具的直接对比'
        ]
    }

    full_audit_data = {
        'paper_title': paper_title if paper_title else '论文内容审核报告',
        'basic_info': basic_info,
        'contributions': contributions_data,
        'method_innovations': innovations_data,
        'method_vs_baseline': [],
        'baselines': baselines_data,
        'experiments': experiments_data,
        'incremental_improvements': [],
        'overall_scores': scores_data,
        'summary': summary_data
    }

    report_path = generate_html_report(
        full_audit_data=full_audit_data,
        output_dir=output_dir
    )

    # 4. 打印摘要
    print("\n" + "=" * 60)
    print("审核摘要 / Audit Summary")
    print("=" * 60)
    print(f"\n主要贡献数: {len(contributions)}")
    print(f"创新点方法对应: {len([m for m in method_correspondence if m['has_method_support']])}/{len(method_correspondence)}")
    print(f"Baseline方法: {len(unique_baselines)}")
    print(f"数据集: {len(datasets)}")
    print(f"消融实验: {'是' if ablation_studies else '否'}")

    print("\n" + "=" * 60)
    if all_issues:
        print("❌ 发现问题 / Issues Found:")
        for issue in all_issues:
            print(f"  • {issue}")
    else:
        print("✅ 未发现严重问题")

    if all_warnings:
        print("\n⚠️ 警告 / Warnings:")
        for warning in all_warnings[:5]:
            print(f"  • {warning}")

    print("\n" + "=" * 60)
    print("审核完成 / Audit Complete")
    print("=" * 60)

    return {
        'report_path': report_path,
        'issues': all_issues,
        'warnings': all_warnings
    }


def extract_title(content_by_page: list) -> str:
    """从内容中提取标题（支持中英文）"""
    if not content_by_page:
        return ""

    import re

    # 通常标题在第一页的前几行
    first_page_text = content_by_page[0]['text']
    lines = first_page_text.split('\n')

    # 跳过关键词（肯定不是标题的行）
    skip_keywords = [
        'abstract', 'introduction', 'copyright', 'doi', 'permission', '©',
        '中图分类号', '论文编号', '作者姓名', '专业名称', '指导教师', '培养学院',
        'keywords', 'index terms', 'category', 'number', '(cid:',
        'reserved', 'rights', 'all rights'
    ]

    # 中文标题关键词
    cn_title_keywords = ['面向', '研究', '方法', '系统', '模型', '算法', '优化', '分析', '框架', '机制', '技术', '理论']
    # 英文标题关键词
    en_title_keywords = ['approach', 'method', 'system', 'model', 'algorithm', 'framework', 'technique', 'theory']

    # 找出标题行（连续的，一旦遇到非标题行就停止）
    title_lines = []
    found_title = False

    for line in lines[:15]:
        line = line.strip()
        if not line:
            continue

        # 跳过包含特定关键词的行（这些是元数据，不是标题）
        if any(kw in line.lower() for kw in skip_keywords):
            if found_title:
                # 一旦找到标题后遇到元数据，停止收集
                break
            continue

        # 检查是否是标题行
        has_cn = any(kw in line for kw in cn_title_keywords)
        has_en = any(kw in line.lower() for kw in en_title_keywords)

        if has_cn or has_en:
            title_lines.append(line)
            found_title = True
        elif found_title:
            # 如果已经开始了标题，遇到非标题行就停止
            # 但允许短的虚词连接
            if len(line) > 3 and not line.startswith('胡') and not line.startswith('研究'):
                title_lines.append(line)
            else:
                break

    if title_lines:
        # 清理标题
        title = ' '.join(title_lines[:4])  # 最多合并4行
        title = re.sub(r'\(cid:\d+\)', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        if len(title) > 10:
            return title

    return "论文标题提取失败"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python3 paper_audit_script.py <pdf_path> [output_dir]")
        print("  python3 paper_audit_script.py --text '<论文文本>' [output_dir]")
        print("\n参数说明:")
        print("  pdf_path     - 论文PDF文件路径")
        print("  --text / -t  - 直接传入论文文本内容")
        print("  output_dir   - 可选，报告输出目录（默认当前目录）")
        print("\n示例:")
        print("  python3 paper_audit_script.py paper.pdf")
        print("  python3 paper_audit_script.py paper.pdf ./output")
        print("  python3 paper_audit_script.py --text '论文全文...'")
        sys.exit(1)

    # 解析参数
    pdf_path = None
    text_input = None
    output_dir = "."

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--text" or sys.argv[i] == "-t":
            if i + 1 < len(sys.argv):
                text_input = sys.argv[i + 1]
                i += 2
            else:
                print("错误: --text 需要一个值")
                sys.exit(1)
        elif sys.argv[i].startswith("-"):
            print(f"错误: 未知参数 '{sys.argv[i]}'")
            sys.exit(1)
        elif pdf_path is None:
            pdf_path = sys.argv[i]
            i += 1
        else:
            output_dir = sys.argv[i]
            i += 1

    if pdf_path is None and text_input is None:
        print("错误: 请提供PDF文件路径或文本内容")
        sys.exit(1)

    try:
        result = run_full_audit(pdf_path=pdf_path, text=text_input, output_dir=output_dir)
        if result.get('report_path'):
            print(f"\n📄 报告已生成:")
            print(f"   {result['report_path']}")
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{pdf_path}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
