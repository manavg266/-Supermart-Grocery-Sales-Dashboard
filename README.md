# Sapphire IQ — Supermart Grocery Sales Dashboard

A practical management Streamlit analytics dashboard built around the **Supermart Grocery Sales** dataset.

## What this project answers

### 1. Overall Sales Performance
- Total sales and profit
- Profit margin and average order value
- Sales/profit trends
- Category and region leaders

### 2. Product Performance
- Category and sub-category performance
- Sales vs profit portfolio analysis
- High-sales / low-profit opportunity monitor

### 3. Profit & Discount
- Discount-band analysis
- Discount vs profit relationship
- Category margin vs discount analysis

### 4. Geographic Performance
- Region performance
- City-level sales/profit analysis
- High-sales / low-margin location monitoring

## UI / UX
- Executive dashboard layout
- Dark enterprise sidebar
- KPI cards
- Interactive Plotly charts
- Global filters
- Management signals
- Data-quality monitoring
- Filtered CSV export
- Responsive wide-screen layout

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

The app automatically loads the CSV from `data/`.

## Project structure

```text
Sapphire_IQ_Supermart_Dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
└── data/
    └── Supermart Grocery Sales - Retail Analytics Dataset.csv
```

## Deployment

### Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload this project.
3. Open Streamlit Community Cloud.
4. Select the repository and `app.py`.
5. Deploy.

No database or environment variables are required for the included dataset.

## Notes

The dashboard calculates metrics from the currently selected filters, so management can move from a portfolio-level view to a specific category, region, year or date range without changing the code.
