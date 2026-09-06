import json
from pathlib import Path
import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

SAVE_FILE = Path("portfolio_state.json")

st.set_page_config(page_title="Portfolio Tracker", layout="wide")

if "portfolio_text" not in st.session_state:
    st.session_state.portfolio_text = "AAPL:10:150\nMSFT:5:320"
if "period" not in st.session_state:
    st.session_state.period = "6mo"

if SAVE_FILE.exists() and not st.session_state.get("loaded"):
    try:
        data = json.loads(SAVE_FILE.read_text("utf-8").strip())
        st.session_state.portfolio_text = data.get("portfolio_text", st.session_state.portfolio_text)
        st.session_state.period = data.get("period", st.session_state.period)
    except Exception:
        pass
    st.session_state.loaded = True

st.title("Portfolio Tracker")

text_input = st.text_area(
    "Holdings (TICKER:SHARES:BUY_PRICE)",
    key="portfolio_text",
    height=120,
)
selected_period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"], key="period")

SAVE_FILE.write_text(
    json.dumps({"portfolio_text": text_input, "period": selected_period}),
    encoding="utf-8",
)

holdings = {}
errors = []

for line_num, line in enumerate(text_input.splitlines(), 1):
    line = line.strip()
    if not line:
        continue

    parts = [p.strip() for p in line.split(":") if p.strip()]
    if len(parts) != 3:
        errors.append(f"Line {line_num}: invalid format (expected TICKER:SHARES:BUY_PRICE)")
        continue

    ticker, shares_str, price_str = parts
    ticker = ticker.upper()

    try:
        shares = float(shares_str)
        buy_price = float(price_str)
        if shares <= 0 or buy_price <= 0:
            raise ValueError
        holdings[ticker] = {"shares": shares, "buy_price": buy_price}
    except ValueError:
        errors.append(f"Line {line_num}: shares and price must be positive numbers")

if errors:
    for err in errors:
        st.warning(err)

if holdings:
    tickers = list(holdings.keys())
    
    hist_data = yf.download(tickers, period=selected_period, progress=False)["Close"]
    
    if isinstance(hist_data, pd.Series):
        hist_data = hist_data.to_frame(name=tickers[0])

    valid_tickers = [t for t in tickers if t in hist_data.columns and not hist_data[t].dropna().empty]
    invalid_tickers = set(tickers) - set(valid_tickers)
    
    for t in invalid_tickers:
        st.warning(f"Ticker '{t}' was not found or has no price data.")

    if valid_tickers:
        ts_df = pd.DataFrame(index=hist_data.index)
        total_invested = 0.0
        total_value = 0.0

        for t in valid_tickers:
            shares = holdings[t]["shares"]
            buy_price = holdings[t]["buy_price"]
            
            ts_df[t] = hist_data[t] * shares
            
            latest_price = hist_data[t].dropna().iloc[-1]
            total_invested += shares * buy_price
            total_value += shares * latest_price

        ts_df["Total"] = ts_df.sum(axis=1)
        pnl = total_value - total_invested
        pnl_pct = (pnl / total_invested * 100) if total_invested > 0 else 0.0

        st.subheader("Portfolio Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Invested", f"${total_invested:,.2f}")
        c2.metric("Current Value", f"${total_value:,.2f}")
        c3.metric("Unrealized P&L", f"${pnl:,.2f}", f"{pnl_pct:+.2f}%")

        st.subheader("Performance")
        st.line_chart(ts_df["Total"])
else:
    st.info("Enter at least one valid holding to display portfolio metrics.")

st.markdown("---")
st.subheader("Market News")

try:
    feed = feedparser.parse("https://finance.yahoo.com/news/rssindex")
    articles = feed.entries[:6]

    for i in range(0, len(articles), 2):
        col1, col2 = st.columns(2)
        for col, article in zip([col1, col2], articles[i:i+2]):
            with col:
                img_url = None
                if "media_thumbnail" in article:
                    img_url = article.media_thumbnail[0]["url"]
                
                img_col, text_col = st.columns([1, 2])
                with img_col:
                    if img_url:
                        st.image(img_url, use_container_width=True)
                with text_col:
                    st.markdown(f"**[{article.title}]({article.link})**")
                    if "published" in article:
                        st.caption(article.published)
except Exception:
    st.caption("Unable to load news feed at this time.")
