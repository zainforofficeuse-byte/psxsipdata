import streamlit as st
import psxdata
import math
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="PSX SIP Calculator", page_icon="📈", layout="centered")

st.title("📈 PSX Smart SIP Calculator")
st.markdown("**Apne pasandeeda Shariah-compliant dividend stocks mein invest karein (Auto-Pilot).**")

# --- User Input ---
budget = st.number_input("Apna mahana SIP budget likhein (Rs):", min_value=1000, value=50000, step=1000)

allocations = {
    "MEBL": 0.25,
    "EFERT": 0.25,
    "HUBC": 0.20,
    "FABL": 0.15,
    "GLAXO": 0.15
}

st.markdown("---")

# --- Calculation Logic ---
if st.button("Calculate SIP 🚀", type="primary"):
    with st.spinner("📡 PSX Screener se LIVE market data laya ja raha hai..."):
        try:
            # 1 request mein puri market ka data layein (Anti-Block)
            market_data = psxdata.screener()
            
            total_spent = 0
            results = []
            
            for symbol, weight in allocations.items():
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
                            "Live Rate (Rs)": f"{live_price:,.2f}",
                            "Shares": shares_to_buy,
                            "Total Cost (Rs)": f"{cost:,.2f}"
                        })
                    else:
                        st.warning(f"⚠️ {symbol}: Rate nahi mila.")
                else:
                    st.warning(f"❌ {symbol}: Market data mein nahi mila.")
                    
            # --- Results Display ---
            if results:
                st.success("✅ Calculation Mukammal!")
                
                # Table show karna
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True, hide_index=True)
                
                st.markdown("### 💰 Final Summary")
                col1, col2, col3 = st.columns(3)
                
                col1.metric(label="Total Budget", value=f"Rs {budget:,.0f}")
                col2.metric(label="Total Kharidari", value=f"Rs {total_spent:,.0f}")
                col3.metric(label="Baqi Bachat (Cash)", value=f"Rs {budget - total_spent:,.0f}")
                
        except Exception as e:
            st.error(f"❌ Data fetch karne mein masla aaya (PSX Server Issue): {e}")
            st.info("Tip: Thori der baad dobara 'Calculate' par click karein.")