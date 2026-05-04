#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bus Factor Analyzer - 公交车因素分析工具
分析项目贡献者分布，计算 Bus Factor（最少多少人能导致项目停滞）
适用于团队风险评估、开源项目健康度评估
"""

import os
import re
import json
import argparse
import subprocess
from collections import Counter
from pathlib import Path


def run_git_command(cmd, cwd):
    """运行 git 命令并返回输出"""
    git_exe = r"C:\Users\朱子瞻\AppData\Local\Git\cmd\git.exe"
    try:
        result = subprocess.run(
            [git_exe] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=30
        )
        return result.stdout.strip(), result.returncode == 0
    except Exception as e:
        return str(e), False


def get_git_authors(project_path):
    """获取 git 仓库的所有作者"""
    output, ok = run_git_command(['log', '--format=%ae', '--follow'], project_path)
    if not ok:
        return []
    authors = [line.strip() for line in output.splitlines() if line.strip()]
    return authors


def get_git_commits_by_author(project_path):
    """获取每个作者的提交次数"""
    output, ok = run_git_command(['log', '--format=%ae', '--numstat'], project_path)
    if not ok:
        return {}

    author_commits = Counter()
    author_lines = Counter()
    current_author = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # numstat 格式: added\tdeleted\tfilename
        if '\t' in line:
            parts = line.split('\t')
            if len(parts) == 3:
                try:
                    added = int(parts[0]) if parts[0] != '-' else 0
                    deleted = int(parts[1]) if parts[1] != '-' else 0
                    author_lines[current_author] += added + deleted
                except (ValueError, TypeError):
                    pass
        else:
            # 这是一个 author email
            current_author = line
            author_commits[current_author] += 1

    return author_commits, author_lines


def get_file_counts_by_author(project_path):
    """获取每个作者修改的文件数"""
    output, ok = run_git_command(['log', '--format=%ae', '--name-only'], project_path)
    if not ok:
        return {}

    author_files = {}
    current_author = None

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        if '\t' not in line and not any(c.isdigit() for c in line):
            # 这是一个 author email
            current_author = line
            if current_author not in author_files:
                author_files[current_author] = set()
        elif current_author:
            author_files[current_author].add(line)

    return {k: len(v) for k, v in author_files.items()}


def anonymize_author(email):
    """将邮箱匿名化为贡献者标识"""
    if '@' in email:
        local = email.split('@')[0]
        # 保留前两位字母，其余用 * 代替
        name_part = re.match(r'^([a-zA-Z]+)', local)
        if name_part:
            name = name_part.group(1)
            if len(name) >= 3:
                return name[:2] + '*' * (len(name) - 2) + email[len(name):]
        return local[:3] + '***@' + email.split('@')[1] if '@' in email else local
    return email[:3] + '***'


def analyze_bus_factor(project_path):
    """主分析函数"""
    project_path = os.path.abspath(project_path)

    # 检查是否是 git 仓库
    git_dir = os.path.join(project_path, '.git')
    if not os.path.exists(git_dir):
        return {'error': f'不是 Git 仓库: {project_path}'}

    authors = get_git_authors(project_path)
    if not authors:
        return {'error': '无法获取 Git 提交历史，请确认目录有提交记录'}

    author_commits, author_lines = get_git_commits_by_author(project_path)
    author_files = get_file_counts_by_author(project_path)

    total_commits = len(authors)
    total_lines = sum(author_lines.values())

    # 统计每个作者的提交和代码行数
    author_stats = []
    seen = set()
    for author in authors:
        if author in seen:
            continue
        seen.add(author)
        commits = author_commits.get(author, 0)
        lines = author_lines.get(author, 0)
        files = author_files.get(author, 0)
        commit_pct = (commits / total_commits * 100) if total_commits > 0 else 0
        line_pct = (lines / total_lines * 100) if total_lines > 0 else 0

        author_stats.append({
            'email': author,
            'name': anonymize_author(author),
            'commits': commits,
            'commit_pct': round(commit_pct, 2),
            'lines': lines,
            'line_pct': round(line_pct, 2),
            'files': files,
        })

    # 按提交数排序
    author_stats.sort(key=lambda x: x['commits'], reverse=True)

    # 计算 Bus Factor：需要多少人才能覆盖 50% 和 80% 的代码
    cumulative = 0
    bus_factor_50 = 0
    bus_factor_80 = 0

    for i, stat in enumerate(author_stats):
        cumulative += stat['lines']
        pct = (cumulative / total_lines * 100) if total_lines > 0 else 0
        if bus_factor_50 == 0 and pct >= 50:
            bus_factor_50 = i + 1
        if bus_factor_80 == 0 and pct >= 80:
            bus_factor_80 = i + 1

    # Gini 系数（贡献均匀度）
    n = len(author_stats)
    if n > 1 and total_lines > 0:
        sorted_lines = sorted(stat['lines'] for stat in author_stats)
        cumsum = 0
        for i, l in enumerate(sorted_lines):
            cumsum += (2 * (i + 1) - n - 1) * l
        gini = cumsum / (n * sum(sorted_lines))
    else:
        gini = 0

    return {
        'project_path': project_path,
        'total_commits': total_commits,
        'total_contributors': len(author_stats),
        'total_lines': total_lines,
        'author_stats': author_stats,
        'bus_factor_50': bus_factor_50,
        'bus_factor_80': bus_factor_80,
        'gini_coefficient': round(gini, 4),
        'risk_level': _calc_risk(bus_factor_50, len(author_stats)),
    }


def _calc_risk(bus_50, total):
    """计算风险等级"""
    if bus_50 == 1:
        return 'CRITICAL'
    elif bus_50 == 2:
        return 'HIGH'
    elif bus_50 <= total * 0.2:
        return 'MEDIUM'
    else:
        return 'LOW'


# ============================================================
# 输出格式
# ============================================================

def format_text(result):
    """文本格式输出"""
    if result.get('error'):
        return f"错误: {result['error']}"

    lines = [
        '=' * 60,
        'Bus Factor Analyzer - 项目贡献者分析报告',
        '=' * 60,
        f'项目路径: {result["project_path"]}',
        f'总提交数: {result["total_commits"]}',
        f'贡献者数量: {result["total_contributors"]}',
        f'总代码行数: {result["total_lines"]}',
        f'Bus Factor (50%): {result["bus_factor_50"]} 人',
        f'Bus Factor (80%): {result["bus_factor_80"]} 人',
        f'Gini 系数: {result["gini_coefficient"]}',
        f'风险等级: {result["risk_level"]}',
        '',
        '-' * 60,
        '贡献者排名 (按提交数)',
        '-' * 60,
    ]

    for stat in result['author_stats']:
        lines.append(
            f"  {stat['name']} ({stat['email']})"
        )
        lines.append(
            f"    提交: {stat['commits']} ({stat['commit_pct']}%) | "
            f"代码行: {stat['lines']} ({stat['line_pct']}%) | "
            f"文件: {stat['files']}"
        )

    lines.append('=' * 60)
    return '\n'.join(lines)


def format_json(result):
    """JSON 格式输出"""
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_markdown(result):
    """Markdown 格式输出"""
    if result.get('error'):
        return f"## 错误\n\n{result['error']}"

    lines = [
        '# Bus Factor Analyzer 报告',
        '',
        f'**项目路径**: `{result["project_path"]}`',
        f'**总提交数**: {result["total_commits"]}',
        f'**贡献者数量**: {result["total_contributors"]}',
        f'**总代码行数**: {result["total_lines"]}',
        '',
        '## 关键指标',
        '',
        '| 指标 | 值 |',
        '|------|----|',
        f'| Bus Factor (50%) | {result["bus_factor_50"]} 人 |',
        f'| Bus Factor (80%) | {result["bus_factor_80"]} 人 |',
        f'| Gini 系数 | {result["gini_coefficient"]} |',
        f'| 风险等级 | {result["risk_level"]} |',
        '',
        '## 贡献者排名',
        '',
        '| 贡献者 | 提交 | 占比 | 代码行 | 占比 | 文件数 |',
        '|--------|------|------|--------|------|--------|',
    ]

    for stat in result['author_stats']:
        lines.append(
            f"| {stat['name']} | {stat['commits']} | "
            f"{stat['commit_pct']}% | {stat['lines']} | "
            f"{stat['line_pct']}% | {stat['files']} |"
        )

    return '\n'.join(lines)


def format_html(result):
    """HTML 格式输出"""
    if result.get('error'):
        return f"<h1>错误: {result['error']}</h1>"

    risk_colors = {'CRITICAL': '#dc3545', 'HIGH': '#fd7e14', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
    risk_color = risk_colors.get(result['risk_level'], '#6c757d')

    rows = ''
    for stat in result['author_stats']:
        rows += f'<tr><td>{stat["name"]}</td><td>{stat["commits"]}</td>'
        rows += f'<td>{stat["commit_pct"]}%</td><td>{stat["lines"]}</td>'
        rows += f'<td>{stat["line_pct"]}%</td><td>{stat["files"]}</td></tr>'

    return f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Bus Factor Report</title>
<style>
body {{ font-family: -apple-system, sans-serif; margin: 40px; background: #f9f9f9; }}
h1 {{ color: #333; }}
.metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 20px 0; }}
.card {{ padding: 20px; border-radius: 8px; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
.card h3 {{ margin: 0 0 8px; color: #666; font-size: 14px; }}
.card p {{ margin: 0; font-size: 28px; font-weight: bold; }}
.risk {{ border-left: 4px solid {risk_color}; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
th {{ background: #f2f2f2; font-weight: 600; }}
</style></head><body>
<h1>Bus Factor Analyzer 报告</h1>
<p><strong>项目:</strong> {result['project_path']}</p>
<div class="metrics">
  <div class="card"><h3>Bus Factor (50%)</h3><p>{result['bus_factor_50']} 人</p></div>
  <div class="card"><h3>Bus Factor (80%)</h3><p>{result['bus_factor_80']} 人</p></div>
  <div class="card risk"><h3>风险等级</h3><p>{result['risk_level']}</p></div>
</div>
<table><tr><th>贡献者</th><th>提交</th><th>提交%</th><th>代码行</th><th>行数%</th><th>文件数</th></tr>{rows}</table>
</body></html>'''


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='Bus Factor Analyzer - 分析项目贡献者分布和 Bus Factor'
    )
    parser.add_argument('project_path', nargs='?', default='.', help='项目路径 (默认当前目录)')
    parser.add_argument('--format', choices=['text', 'json', 'markdown', 'html'],
                        default='text', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    args = parser.parse_args()

    result = analyze_bus_factor(args.project_path)

    formatters = {
        'text': format_text,
        'json': format_json,
        'markdown': format_markdown,
        'html': format_html,
    }
    output = formatters[args.format](result)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'报告已保存到: {args.output}')
    else:
        print(output)


if __name__ == '__main__':
    main()
