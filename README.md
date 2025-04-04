
# AHP Decision Support System

![AHP Demo](https://b1879915.smushcdn.com/1879915/wp-content/uploads/2023/10/SSDSI-Infographics-11.jpeg?lossy=2&strip=1&webp=1)

A web-based decision support system implementing the Analytic Hierarchy Process (AHP) method, built with Python and Streamlit.

## 🌟 Features

- **Multi-language support**: English & Vietnamese interfaces
- **Criteria & alternatives management**: Add, edit, and delete criteria/alternatives
- **Pairwise comparison**: Two input methods (dropdown & manual entry)
- **AHP calculations**: Compute weights, consistency ratio, and final scores
- **Visualization**: Interactive tables and charts
- **Analysis storage**: Save and retrieve previous analyses
- **Responsive UI**: Modern interface with tabs and intuitive controls

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation
1. Clone the repository:
```bash
git clone https://github.com/your-username/ahp-decision-support-system.git
cd ahp-decision-support-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run main.py
```

## 🛠️ Usage

### Creating a New Analysis
1. Define your problem (name and description)
2. Add evaluation criteria (e.g., cost, quality, time)
3. Add alternatives (e.g., Option A, Option B)
4. Initialize matrices

### Inputting Pairwise Comparisons
1. Choose input method (dropdown or manual)
2. Compare criteria using Saaty's scale (1-9)
3. Compare alternatives for each criterion
4. Calculate results

### Viewing Results
- Criteria weights
- Consistency ratio
- Alternative scores per criterion
- Final rankings

## 📦 Project Structure
```
ahp_project/
├── main.py                  # Main application entry
├── db.py                    # Database operations
├── ahp.py                   # AHP calculations
├── utils/                   # Utility functions
├── ui/                      # User interface components
└── requirements.txt         # Dependencies
```

## 🌐 Deployment

### Streamlit Cloud
[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

1. Fork this repository
2. Log in to [Streamlit Cloud](https://share.streamlit.io/)
3. Click "New app"
4. Select your repository and branch
5. Set main file path to `main.py`
6. Click "Deploy!"

### Heroku
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

```bash
heroku create your-app-name
git push heroku main
```

## 📚 AHP Method Details
The Analytic Hierarchy Process (AHP) involves:
1. Structuring the decision problem into a hierarchy
2. Pairwise comparisons using Saaty's scale
3. Weight calculation through matrix normalization
4. Consistency check (CR < 0.1 required)
5. Final score aggregation

## 🤝 Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a PR

## 📜 License
MIT - See [LICENSE](LICENSE) for details.

## 📧 Contact
- Email: [khacthien.dev@gmail.com](mailto:khacthien.dev@gmail.com)
- GitHub: [@khacthiennguyen](https://github.com/khacthiennguyen)

