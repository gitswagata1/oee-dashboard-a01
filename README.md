<div align="center">

[![header](https://capsule-render.vercel.app/api?type=waving&color=0:141e30,50:e44d26,100:f7b733&height=200&section=header&text=OEE%20Dashboard&fontSize=55&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Real-time%20manufacturing%20analytics%20%E2%80%94%20Cell%20A01&descAlignY=55&descSize=18&descColor=f0e6d3)](https://github.com/gitswagata1/oee-dashboard-a01)

**Monitor Overall Equipment Effectiveness in real-time — track availability, performance, and quality across your manufacturing floor.**

<br/>

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/gitswagata1/oee-dashboard-a01?style=for-the-badge&color=f7b733)](https://github.com/gitswagata1/oee-dashboard-a01/stargazers)
[![Forks](https://img.shields.io/github/forks/gitswagata1/oee-dashboard-a01?style=for-the-badge&color=70a5fd)](https://github.com/gitswagata1/oee-dashboard-a01/network/members)
[![Issues](https://img.shields.io/github/issues/gitswagata1/oee-dashboard-a01?style=for-the-badge&color=e44d26)](https://github.com/gitswagata1/oee-dashboard-a01/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

</div>

---

## What is OEE?

**OEE (Overall Equipment Effectiveness)** is the gold standard for measuring manufacturing productivity:

```
OEE = Availability x Performance x Quality
```

| Component | Measures | Formula |
|-----------|----------|---------|
| **Availability** | Uptime vs. planned time | Run Time / Planned Time |
| **Performance** | Actual vs. ideal speed | Ideal Cycle Time / Run Time |
| **Quality** | Good parts vs. total | Good Parts / Total Parts |

An OEE of **85%+** is considered world-class. This dashboard helps you track, analyze, and improve it.

---

## Features

- **Real-time OEE metrics** — Availability, Performance, Quality at a glance
- **Machine-level breakdown** — Compare OEE across all machines in Cell A01
- **Loss attribution** — See exactly where time and output is being lost
- **Time-weighted calculations** — Components capped at 100% for accurate aggregation
- **Band classification** — Color-coded health bands (good / mid / poor / critical)
- **Interactive Plotly charts** — Trend lines, bar charts, heatmaps with hover details
- **Date & machine filters** — Drill into any time range or specific machine
- **Streamlit UI** — Clean, responsive interface that works on desktop and mobile

---

## Architecture

```
  CSV Data (rows_clean.csv)     Meta Config (meta.json)
          |                            |
          v                            v
    +------------------------------------------+
    |          Streamlit App (app.py)           |
    |                                          |
    |  - Time-weighted OEE recompute engine    |
    |  - Loss attribution (A/P/Q losses)       |
    |  - Band classification                   |
    |  - Machine-level aggregation             |
    +------------------------------------------+
          |                |               |
          v                v               v
     Plotly Charts    KPI Metrics    Machine Tables
```

---

## Quickstart

### Prerequisites

- Python 3.10+

### Installation

```bash
# Clone the repository
git clone https://github.com/gitswagata1/oee-dashboard-a01.git
cd oee-dashboard-a01

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. The dashboard loads with sample data from Cell A01.

### Docker

```bash
docker build -t oee-dashboard .
docker run -p 8501:8501 oee-dashboard
```

---

## Data Format

The dashboard reads from `rows_clean.csv`. Expected columns:

| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Production date |
| `machine` | string | Machine identifier (e.g., A01-CNC-01) |
| `planned` | float | Planned production time (minutes) |
| `run` | float | Actual run time (minutes) |
| `ideal` | float | Ideal cycle time (minutes) |
| `total` | int | Total parts produced |
| `ok` | int | Good parts produced |
| `valid` | int | 1 = valid row, 0 = excluded |
| `aloss` | float | Availability loss (minutes) |
| `ploss` | float | Performance loss (minutes) |
| `qloss` | float | Quality loss (minutes) |

---

## Roadmap

- [ ] **Shift-wise OEE comparison** — Compare day, evening, and night shifts
- [ ] **CSV/Excel import** — Upload data through the UI
- [ ] **Email alerts** — Notify when OEE drops below threshold
- [ ] **Historical trends** — Week-over-week and month-over-month views
- [ ] **PDF report export** — Generate shift-end OEE reports

See the [open issues](https://github.com/gitswagata1/oee-dashboard-a01/issues) for community-requested features.

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Push and open a Pull Request

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built by [Swagata Banerjee](https://github.com/gitswagata1)**

*Making manufacturing data actionable.*

[![footer](https://capsule-render.vercel.app/api?type=waving&color=0:f7b733,50:e44d26,100:141e30&height=100&section=footer)](https://github.com/gitswagata1/oee-dashboard-a01)

</div>
