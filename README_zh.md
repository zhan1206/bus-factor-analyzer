# Bus Factor Analyzer

公交车因素分析工具 - 计算项目贡献者分布与 Bus Factor

## 功能特性

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

## 授权

MIT License
