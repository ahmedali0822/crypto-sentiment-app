import streamlit as st
import praw
import pandas as pd
from textblob import TextBlob
import requests
import datetime
import plotly.graph_objs as go
import os
import time
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential

# ==============================================
# CUSTOM FRONTEND COMPONENTS
# ==============================================
def inject_custom_css():
    """Inject premium custom CSS"""
    st.markdown("""
    <style>
    /* Main app styling */
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --dark: #1e293b;
        --light: #f8fafc;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
    }
    
    /* Modern glass morphism effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15) !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Animated gradient background */
    .gradient-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Custom buttons */
    .stButton>button {
        border: none !important;
        background: linear-gradient(to right, var(--primary), var(--secondary)) !important;
        color: white !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Custom tabs */
    .stTabs [role="tablist"] {
        gap: 8px !important;
    }
    
    .stTabs [role="tab"] {
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--primary);
        border-radius: 4px;
    }
    
    /* Custom tooltips */
    [data-tooltip] {
        position: relative;
    }
    
    [data-tooltip]:hover:after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--dark);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-size: 0.875rem;
        white-space: nowrap;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

def inject_custom_js():
    """Inject custom JavaScript for animations and interactions"""
    st.components.v1.html("""
    <script>
    // Smooth scroll to sections
    document.addEventListener('DOMContentLoaded', function() {
        // Add animation class when elements come into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-fade-in');
                }
            });
        }, { threshold: 0.1 });
        
        document.querySelectorAll('.glass-card').forEach(card => {
            observer.observe(card);
        });
        
        // Add click effects to buttons
        document.querySelectorAll('.stButton>button').forEach(button => {
            button.addEventListener('click', function() {
                this.classList.add('animate-pulse');
                setTimeout(() => {
                    this.classList.remove('animate-pulse');
                }, 300);
            });
        });
    });
    
    // Custom notification system
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    }
    </script>
    """, height=0)

def create_navigation():
    """Create custom navigation bar"""
    st.markdown("""
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo">📊</span>
            <span class="title">Crypto Pulse Pro</span>
        </div>
        <div class="nav-links">
            <a href="#analysis" class="nav-link">Analysis</a>
            <a href="#market" class="nav-link">Market</a>
            <a href="#insights" class="nav-link">Insights</a>
        </div>
    </nav>
    
    <style>
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        position: sticky;
        top: 0;
        z-index: 1000;
        margin-bottom: 2rem;
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .logo {
        font-size: 1.5rem;
    }
    
    .title {
        font-size: 1.25rem;
        font-weight: 600;
        background: linear-gradient(to right, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .nav-links {
        display: flex;
        gap: 1.5rem;
    }
    
    .nav-link {
        color: white;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================
# APP INITIALIZATION
# ==============================================
st.set_page_config(
    page_title="Crypto Pulse Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# Inject custom frontend components
inject_custom_css()
inject_custom_js()
create_navigation()

# ==============================================
# API CLIENT SETUP
# ==============================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def initialize_reddit():
    """Initialize and verify Reddit API connection"""
    try:
        reddit = praw.Reddit(
        client_id=st.secrets["REDDIT_CLIENT_ID"],
        client_secret=st.secrets["REDDIT_CLIENT_SECRET"],
        user_agent=st.secrets["REDDIT_USER_AGENT"]
        )
        reddit.read_only = True

        # Test connection
        if not reddit.user.me():
            raise Exception("Reddit authentication failed")
        return reddit
    except Exception as e:
        st.error(f"🔴 Reddit API Error: {str(e)}")
        st.stop()

reddit = initialize_reddit()

# ==============================================
# UTILITY FUNCTIONS
# ==============================================
def rate_limited(max_per_second):
    """Decorator to limit function call rate"""
    min_interval = 1.0 / max_per_second
    def decorator(func):
        last_time_called = 0.0
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            nonlocal last_time_called
            elapsed = time.time() - last_time_called
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            last_time_called = time.time()
            return func(*args, **kwargs)
        return rate_limited_function
    return decorator

# ==============================================
# DATA FETCHING FUNCTIONS
# ==============================================
@st.cache_data(ttl=3600, show_spinner="Fetching coin list...")
@rate_limited(1)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_all_coins():
    """Fetch list of all cryptocurrencies from CoinGecko"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/list",
            timeout=10
        )
        response.raise_for_status()
        return {coin["id"]: coin["symbol"] for coin in response.json()}
    except Exception as e:
        st.error(f"Failed to fetch coins: {str(e)}")
        return {}

@st.cache_data(ttl=600, show_spinner="Fetching coin data...")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_coin_info(coin_id):
    """Fetch detailed information for a specific coin"""
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch info for {coin_id}: {str(e)}")
        return None

@st.cache_data(ttl=300, show_spinner="Loading market data...")
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_market_data(coin_id, days):
    """Fetch historical price data for a coin"""
    try:
        response = requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
            params={
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json().get("prices", [])
        if data:
            dates, prices = zip(*[
                (datetime.datetime.fromtimestamp(d / 1000), p) 
                for d, p in data
            ])
            return dates, prices
        return [], []
    except Exception as e:
        st.error(f"Failed to fetch market data: {str(e)}")
        return [], []

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def fetch_reddit_comments(coin_symbol, limit=50):
    """Fetch Reddit comments mentioning the cryptocurrency"""
    try:
        comments = []
        for submission in reddit.subreddit("cryptocurrency").hot(limit=10):
            submission.comments.replace_more(limit=0)
            comments.extend(
                c.body for c in submission.comments.list() 
                if coin_symbol.lower() in c.body.lower()
            )
            if len(comments) >= limit:
                break
        return comments[:limit]
    except Exception as e:
        st.error(f"Reddit error: {str(e)}")
        return []

# ==============================================
# ANALYSIS FUNCTIONS
# ==============================================
def analyze_comments(comments):
    """Perform sentiment analysis on Reddit comments"""
    if not comments:
        return 0
        
    analysis = pd.DataFrame({
        "Comment": comments,
        "Polarity": [TextBlob(c).sentiment.polarity for c in comments]
    })
    analysis["Sentiment"] = analysis["Polarity"].apply(
        lambda x: "Positive 😊" if x > 0 else ("Negative 😔" if x < 0 else "Neutral 😐")
    )
    
    st.dataframe(
        analysis,
        column_config={
            "Comment": "Reddit Comment",
            "Polarity": st.column_config.NumberColumn(
                "Sentiment Score",
                format="%.2f",
                help="Range from -1 (negative) to 1 (positive)"
            ),
            "Sentiment": "Analysis"
        },
        hide_index=True,
        use_container_width=True
    )
    
    return analysis["Polarity"].mean()

def provide_investment_advice(score):
    """Generate investment advice based on sentiment score"""
    if score > 0.1:
        st.success("🎉 Strong positive sentiment! Potentially good buying opportunity.")
    elif score > 0:
        st.info("👍 Moderately positive sentiment. Consider buying with caution.")
    elif score < -0.1:
        st.error("⚠️ Strong negative sentiment! Consider waiting or selling.")
    elif score < 0:
        st.warning("👎 Moderately negative sentiment. Be cautious with investments.")
    else:
        st.warning("🔍 Neutral sentiment. Monitor the market before deciding.")

# ==============================================
# UI COMPONENTS
# ==============================================
def display_coin_info(info):
    """Display coin information in a structured format"""
    if not info:
        return
        
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f"{info['name']} ({info['symbol'].upper()})")
        st.metric(
            "Current Price", 
            f"${info['market_data']['current_price']['usd']:,.2f}",
            f"{info['market_data']['price_change_percentage_24h']:+.2f}%"
        )
        st.metric(
            "Market Cap", 
            f"${info['market_data']['market_cap']['usd']:,.2f}"
        )
        
    with col2:
        st.markdown(f"**Description**: {info['description']['en'][:500]}...")
        st.markdown(f"**Official Website**: {info['links']['homepage'][0]}")

def display_price_chart(dates, prices, coin_name, time_period):
    """Display interactive price chart"""
    if not dates or not prices:
        return
        
    fig = go.Figure(
        data=[go.Scatter(
            x=dates, 
            y=prices, 
            mode='lines+markers',
            line=dict(color='#00cc96'),
            hovertemplate='Date: %{x|%b %d, %Y}<br>Price: $%{y:,.2f}<extra></extra>'
        )]
    )
    
    fig.update_layout(
        title=f"{coin_name} Price Over {time_period}",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ==============================================
# MAIN APP LOGIC
# ==============================================
def main():
    """Main app function with enhanced UI"""
    st.markdown('<div class="gradient-bg"></div>', unsafe_allow_html=True)
    
    # Hero section
    with st.container():
        st.markdown("""
        <div class="glass-card animate-fade-in" style="margin-top: 2rem;">
            <h1 style="color: white; margin-bottom: 0.5rem;">📊 Crypto Pulse Pro</h1>
            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1.5rem;">
                Real-time sentiment analysis and market insights for cryptocurrency investors
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            with st.container():
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.header("🔍 Coin Selector")
                
                # Load coin list
                coins = fetch_all_coins()
                if not coins:
                    st.error("Failed to load cryptocurrency list")
                    st.stop()
                    
                selected_coin = st.selectbox(
                    "Select Cryptocurrency",
                    options=list(coins.keys()),
                    format_func=lambda x: f"{x} ({coins[x].upper()})",
                    key="coin_select"
                )
                
                time_period = st.selectbox(
                    "Time Period",
                    options=["1 Day", "7 Days", "30 Days", "90 Days", "180 Days", "1 Year"],
                    key="time_select"
                )
                
                time_mapping = {
                    "1 Day": 1, "7 Days": 7, "30 Days": 30,
                    "90 Days": 90, "180 Days": 180, "1 Year": 365
                }
                
                target_price = st.number_input(
                    "Set Price Alert",
                    min_value=0.0,
                    step=1.0,
                    key="price_alert"
                )
                
                if st.button("Analyze Sentiment", key="analyze_btn"):
                    st.session_state.analyze_clicked = True
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if st.session_state.get('analyze_clicked', False):
                coin_symbol = coins[selected_coin]
                
                # Coin information card
                with st.container():
                    st.markdown('<div class="glass-card" id="analysis">', unsafe_allow_html=True)
                    st.header("📈 Coin Overview")
                    
                    with st.spinner("Loading coin information..."):
                        coin_info = fetch_coin_info(selected_coin)
                        if coin_info:
                            display_coin_info(coin_info)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Sentiment analysis card
                with st.container():
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.header("🧠 Sentiment Analysis")
                    
                    with st.spinner("Analyzing Reddit discussions..."):
                        comments = fetch_reddit_comments(coin_symbol)
                        if comments:
                            score = analyze_comments(comments)
                            provide_investment_advice(score)
                        else:
                            st.warning(f"No recent Reddit comments found mentioning {coin_symbol.upper()}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Market data card
                with st.container():
                    st.markdown('<div class="glass-card" id="market">', unsafe_allow_html=True)
                    st.header("📊 Market Data")
                    
                    with st.spinner("Loading price data..."):
                        dates, prices = fetch_market_data(
                            selected_coin, 
                            time_mapping[time_period]
                        )
                        if dates and prices:
                            display_price_chart(dates, prices, coin_info['name'], time_period)
                            
                            # Price alert check
                            current_price = prices[-1] if prices else 0
                            if current_price >= target_price > 0:
                                st.success(f"🚨 Price alert! {coin_symbol.upper()} reached ${target_price:,.2f}")
                            elif current_price <= target_price > 0:
                                st.warning(f"⚠️ Price alert! {coin_symbol.upper()} dropped below ${target_price:,.2f}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <footer style="text-align: center; margin-top: 3rem; padding: 1.5rem; color: rgba(255, 255, 255, 0.6);">
        <p>© 2023 Crypto Pulse Pro | Powered by Streamlit</p>
    </footer>
    """, unsafe_allow_html=True)

# ==============================================
# RUN THE APP
# ==============================================
if __name__ == "__main__":
    main()
