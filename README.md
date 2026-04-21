# Weyland-Yutani Multi-Mine Analytics Portal

This is an analytics platform designed to monitor the performance of mining operations. The system automatically fetches data from Google Sheets, performs statistical analysis, and visualizes key performance indicators.

## 🚀 Key Features

* **Multi-Mine Tracking:** A centralized portal to analyze different locations (e.g., LV-426, Fiorina 161, Origae-6).
* **Statistical Metrics:** Automatic calculation of Mean, Median, Standard Deviation, and Interquartile Range (IQR).
* **Advanced Anomaly Detection:** Identifies irregular operations using four robust methods:
    * **Z-score:** Standard deviation-based detection.
    * **Moving Average Distance:** Detection based on deviation from the local trend.
    * **Grubbs' Test:** Statistical identification of extreme outliers.
    * **IQR Rule:** Distribution-based filtering.
* **Interactive Charts:** Support for line and bar charts with customizable polynomial trendlines (degrees 1-4).
* **PDF Reporting:** Generate and download professional analysis reports with one click.

## 🛠 Technical Stack

* **Language:** Python 3.11+
* **Web Framework:** Streamlit
* **Data Processing:** Pandas, NumPy, SciPy
* **Visualization:** Plotly
* **Reporting:** FPDF

