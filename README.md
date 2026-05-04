# Bus Factor Analyzer

Analyze project contributor distribution and calculate Bus Factor - how many people need to leave for a project to stall.

## Features

- **Bus Factor Calculation**: Calculate the minimum number of contributors covering 50%/80% of code
- **Contributor Ranking**: Rank by commits, lines of code, and files modified
- **Gini Coefficient**: Measure contribution distribution evenness
- **Risk Assessment**: CRITICAL / HIGH / MEDIUM / LOW four-level risk alerts
- **Multiple Output Formats**: Text, JSON, Markdown, HTML
- **Zero Dependencies**: Uses only Python standard library

## Usage

```bash
# Analyze current Git repository
python scripts/bus_factor_analyzer.py .

# Specify repo path
python scripts/bus_factor_analyzer.py /path/to/repo

# Output JSON format
python scripts/bus_factor_analyzer.py . --format json -o report.json

# Output Markdown report
python scripts/bus_factor_analyzer.py . --format markdown -o report.md

# Output HTML report
python scripts/bus_factor_analyzer.py . --format html -o report.html
```

## Risk Levels

| Level | Bus Factor (50%) | Description |
|-------|------------------|-------------|
| CRITICAL | 1 | All code by one person, extremely high risk |
| HIGH | 2 | Few core contributors, needs attention |
| MEDIUM | 3-4 | Reasonable contributor distribution |
| LOW | 5+ | Balanced distribution, low risk |

## Installation

No installation needed. Requires Python 3.8+.

```bash
git clone https://github.com/zhan1206/bus-factor-analyzer.git
cd bus-factor-analyzer
python scripts/bus_factor_analyzer.py --help
```

## License

MIT License
