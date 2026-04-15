# Paper Content Audit Tool

A skill for auditing academic papers, evaluating main contributions, methodological innovation, experimental evaluation, and detailed comparison with baselines.

## Features

| Audit Item | Type | Description |
|------------|------|-------------|
| Main Contributions | ✅/❌ | Whether contributions are clear, specific, and verifiable |
| Method Innovation | ✅/❌ | Whether innovations have corresponding method improvements |
| Method-Innovation Mapping | ⚠️ Warning | Whether each innovation has detailed method description |
| Method vs Baseline | ✅ | Detailed comparison of improvements and performance metrics |
| Baseline Comparison | ❌ Issue | Whether baseline methods are included in evaluation |
| Experiment Completeness | ⚠️ Warning | Whether key scenarios and ablation studies are covered |
| Incremental Improvement | ⚠️ Warning | Whether incremental improvements are mislabeled as "novel" |
| Missing Comparisons | ⚠️ Warning | Whether any methods or datasets are missing |

## Quick Start

### Basic Usage

```bash
python3 scripts/paper_audit_script.py <pdf_path> [output_dir]
# or
python3 scripts/paper_audit_script.py --text "<paper_text>" [output_dir]
```

### Parameters

- `pdf_path`: Path to the paper PDF file
- `--text` or `-t`: Directly pass paper text content
- `output_dir`: Optional, output directory for the report (default: current directory)

### Examples

```bash
python3 paper_audit_script.py /path/to/paper.pdf
python3 paper_audit_script.py --text "Full paper text content..."
python3 paper_audit_script.py paper.pdf ./output
```

## Dependencies

Install multiple PDF extraction libraries for best Chinese and English support:

```bash
pip install pypdf pdfplumber PyMuPDF
```

| Library | Description |
|---------|-------------|
| `pdfplumber` | Recommended, better Chinese support |
| `PyMuPDF` (fitz) | Alternative, better for tables and graphics |
| `pypdf` | Fallback option |

## Workflow

1. **Extract Paper Content** - Use pypdf to read PDF or parse text
2. **Analyze Contribution Claims** - Extract contributions from abstract, introduction, conclusion
3. **Verify Innovation Mapping** - Check if each contribution has method support
4. **Check Experimental Evaluation** - Verify baseline comparison, experiment completeness
5. **Generate Report** - Output structured audit report

## Output Report

Generates a **bilingual (Chinese/English) HTML format** structured report.

**Report Contents:**
1. **Basic Information** - Title, authors, degree, institution, type
2. **Main Contributions Evaluation** - Contribution points, method support, evaluation table
3. **Method Innovation Evaluation** - Innovation points, sections, detailed content table
4. **Method vs Baseline Detailed Comparison** - Specific improvements and performance metrics for each method
5. **Baseline Comparison Evaluation** - Compared methods list, descriptions, paper locations
6. **Experiment Completeness Evaluation** - Experiment types, sections, descriptions
7. **Incremental Improvement Identification** - Incremental vs novel assessment for each contribution
8. **Overall Scores** - Scoring results for each audit dimension
9. **Summary** - Strengths list + Main weaknesses list

**Report Format:** HTML (openable in browser)
- Bilingual titles
- Tabular display of audit results
- Color coding: Green (✅ Pass), Red (❌ Issue), Yellow (⚠️ Warning)
- info-box/warning-box/error-box for different information types
- comparison-card for method vs Baseline detailed comparisons
- Responsive layout, mobile-friendly

## Report Data Structure

Use `full_audit_data` parameter to pass complete audit information:

```python
full_audit_data = {
    'paper_title': 'Paper Title',
    'basic_info': {
        'Title': '...',
        'Authors': '...',
        'Degree': '...',
        'Institution': '...',
        'Type': '...',
        'Audit Date': 'YYYY-MM-DD'
    },
    'contributions': [
        {'point': 'Contribution', 'method': 'Method Support', 'evaluation': '✅/❌'}
    ],
    'method_innovations': [
        {'innovation': 'Innovation', 'section': 'Section', 'details': 'Details', 'status': '✅/❌'}
    ],
    'method_vs_baseline': [
        {
            'method_name': 'Method Name',
            'baseline': 'Baseline',
            'improvements': ['Improvement 1', 'Improvement 2'],
            'metrics': ['Metric 1', 'Metric 2']
        }
    ],
    'baselines': [
        {'name': 'Baseline Name', 'description': 'Description', 'section': 'Location'}
    ],
    'experiments': [
        {'type': 'Experiment Type', 'section': 'Section', 'description': 'Description'}
    ],
    'incremental_improvements': [
        {'contribution': 'Contribution', 'assessment': 'Assessment'}
    ],
    'overall_scores': [
        {'dimension': 'Dimension', 'result': '✅/⚠️/❌'}
    ],
    'summary': {
        'strengths': ['Strength 1', 'Strength 2'],
        'weaknesses': ['Weakness 1', 'Weakness 2']
    }
}
```

## Project Structure

```
scripts/
├── paper_audit_script.py   # Main entry point
├── extractors/
│   └── content.py          # Content extraction
├── checks/
│   ├── contributions.py    # Contribution extraction and analysis
│   ├── innovation.py        # Innovation verification
│   ├── baseline_comparison.py # Baseline comparison check
│   └── experiments.py       # Experiment completeness check
└── reports/
    └── generator.py         # Report generation (supports full_audit_data)
```

## Audit Standards Reference

### Main Contributions Evaluation Criteria

**Good Contribution Statements:**
- Clearly state the problem being solved
- Point out advantages over existing methods
- Contributions are specific and verifiable

**Poor Contribution Statements:**
- Only describe the task without solution
- Lack comparison with existing work
- Contributions too broad or unverifiable

### Method Innovation Evaluation Criteria

Each innovation must satisfy:
1. **Method Level** - Detailed algorithm/model description in method section
2. **Clear Improvement** - Clearly state specific improvements over baseline
3. **Theoretical Support** - Have theoretical analysis or motivation explanation

### Method vs Baseline Comparison Criteria

**Must Include:**
- Specific improvements of the method over each baseline
- Performance improvement metrics (numerical comparison)
- Improvement percentage or absolute values

**Should Include:**
- Visual comparison cards (comparison-card)
- Ablation study results

### Baseline Comparison Evaluation Criteria

**Must Include:**
- Comparison with at least one mainstream baseline method
- Performance comparison on standard datasets
- Statistical significance explanation (if applicable)

**Should Include:**
- Ablation Study
- Fair comparison with similar methods
- Complexity/efficiency comparison

## Adding New Audit Items

To add new audit items, create an independent module under `scripts/checks/`:

```python
# scripts/checks/my_check.py
from typing import List, Dict

def check_my_item(content: Dict, ...) -> Dict:
    """
    Audit item description

    Returns:
        Dict with keys: result, issues, warnings
    """
    issues = []
    warnings = []
    result = {}

    # Audit logic...

    return {
        'result': result,
        'issues': issues,
        'warnings': warnings
    }
```

Then export in `scripts/checks/__init__.py` and call in `paper_audit_script.py`'s `run_full_audit()`.

## Notes

1. **Text Extraction Limitations**: PDF text extraction may not capture exact formatting
2. **Subjective Evaluation**: Innovation and contribution assessment has some subjectivity
3. **Domain Differences**: Definition of innovation and baseline may vary across fields
4. **Report Generation**: Using `full_audit_data` parameter is recommended for best results
