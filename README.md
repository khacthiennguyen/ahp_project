
# AHP Decision Support System

![AHP System Demo](https://b1879915.smushcdn.com/1879915/wp-content/uploads/2023/10/SSDSI-Infographics-11.jpeg?lossy=2&strip=1&webp=1)

A web-based decision support tool implementing the Analytic Hierarchy Process (AHP) method, built with Python and Streamlit.

## ✨ Key Features
- **Bilingual Interface**: English & Vietnamese support
- **Criteria Management**: Dynamic CRUD operations for decision criteria
- **Alternative Evaluation**: Comparative assessment framework
- **Flexible Input Methods**:
  - Dropdown selection (Saaty scale 1-9)
  - Manual matrix input
- **Automated AHP Calculations**:
  - Weight computation
  - Consistency Ratio (CR) validation
  - Final scoring and ranking
- **Interactive Visualization**: Dynamic charts and comparison matrices
- **Analysis Persistence**: Local storage of decision models

## 🚀 Quick Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup
```bash
# Clone repository
git clone https://github.com/khacthiennguyen/ahp-decision-support-system.git
cd ahp-decision-support-system

# Install dependencies
pip install -r requirements.txt

# Launch application
streamlit run main.py
```

## 🛠️ User Guide

### 1. Create New Analysis
1. **Problem Definition**:
   - Enter analysis title and description
2. **Criteria Setup**:
   - Add decision factors (e.g., Cost, Quality)
   - Supports bulk entry (one criterion per line)
3. **Alternative Options**:
   - Define comparable solutions
   - Real-time table editing

### 2. Pairwise Comparisons
```python
# Example comparison matrix
[[1,   3,   5],
 [1/3, 1,   2],
 [1/5, 1/2, 1]]
```

**Input Methods**:
- **Dropdown**: Predefined Saaty scale values
- **Manual**: Direct matrix cell editing

**Validation**:
- Automatic CR calculation
- Warning for inconsistent judgments (CR ≥ 0.1)

### 3. Results Interpretation
- **Criteria Weights**: Relative importance percentages
- **Alternative Scores**: Performance by criterion
- **Final Ranking**: Comprehensive evaluation results

## 📦 System Architecture
```
ahp-system/
├── main.py                 # Application entry point
├── ahp_core.py             # AHP algorithm implementation
├── data_models/            # Database schemas
│   ├── analysis.py
│   └── comparison.py
├── ui/                     # Interface components
│   ├── input_panels.py
│   └── visualization.py
└── requirements.txt        # Dependency specifications
```

## 🌐 Deployment Options

### Streamlit Cloud
[![Deploy on Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/cloud)

1. Fork repository
2. Connect to Streamlit Cloud
3. Set main path to `main.py`
4. Deploy

### Heroku
```bash
# Create new instance
heroku create ahp-decision-tool

# Deploy application
git push heroku main
```

## 📊 AHP Methodology
1. **Hierarchy Construction**:
   - Goal → Criteria → Alternatives
2. **Pairwise Comparison**:
   ```math
   A = \begin{bmatrix}
   1 & a_{12} & \cdots & a_{1n} \\
   1/a_{12} & 1 & \cdots & a_{2n} \\
   \vdots & \vdots & \ddots & \vdots \\
   1/a_{1n} & 1/a_{2n} & \cdots & 1
   \end{bmatrix}
   ```
3. **Consistency Verification**:
   - λₘₐₓ calculation
   - CI = (λₘₐₓ - n)/(n - 1)
   - CR = CI/RI

## 🤝 Contribution Guidelines
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

## 📜 License
MIT License - See [LICENSE](LICENSE) for full terms.

## 📩 Contact Information
- **Developer**: Khac Thien Nguyen
- **Email**: [khacthien.dev@gmail.com](mailto:khacthien.dev@gmail.com)
- **GitHub**: [@khacthiennguyen](https://github.com/khacthiennguyen)
