import streamlit as st
import psxdata
import math
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="PSX SIP Pro Calculator", page_icon="📈", layout="wide")

st.title("📈 PSX Smart SIP & Wealth Builder")
st.markdown("**Live Stock Allocation + Long-Term Compounding Projection**")

# --- Sidebar Inputs (SIP Fundamentals) ---
st.sidebar.header("⚙️ SIP Parameters")
budget = st.sidebar.number_input("Mahana SIP Budget (Rs):", min_value=1000, value=50000, step=1000)
years = st.sidebar.slider("Investment Duration (Years):", min_value=1, max_value=30, value=10)
# Expected combined return (Capital Gain + Dividend Yield)
expected_return_pct = st.sidebar.slider("Expected Annual Return (%):", min_value=5, max_value=35, value=18)

# --- Portfolio Configuration (Weights & Est. Dividend Yields) ---
portfolio = {
    "MEBL":  {"weight": 0.25, "yield_pct": 10.5}, # High Growth, Good Dividend
    "EFERT": {"weight": 0.25, "yield_pct": 18.0}, # Super High Dividend
    "HUBC":  {"weight": 0.20, "yield_pct": 19.5}, # Super High Dividend
    "FABL":  {"weight": 0.15, "yield_pct": 14.0}, # Growth + Dividend
    "GLAXO": {"weight": 0.15, "yield_pct": 5.0}   # Defensive / Stability
}

# --- Section 1: Live Market Allocation ---
st.header("🛒 1. Aaj Ki Live Kharidari (Monthly Allocation)")
if st.button("Fetch Live Prices & Calculate 🚀", type="primary"):
    with st.spinner("📡 PSX Screener se LIVE market data laya ja raha hai..."):
        try:
            market_data = psxdata.screener()
            
            total_spent = 0
            results = []
            
            for symbol, info in portfolio.items():
                weight = info["weight"]
                div_yield = info["yield_pct"]
                
                stock_row = market_data[market_data['symbol'] == symbol]
                
                if not stock_row.empty:
                    possible_columns = ['price', 'current', 'close', 'ldcp']
                    live_price = None
                    for col in possible_columns:
                        if col in stock_row.columns:
                            live_price = float(stock_row.iloc[0][col])
                            break
                    
                    if live_price and live_price > 0:
                        allocated_amount = budget * weight
                        shares_to_buy = math.floor(allocated_amount / live_price)
                        cost = shares_to_buy * live_price
                        total_spent += cost
                        
                        results.append({
                            "Symbol": symbol,
                            "Allocation": f"{int(weight*100)}%",
                            "Est. Div Yield": f"{div_yield}%",
                            "Live Rate (Rs)": f"{live_price:,.2f}",
                            "Shares": shares_to_buy,
                            "Cost (Rs)": f"{cost:,.2f}"
                        })
                    else:
                        st.warning(f"⚠️ {symbol}: Rate nahi mila.")
                else:
                    st.warning(f"❌ {symbol}: Market data mein nahi mila.")
                    
            if results:
                st.success("✅ Live Data Fetched Successfully!")
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric(label="Total Budget", value=f"Rs {budget:,.0f}")
                c2.metric(label="Total Kharidari", value=f"Rs {total_spent:,.0f}")
                c3.metric(label="Baqi Bachat (Cash)", value=f"Rs {budget - total_spent:,.0f}")
                
        except Exception as e:
            st.error(f"❌ Data fetch karne mein masla aaya: {e}")

st.markdown("---")

# --- Section 2: SIP Fundamentals & Projection ---
st.header("🌱 2. SIP Compounding Jadoo (Future Wealth)")
st.markdown(f"Agar aap **Rs {budget:,}** har mahine **{years} saal** tak invest karein, aur Prafits ko dobara invest (Reinvest) karein:")

# SIP Calculation Formula (Future Value of Annuity)
P = budget
r = (expected_return_pct / 100) / 12  # Monthly interest rate
n = years * 12 # Total months

projection_data = []
cumulative_investment = 0

for month in range(1, n + 1):
    cumulative_investment += P
    # Future Value formula
    future_value = P * (((1 + r)**month - 1) / r) * (1 + r)
    
    # Saal ke aakhir ka data graph ke liye save karna
    if month % 12 == 0: 
        year_num = month // 12
        projection_data.append({
            "Year": f"Year {year_num}",
            "Invested Amount": cumulative_investment,
            "Future Wealth": future_value
        })

df_proj = pd.DataFrame(projection_data)
df_proj.set_index("Year", inplace=True)

# Display Projection Metrics
final_invested = df_proj["Invested Amount"].iloc[-1]
final_wealth = df_proj["Future Wealth"].iloc[-1]
total_profit = final_wealth - final_invested

col_a, col_b, col_c = st.columns(3)
col_a.metric("Total Invested (Aap ki jaib se)", f"Rs {final_invested:,.0f}")
col_b.metric("Estimated Profit (Compounding)", f"Rs {total_profit:,.0f}")
col_c.metric("Future Portfolio Value", f"Rs {final_wealth:,.0f}", delta=f"In {years} Years")

# Draw the Chart
st.area_chart(df_proj)

st.caption(f"📝 **Note:** Yeh calculation {expected_return_pct}% expected annual return (Capital Gain + Dividend) par mabni hai. PSX ki top dividend companies historically 15% se 20% return easily generate karti hain.")

# --- Disclaimer ---
st.markdown("---")
st.caption("⚠️ **Disclaimer:** This application is for educational and informational purposes only. This does NOT constitute financial advice. Stock market investments are subject to market risks. Please do your own research (DYOR) or consult a certified financial advisor before making any investment decisions.")
