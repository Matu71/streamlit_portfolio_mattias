# Streamlit Stock Portfolio Tracker

A simple web app I built with Python and Streamlit to track my stock portfolio and see real-time price updates. 

I created this project to practice working with live data from APIs, handling user inputs, and visualizing time-series data on an interactive dashboard.

---

## Features

* **Live Market Data:** Pulls current stock prices and news using yfinance and feedparser.
* **Portfolio Valuation:** Uses Pandas to calculate total portfolio value, profits/losses, and percentage changes automatically.
* **Input Checking:** Basic error handling to make sure invalid ticker symbols or incorrect inputs don't crash the app.
* **Local Data Saving:** Saves portfolio settings locally to a JSON file so you don't lose your data when refreshing the page.
* **Simple Dashboard:** Interactive charts and metrics rendered with Streamlit.

---

## Tech Stack

* **Language:** Python
* **Data Processing:** Pandas
* **Web Framework:** Streamlit
* **APIs:** yfinance, feedparser

---

## How to Run Locally

1. **Clone this repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
   cd YOUR-REPO-NAME