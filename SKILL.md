---
name: "bus-factor-analyzer"
description: "Bus Factor Analyzer - 分析项目贡献者分布，计算 Bus Factor（最少多少人能导致项目停滞）。适用于团队风险评估、开源项目健康度评估。触发词：bus factor、贡献者分析、项目风险、团队依赖。"
agent_created: true
---

# Bus Factor Analyzer

> 分析项目贡献者分布，计算 Bus Factor（最少多少人能导致项目停滞）

## 功能概述

- **Bus Factor 计算**：计算覆盖 50%/80% 代码的最小贡献者数量
- **贡献者排名**：按提交数、代码行数、修改文件数排名
- **Gini 系数**：衡量贡献分布的均匀程度
- **风险评估**：CRITICAL / HIGH / MEDIUM / LOW 四级风险提示
- **多格式报告**：Text、JSON、Markdown、HTML
- **零依赖**：仅使用 Python 标准库

## 快速使用

```bash
# 分析当前 Git 仓库
python scripts/bus_factor_analyzer.py .

# 指定仓库路径
python scripts/bus_factor_analyzer.py /path/to/repo

# 输出 JSON 格式
python scripts/bus_factor_analyzer.py . --format json -o report.json

# 输出 Markdown 报告
python scripts/bus_factor_analyzer.py . --format markdown -o report.md

# 输出 HTML 报告
python scripts/bus_factor_analyzer.py . --format html -o report.html
```

## 输出示例

```
============================================================
Bus Factor Analyzer - 项目贡献者分析报告
============================================================
项目路径: /path/to/project
总提交数: 150
贡献者数量: 5
总代码行数: 12000
Bus Factor (50%): 2 人
Bus Factor (80%): 3 人
Gini 系数: 0.35
风险等级: MEDIUM

------------------------------------------------------------
贡献者排名 (按提交数)
------------------------------------------------------------
  alice***@example.com (alice@example.com)
    提交: 80 (53.33%) | 代码行: 6000 (50.00%) | 文件: 45
  bob***@example.com (bob@example.com)
    提交: 40 (26.67%) | 代码行: 3000 (25.00%) | 文件: 30
============================================================
```

## 风险等级说明

| 等级 | Bus Factor (50%) | 说明 |
|------|------------------|------|
| CRITICAL | 1 | 所有代码由一人完成，极高风险 |
| HIGH | 2 | 核心贡献者少，需要警惕 |
| MEDIUM | 3-4 | 贡献者分布较合理 |
| LOW | 5+ | 贡献者分布均衡，风险低 |

## 安装

无需安装任何依赖，直接使用 Python 3.8+ 运行。

```bash
git clone https://github.com/zhan1206/bus-factor-analyzer.git
cd bus-factor-analyzer
python scripts/bus_factor_analyzer.py --help
```

## 在 WorkBuddy 中使用

直接对 WorkBuddy 说：
- "分析这个项目的 Bus Factor"
- "检查项目贡献者分布"
- "团队风险评估"

## 授权

MIT License
