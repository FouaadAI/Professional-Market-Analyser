"""
╔══════════════════════════════════════════════════════════════╗
║          K1NG QUANTUM ULTIMATE – PRO MAX TRADING PLATFORM    ║
║          Version 2.0 – 2026 kompatibel                       ║
║          Streamlit · Gemini 2.5 Flash · Binance · CoinGecko  ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─── IMPORTS ────────────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
from typing import Dict, Any, Optional, List

# TA-Lib Indikatoren
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

# Gemini (google-genai >= 1.0.0)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# ─── SEITEN-KONFIGURATION ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K1NG QUANTUM ULTIMATE",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── GLOBALES CSS & DESIGN ───────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap');

  /* ── Hintergrund & Basis ── */
  html, body, [data-testid="stAppViewContainer"] {
      background: #080818 !important;
      color: #dde0f0 !important;
  }
  [data-testid="stAppViewContainer"] {
      background:
          radial-gradient(ellipse 80% 40% at 50% 0%, #0d0d2b 0%, transparent 70%),
          radial-gradient(ellipse 60% 30% at 80% 80%, #0a1a0a 0%, transparent 60%),
          #080818 !important;
  }
  [data-testid="stHeader"] { background: transparent !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0a0a1e 0%, #0d0d1a 100%) !important;
      border-right: 1px solid #1e1e3f !important;
  }
  [data-testid="stSidebar"] * { color: #c8cce8 !important; }
  [data-testid="stSidebar"] .stTextInput input,
  [data-testid="stSidebar"] .stSelectbox select {
      background: #12122a !important;
      border: 1px solid #2a2a5e !important;
      color: #e0e4ff !important;
      border-radius: 8px !important;
  }

  /* ── Haupt-Titel ── */
  .king-header {
      font-family: 'Orbitron', monospace;
      font-size: 2.2rem;
      font-weight: 900;
      background: linear-gradient(135deg, #FFD700 0%, #FFA500 40%, #FF6B00 70%, #FFD700 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      text-align: center;
      letter-spacing: 4px;
      text-shadow: none;
      margin-bottom: 0;
      animation: shimmer 3s ease-in-out infinite;
  }
  @keyframes shimmer {
      0%,100% { filter: brightness(1); }
      50%      { filter: brightness(1.3) drop-shadow(0 0 8px #FFD70066); }
  }
  .king-subtitle {
      font-family: 'Share Tech Mono', monospace;
      font-size: 0.75rem;
      color: #6060a0;
      text-align: center;
      letter-spacing: 8px;
      margin-top: 2px;
  }

  /* ── Metrik-Karten ── */
  .metric-card {
      background: linear-gradient(135deg, #10102a 0%, #12122e 100%);
      border: 1px solid #1e1e42;
      border-left: 4px solid #FFD700;
      border-radius: 12px;
      padding: 16px 20px;
      margin: 6px 0;
      box-shadow: 0 4px 20px #00000060;
      transition: transform 0.2s, box-shadow 0.2s;
  }
  .metric-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 30px #FFD70020;
  }
  .metric-label {
      font-family: 'Share Tech Mono', monospace;
      font-size: 0.65rem;
      color: #7070a0;
      letter-spacing: 3px;
      text-transform: uppercase;
  }
  .metric-value {
      font-family: 'Orbitron', monospace;
      font-size: 1.5rem;
      font-weight: 700;
      color: #FFD700;
      line-height: 1.2;
  }
  .metric-change-pos { color: #00e676; font-size: 0.8rem; font-family: 'Rajdhani'; }
  .metric-change-neg { color: #ff5252; font-size: 0.8rem; font-family: 'Rajdhani'; }

  /* ── Preis-Ticker ── */
  .price-ticker {
      background: linear-gradient(135deg, #0c1020 0%, #101828 100%);
      border: 1px solid #1e2a3a;
      border-top: 3px solid #00bcd4;
      border-radius: 12px;
      padding: 18px 22px;
      text-align: center;
  }
  .price-symbol {
      font-family: 'Orbitron', monospace;
      font-size: 0.9rem;
      color: #00bcd4;
      letter-spacing: 3px;
  }
  .price-val {
      font-family: 'Orbitron', monospace;
      font-size: 2rem;
      font-weight: 900;
      color: #ffffff;
  }

  /* ── AI-Analyse-Ausgabe ── */
  .analysis-box {
      background: linear-gradient(135deg, #0a0f1e 0%, #0d1420 100%);
      border: 1px solid #1a2a4a;
      border-left: 4px solid #4CAF50;
      border-radius: 12px;
      padding: 20px 24px;
      font-family: 'Rajdhani', sans-serif;
      font-size: 0.95rem;
      line-height: 1.7;
      color: #c8d8f0;
      white-space: pre-wrap;
      max-height: 600px;
      overflow-y: auto;
  }

  /* ── Buttons ── */
  .stButton > button {
      background: linear-gradient(135deg, #b8860b 0%, #FFD700 50%, #b8860b 100%) !important;
      color: #080818 !important;
      font-family: 'Orbitron', monospace !important;
      font-weight: 700 !important;
      font-size: 0.75rem !important;
      letter-spacing: 2px !important;
      border: none !important;
      border-radius: 8px !important;
      padding: 10px 20px !important;
      transition: all 0.3s !important;
      box-shadow: 0 4px 15px #FFD70030 !important;
  }
  .stButton > button:hover {
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 25px #FFD70060 !important;
      filter: brightness(1.15) !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
      background: #0c0c1e !important;
      border-bottom: 2px solid #1e1e42 !important;
      gap: 4px;
  }
  .stTabs [data-baseweb="tab"] {
      font-family: 'Orbitron', monospace !important;
      font-size: 0.7rem !important;
      color: #5050a0 !important;
      letter-spacing: 2px !important;
      padding: 10px 20px !important;
  }
  .stTabs [aria-selected="true"] {
      color: #FFD700 !important;
      border-bottom: 2px solid #FFD700 !important;
      background: transparent !important;
  }

  /* ── Trennlinien & Divider ── */
  hr { border-color: #1e1e42 !important; }

  /* ── Select/Input ── */
  .stSelectbox select, .stNumberInput input, .stTextInput input {
      background: #10102a !important;
      border: 1px solid #2020448 !important;
      color: #e0e4ff !important;
      border-radius: 8px !important;
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #080818; }
  ::-webkit-scrollbar-thumb { background: #2a2a5e; border-radius: 3px; }

  /* ── Status-Badge ── */
  .status-live {
      display: inline-block;
      background: #003300;
      color: #00e676;
      font-family: 'Share Tech Mono', monospace;
      font-size: 0.65rem;
      padding: 2px 8px;
      border-radius: 4px;
      border: 1px solid #00e67660;
      letter-spacing: 2px;
      animation: pulse-green 2s infinite;
  }
  @keyframes pulse-green {
      0%,100% { box-shadow: 0 0 4px #00e67640; }
      50%      { box-shadow: 0 0 10px #00e67680; }
  }

  /* ── Signal-Box ── */
  .signal-long  { border-left-color: #00e676 !important; }
  .signal-short { border-left-color: #ff5252 !important; }
  .signal-neutral { border-left-color: #FFD700 !important; }

  /* ── Backtesting ── */
  .bt-profit { color: #00e676; font-family: 'Orbitron'; font-weight: 700; }
  .bt-loss   { color: #ff5252; font-family: 'Orbitron'; font-weight: 700; }

</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ── HILFSFUNKTIONEN & API-CALLS ──────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def fetch_global_metrics() -> Dict[str, Any]:
    """CoinGecko Global: MarketCap, Volume, BTC-Dominance (Cache 5 Min)."""
    result = {
        "market_cap": 0.0, "market_cap_change": 0.0,
        "volume_24h": 0.0, "btc_dominance": 0.0
    }
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=8,
            headers={"Accept": "application/json"}
        )
        if r.status_code == 200:
            d = r.json().get("data", {})
            result["market_cap"] = d.get("total_market_cap", {}).get("usd", 0)
            result["market_cap_change"] = d.get("market_cap_change_percentage_24h_usd", 0)
            result["volume_24h"] = d.get("total_volume", {}).get("usd", 0)
            result["btc_dominance"] = d.get("market_cap_percentage", {}).get("btc", 0)
    except Exception:
        pass
    return result


@st.cache_data(ttl=300)
def fetch_fear_greed() -> Dict[str, Any]:
    """Fear & Greed Index von alternative.me (Cache 5 Min)."""
    result = {"value": 50, "label": "Neutral"}
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=6)
        if r.status_code == 200:
            data = r.json().get("data", [{}])[0]
            result["value"] = int(data.get("value", 50))
            result["label"] = data.get("value_classification", "Neutral")
    except Exception:
        pass
    return result


@st.cache_data(ttl=10)
def fetch_live_prices(symbols: List[str]) -> Dict[str, float]:
    """Binance REST: Aktuelle Preise (Cache 10 Sek)."""
    prices: Dict[str, float] = {}
    for sym in symbols:
        try:
            r = requests.get(
                f"https://api.binance.com/api/v3/ticker/price?symbol={sym}",
                timeout=5
            )
            if r.status_code == 200:
                prices[sym] = float(r.json().get("price", 0))
        except Exception:
            prices[sym] = 0.0
    return prices


@st.cache_data(ttl=120)
def fetch_klines(symbol: str, interval: str = "1h", limit: int = 200) -> pd.DataFrame:
    """Binance Kerzendaten (Cache 2 Min)."""
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
            timeout=10
        )
        if r.status_code != 200:
            return pd.DataFrame()
        raw = r.json()
        df = pd.DataFrame(raw, columns=[
            "open_time","open","high","low","close","volume",
            "close_time","qav","trades","tbbav","tbqav","ignore"
        ])
        for col in ["open","high","low","close","volume"]:
            df[col] = pd.to_numeric(df[col])
        df["time"] = pd.to_datetime(df["open_time"], unit="ms")
        return df[["time","open","high","low","close","volume"]].reset_index(drop=True)
    except Exception:
        return pd.DataFrame()


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Berechne RSI, MACD, Bollinger Bänder, EMA."""
    if df.empty or len(df) < 30:
        return df
    close = df["close"]
    # RSI
    df["rsi"] = RSIIndicator(close, window=14).rsi()
    # MACD
    macd_obj = MACD(close)
    df["macd"]        = macd_obj.macd()
    df["macd_signal"] = macd_obj.macd_signal()
    df["macd_hist"]   = macd_obj.macd_diff()
    # Bollinger
    bb = BollingerBands(close, window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_mid"]   = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()
    # EMAs
    df["ema20"]  = EMAIndicator(close, window=20).ema_indicator()
    df["ema50"]  = EMAIndicator(close, window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close, window=200).ema_indicator()
    return df


def format_number(n: float, decimals: int = 2, suffix: str = "") -> str:
    """Formatiere große Zahlen mit T/B/M Suffix."""
    if n >= 1e12:
        return f"${n/1e12:.{decimals}f}T{suffix}"
    elif n >= 1e9:
        return f"${n/1e9:.{decimals}f}B{suffix}"
    elif n >= 1e6:
        return f"${n/1e6:.{decimals}f}M{suffix}"
    else:
        return f"${n:,.{decimals}f}{suffix}"


def send_telegram(token: str, chat_id: str, text: str) -> bool:
    """Telegram Nachricht senden."""
    if not token or not chat_id:
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text[:4096],
            "parse_mode": "HTML"
        }
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception:
        return False


def fng_color(value: int) -> str:
    """Farbe für Fear & Greed Index."""
    if value <= 25:
        return "#ff5252"
    elif value <= 45:
        return "#ff9800"
    elif value <= 55:
        return "#FFD700"
    elif value <= 75:
        return "#8bc34a"
    else:
        return "#00e676"


# ═══════════════════════════════════════════════════════════════════════════════
# ── CHARTS ───────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def build_candlestick_chart(df: pd.DataFrame, symbol: str) -> go.Figure:
    """Candlestick + Bollinger Bänder + EMAs."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2],
        vertical_spacing=0.03,
        subplot_titles=(f"{symbol} – 1H Kerzenchart", "RSI (14)", "MACD")
    )

    # ── Candlestick ──
    fig.add_trace(go.Candlestick(
        x=df["time"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        name="OHLC",
        increasing_line_color="#00e676",
        decreasing_line_color="#ff5252",
        increasing_fillcolor="#00e676",
        decreasing_fillcolor="#ff5252",
    ), row=1, col=1)

    # ── Bollinger Bänder ──
    if "bb_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["bb_upper"], name="BB Upper",
            line=dict(color="#FFD700", width=1, dash="dot"), opacity=0.7
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["bb_mid"], name="BB Mid",
            line=dict(color="#FFA500", width=1), opacity=0.8
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["bb_lower"], name="BB Lower",
            line=dict(color="#FFD700", width=1, dash="dot"),
            fill="tonexty", fillcolor="rgba(255,215,0,0.05)", opacity=0.7
        ), row=1, col=1)

    # ── EMAs ──
    if "ema20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["ema20"], name="EMA 20",
            line=dict(color="#00bcd4", width=1.5)
        ), row=1, col=1)
    if "ema50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["ema50"], name="EMA 50",
            line=dict(color="#e040fb", width=1.5)
        ), row=1, col=1)

    # ── RSI ──
    if "rsi" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["rsi"], name="RSI",
            line=dict(color="#FFD700", width=2)
        ), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ff5252", opacity=0.6, row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00e676", opacity=0.6, row=2, col=1)
        fig.add_hline(y=50, line_dash="dot",  line_color="#404060", opacity=0.4, row=2, col=1)

    # ── MACD ──
    if "macd" in df.columns:
        colors = ["#00e676" if v >= 0 else "#ff5252" for v in df["macd_hist"].fillna(0)]
        fig.add_trace(go.Bar(
            x=df["time"], y=df["macd_hist"], name="MACD Hist",
            marker_color=colors, opacity=0.8
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["macd"], name="MACD",
            line=dict(color="#2196F3", width=1.5)
        ), row=3, col=1)
        fig.add_trace(go.Scatter(
            x=df["time"], y=df["macd_signal"], name="Signal",
            line=dict(color="#ff9800", width=1.5)
        ), row=3, col=1)

    # ── Layout ──
    fig.update_layout(
        paper_bgcolor="#080818",
        plot_bgcolor="#0c0c1e",
        font=dict(family="Share Tech Mono", color="#8888b0", size=11),
        xaxis_rangeslider_visible=False,
        height=620,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(
            bgcolor="#10102a", bordercolor="#1e1e42",
            borderwidth=1, font=dict(size=10)
        ),
        hovermode="x unified"
    )
    fig.update_xaxes(
        gridcolor="#14143a", gridwidth=0.5,
        zerolinecolor="#1e1e42"
    )
    fig.update_yaxes(
        gridcolor="#14143a", gridwidth=0.5,
        zerolinecolor="#1e1e42"
    )
    # RSI Y-Achse fixieren
    fig.update_yaxes(range=[0, 100], row=2, col=1)

    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# ── BACKTESTING ──────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def run_backtest(
    df: pd.DataFrame,
    start_capital: float = 1000.0,
    rsi_oversold: float = 30.0,
    rsi_overbought: float = 70.0
) -> Dict[str, Any]:
    """
    Einfaches RSI-Backtesting: BUY wenn RSI < oversold, SELL wenn RSI > overbought.
    Gibt Endkapital, Trades, Rendite zurück.
    """
    if df.empty or "rsi" not in df.columns:
        return {"error": "Keine Daten oder RSI nicht berechnet."}

    capital    = start_capital
    in_trade   = False
    entry_price= 0.0
    trades     = []

    for _, row in df.iterrows():
        rsi   = row.get("rsi")
        price = row["close"]
        ts    = row["time"]

        if pd.isna(rsi):
            continue

        if not in_trade and rsi < rsi_oversold:
            # KAUF
            entry_price = price
            units       = capital / price
            in_trade    = True
            trades.append({
                "type": "BUY",
                "time": ts.strftime("%Y-%m-%d %H:%M"),
                "price": round(price, 4),
                "rsi": round(rsi, 1),
                "capital_before": round(capital, 2)
            })

        elif in_trade and rsi > rsi_overbought:
            # VERKAUF
            capital  = units * price
            in_trade = False
            pnl_pct  = (price - entry_price) / entry_price * 100
            trades[-1]["sell_price"] = round(price, 4)
            trades[-1]["sell_time"]  = ts.strftime("%Y-%m-%d %H:%M")
            trades[-1]["pnl_pct"]    = round(pnl_pct, 2)
            trades[-1]["capital_after"] = round(capital, 2)

    # Falls noch in offener Position am Ende
    if in_trade:
        last_price = df["close"].iloc[-1]
        capital    = units * last_price
        pnl_pct    = (last_price - entry_price) / entry_price * 100
        if trades:
            trades[-1]["sell_price"]    = round(last_price, 4)
            trades[-1]["sell_time"]     = "(offen)"
            trades[-1]["pnl_pct"]       = round(pnl_pct, 2)
            trades[-1]["capital_after"] = round(capital, 2)

    total_return = (capital - start_capital) / start_capital * 100
    closed = [t for t in trades if "pnl_pct" in t]
    wins   = [t for t in closed if t.get("pnl_pct", 0) > 0]
    win_rate = (len(wins) / len(closed) * 100) if closed else 0

    return {
        "end_capital":   round(capital, 2),
        "total_return":  round(total_return, 2),
        "trades":        trades,
        "num_trades":    len(closed),
        "win_rate":      round(win_rate, 1),
        "start_capital": start_capital
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ── GEMINI AI ANALYSE ─────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

QUANTUM_SYSTEM_PROMPT = """
Du bist K1NG ANALYST – Quantum Trading Intelligence.
STATUS: Level-9 Market Dominance | IQ: 280+
MISSION: Absolute Profitabilität durch multi-dimensionale Analyse

QUANTUM ANALYSE-PROTOKOLL:
1. 🔍 LIQUIDITÄTS-ANALYSE: Order-Cluster, Stop-Hunt-Zonen, Whale-Bewegungen
2. 📊 TECHNISCHE ANALYSE: HTF-Trend, ICT Patterns (FVG/BOS/CHoCH), RSI/MACD
3. ⚡ SIGNAL-GENERIERUNG: Entry-Zonen, 4 Take-Profit Targets, Stop-Loss, Leverage
4. 🌐 FUNDAMENTAL: News-Sentiment, On-Chain-Metriken, Institutional Flows

AUSGABE-FORMAT (STRENG EINHALTEN):
🦅 K1NG QUANTUM SIGNAL - [ASSET] 🦅

📈 LIQUIDITÄTS-ANALYSE:
• Buy-Side Liquidity: [Zone]
• Sell-Side Liquidity: [Zone]
• Liquidation-Cluster: [Long/Short Levels]
• Next HTF Liquidity: [Area]
• Stop-Hunt Zone: [Price Level]

🎯 TECHNISCHES SETUP:
• Market Structure: [Bullish/Bearish/Neutral]
• Key Level: [Support/Resistance]
• ICT Pattern: [Silver Bullet/FVG/BOS/CHoCH]
• Momentum: [RSI/MACD Direction]
• Volume Analysis: [Accumulation/Distribution]

⚡ TRADING-SIGNAL:
#[ASSET] [LONG/SHORT]
Entry: [Preisbereich]
Leverage: [3x–10x]
Target 1: [Price]
Target 2: [Price]
Target 3: [Price]
Target 4: [Price]
Stop-Loss: [Price]

📊 RISIKO-MANAGEMENT:
• Max Risk: [1–2%] Portfolio
• R/R Ratio: [1:3+]
• Position Size: [Berechnet]
• Hedge Recommendation: [Asset/Strategie]
• Break-Even Move: [Target Level]

🔮 K1NG KONFIDENZ: [XX]%
⏰ GÜLTIGKEIT: [4–12 Stunden]
🎯 WIN RATE: 85%+ Historical

Antworte IMMER auf Deutsch. Sei präzise, professionell, datengetrieben.
"""


def call_gemini(api_key: str, user_prompt: str, use_search: bool = True) -> str:
    """Gemini 2.5 Flash API-Aufruf mit optionalem Google Search Grounding."""
    if not GENAI_AVAILABLE:
        return "❌ google-genai Paket nicht installiert. Führe: pip install google-genai>=1.0.0 aus."
    if not api_key:
        return "❌ Kein Gemini API Key angegeben. Bitte im Sidebar eintragen."

    try:
        client = genai.Client(api_key=api_key)

        tools = []
        if use_search:
            try:
                tools = [types.Tool(google_search=types.GoogleSearch())]
            except Exception:
                tools = []

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=QUANTUM_SYSTEM_PROMPT,
                tools=tools if tools else None,
                temperature=0.7,
                max_output_tokens=3000,
            )
        )
        return response.text

    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "invalid" in err.lower():
            return f"❌ Ungültiger API Key: {err}"
        elif "quota" in err.lower():
            return "❌ API Quota überschritten. Bitte später nochmal versuchen."
        else:
            return f"❌ Gemini Fehler: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# ── SESSION STATE INITIALISIERUNG ────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = ""
if "selected_symbol" not in st.session_state:
    st.session_state.selected_symbol = "BTCUSDT"


# ═══════════════════════════════════════════════════════════════════════════════
# ── SIDEBAR ───────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; margin-bottom: 20px;'>
        <div style='font-family: Orbitron, monospace; font-size: 1.1rem; font-weight:900;
                    background: linear-gradient(135deg,#FFD700,#FFA500);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    letter-spacing:4px;'>🦅 K1NG</div>
        <div style='font-family: Share Tech Mono; font-size:0.6rem; color:#505090;
                    letter-spacing:4px;'>QUANTUM ULTIMATE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 API KEYS")

    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Erhalte deinen Key unter: aistudio.google.com"
    )

    st.markdown("---")
    st.markdown("### 📲 TELEGRAM")

    tg_token = st.text_input("Bot Token", type="password", placeholder="123456:ABC...")
    tg_chat  = st.text_input("Chat ID", placeholder="-100...")

    if st.button("📤 Test-Nachricht senden"):
        if send_telegram(tg_token, tg_chat, "🦅 K1NG QUANTUM ULTIMATE – Verbindung erfolgreich! ⚡"):
            st.success("✅ Telegram OK!")
        else:
            st.error("❌ Telegram Fehler – Token/ID prüfen")

    st.markdown("---")
    st.markdown("### ⚙️ EINSTELLUNGEN")

    auto_refresh = st.toggle("Auto-Refresh (30s)", value=st.session_state.auto_refresh)
    st.session_state.auto_refresh = auto_refresh

    st.markdown("""
    <div style='margin-top:20px; padding:12px; background:#0a0a1e;
                border-radius:8px; border:1px solid #1e1e42;'>
        <div style='font-family: Share Tech Mono; font-size:0.6rem; color:#505090; letter-spacing:2px;'>
            STATUS<br>
        </div>
        <span class='status-live'>● LIVE</span>
        <div style='font-family: Share Tech Mono; font-size:0.6rem; color:#505090;
                    margin-top:8px; letter-spacing:1px;'>
            Binance · CoinGecko · Gemini
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:16px; font-family: Share Tech Mono; font-size:0.55rem;
                color:#303060; text-align:center; letter-spacing:2px;'>
        ⚠️ NUR ZU BILDUNGSZWECKEN<br>KEIN FINANZIELLE BERATUNG
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ── HAUPT-HEADER ─────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='padding: 20px 0 10px 0;'>
    <div class='king-header'>🦅 K1NG QUANTUM ULTIMATE</div>
    <div class='king-subtitle'>PRO MAX · QUANTUM TRADING INTELLIGENCE · v2.0</div>
</div>
""", unsafe_allow_html=True)

now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div style='text-align:center; font-family: Share Tech Mono; font-size:0.65rem;
            color:#3a3a6a; letter-spacing:3px; margin-bottom:20px;'>
    {now_str}
</div>
""", unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# ── SEKTION 1: ECHTZEIT-MARKT-METRIKEN ──────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='font-family: Orbitron, monospace; font-size:0.8rem; color:#FFD700;
            letter-spacing:4px; margin-bottom:12px;'>
    📊 MARKT-DASHBOARD
</div>
""", unsafe_allow_html=True)

# Daten laden
with st.spinner("Lade Marktdaten..."):
    gmetrics = fetch_global_metrics()
    fng      = fetch_fear_greed()

mc_val    = gmetrics["market_cap"]
mc_change = gmetrics["market_cap_change"]
vol_val   = gmetrics["volume_24h"]
btc_dom   = gmetrics["btc_dominance"]
fng_val   = fng["value"]
fng_label = fng["label"]

arrow_mc  = "↑" if mc_change >= 0 else "↓"
cls_mc    = "metric-change-pos" if mc_change >= 0 else "metric-change-neg"
fng_color_val = fng_color(fng_val)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>💰 TOTAL MARKET CAP</div>
        <div class='metric-value'>{format_number(mc_val)}</div>
        <div class='{cls_mc}'>{arrow_mc} {abs(mc_change):.2f}% (24h)</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>📈 24H VOLUME</div>
        <div class='metric-value'>{format_number(vol_val)}</div>
        <div style='color:#5050a0; font-size:0.75rem; font-family:Rajdhani;'>Total Krypto Volumen</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>₿ BTC DOMINANCE</div>
        <div class='metric-value'>{btc_dom:.1f}%</div>
        <div style='color:#5050a0; font-size:0.75rem; font-family:Rajdhani;'>Marktanteil Bitcoin</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-label'>😱 FEAR & GREED INDEX</div>
        <div class='metric-value' style='color:{fng_color_val};'>{fng_val}</div>
        <div style='color:{fng_color_val}; font-size:0.8rem; font-family:Rajdhani;'>{fng_label}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# ── SEKTION 2: LIVE-PREIS TICKER ─────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div style='font-family: Orbitron, monospace; font-size:0.8rem; color:#00bcd4;
            letter-spacing:4px; margin-bottom:12px;'>
    ⚡ LIVE PREIS TICKER
</div>
""", unsafe_allow_html=True)

price_col1, price_col2, price_col3, price_col4 = st.columns([3, 3, 3, 2])

with st.spinner("Lade Live-Preise..."):
    live = fetch_live_prices(["BTCUSDT", "ETHUSDT", "SOLUSDT"])

btc_price = live.get("BTCUSDT", 0)
eth_price = live.get("ETHUSDT", 0)
sol_price = live.get("SOLUSDT", 0)

with price_col1:
    st.markdown(f"""
    <div class='price-ticker'>
        <div class='price-symbol'>BTC / USDT</div>
        <div class='price-val'>${btc_price:,.1f}</div>
    </div>""", unsafe_allow_html=True)

with price_col2:
    st.markdown(f"""
    <div class='price-ticker'>
        <div class='price-symbol'>ETH / USDT</div>
        <div class='price-val'>${eth_price:,.1f}</div>
    </div>""", unsafe_allow_html=True)

with price_col3:
    st.markdown(f"""
    <div class='price-ticker'>
        <div class='price-symbol'>SOL / USDT</div>
        <div class='price-val'>${sol_price:,.2f}</div>
    </div>""", unsafe_allow_html=True)

with price_col4:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
    ref_status = "🟢 AUTO" if st.session_state.auto_refresh else "⚫ MANUELL"
    st.markdown(f"""
    <div style='font-family: Share Tech Mono; font-size:0.65rem;
                color:#5050a0; text-align:center; margin-top:8px;
                letter-spacing:2px;'>{ref_status}</div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
# ── HAUPT-TABS ────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊  CHART & INDIKATOREN",
    "🎯  BACKTESTING",
    "🦅  K1NG ANALYSE",
    "📋  SIGNAL LOG"
])


# ───────────────────────────────────────────────────────────────────────────────
# TAB 1: CHART & INDIKATOREN
# ───────────────────────────────────────────────────────────────────────────────
with tab1:
    c_col1, c_col2, c_col3 = st.columns([2, 2, 2])

    with c_col1:
        chart_symbol = st.selectbox(
            "🔍 Asset auswählen",
            ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT",
             "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT"],
            index=0
        )
        st.session_state.selected_symbol = chart_symbol

    with c_col2:
        chart_interval = st.selectbox(
            "⏱ Zeitintervall",
            ["15m", "1h", "4h", "1d"],
            index=1
        )
    with c_col3:
        chart_limit = st.slider("📊 Kerzen", 50, 500, 200, step=50)

    with st.spinner(f"Lade {chart_symbol} Daten ({chart_interval})..."):
        df_chart = fetch_klines(chart_symbol, chart_interval, chart_limit)

    if df_chart.empty:
        st.warning("⚠️ Keine Kerzendaten verfügbar. Binance API möglicherweise nicht erreichbar.")
    else:
        df_chart = compute_indicators(df_chart)

        # Kurze Statistiken
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        latest = df_chart.iloc[-1]
        first  = df_chart.iloc[0]
        pct_ch = (latest["close"] - first["close"]) / first["close"] * 100
        rsi_now = latest.get("rsi", float("nan"))

        with s_col1:
            st.metric("Aktuell", f"${latest['close']:,.4f}",
                      f"{pct_ch:+.2f}% ({chart_limit} Kerzen)")
        with s_col2:
            st.metric("Hoch",  f"${df_chart['high'].max():,.4f}")
        with s_col3:
            st.metric("Tief",  f"${df_chart['low'].min():,.4f}")
        with s_col4:
            rsi_display = f"{rsi_now:.1f}" if not pd.isna(rsi_now) else "N/A"
            rsi_color   = "inverse" if (not pd.isna(rsi_now) and rsi_now > 70) else "normal"
            st.metric("RSI (14)", rsi_display)

        # Chart
        fig = build_candlestick_chart(df_chart, chart_symbol)
        st.plotly_chart(fig, width='stretch', config={
            "displayModeBar": True,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {"format": "png", "filename": f"k1ng_{chart_symbol}"}
        })

        # Rohdaten-Tabelle (optional)
        with st.expander("📋 Rohdaten anzeigen"):
            show_cols = ["time","open","high","low","close","volume","rsi","macd","bb_upper","bb_lower"]
            show_cols = [c for c in show_cols if c in df_chart.columns]
            st.dataframe(
                df_chart[show_cols].tail(50).style.format({
                    "open":"{:.4f}","high":"{:.4f}","low":"{:.4f}","close":"{:.4f}",
                    "volume":"{:,.0f}","rsi":"{:.1f}","macd":"{:.4f}",
                    "bb_upper":"{:.4f}","bb_lower":"{:.4f}"
                }),
                width='stretch'
            )


# ───────────────────────────────────────────────────────────────────────────────
# TAB 2: BACKTESTING
# ───────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div style='font-family: Orbitron; font-size:0.85rem; color:#FFD700;
                letter-spacing:3px; margin-bottom:16px;'>
        🎯 RSI BACKTESTING SIMULATOR
    </div>
    """, unsafe_allow_html=True)

    bt_col1, bt_col2, bt_col3 = st.columns(3)
    with bt_col1:
        bt_symbol  = st.selectbox("Asset", ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT"], key="bt_sym")
    with bt_col2:
        bt_capital = st.number_input("Startkapital (USDT)", min_value=100.0,
                                     max_value=1_000_000.0, value=1000.0, step=100.0)
    with bt_col3:
        bt_interval = st.selectbox("Zeitrahmen", ["15m","1h","4h","1d"], index=1, key="bt_int")

    bt_col4, bt_col5 = st.columns(2)
    with bt_col4:
        rsi_os = st.slider("RSI Oversold (Kaufen <)", 10, 50, 30, key="bt_os")
    with bt_col5:
        rsi_ob = st.slider("RSI Overbought (Verkaufen >)", 50, 90, 70, key="bt_ob")

    if st.button("▶ BACKTEST STARTEN"):
        with st.spinner("Backtesting läuft..."):
            bt_df = fetch_klines(bt_symbol, bt_interval, 500)
            if not bt_df.empty:
                bt_df = compute_indicators(bt_df)
                result = run_backtest(bt_df, bt_capital, rsi_os, rsi_ob)

                if "error" in result:
                    st.error(result["error"])
                else:
                    # Ergebnis-Metriken
                    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
                    ret_class = "bt-profit" if result["total_return"] >= 0 else "bt-loss"
                    cap_class = "bt-profit" if result["end_capital"] >= bt_capital else "bt-loss"

                    with r_col1:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>ENDKAPITAL</div>
                            <div class='{cap_class}' style='font-size:1.3rem;'>
                                ${result["end_capital"]:,.2f}
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with r_col2:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>GESAMTRENDITE</div>
                            <div class='{ret_class}' style='font-size:1.3rem;'>
                                {result["total_return"]:+.2f}%
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with r_col3:
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>ANZAHL TRADES</div>
                            <div class='metric-value'>{result["num_trades"]}</div>
                        </div>""", unsafe_allow_html=True)
                    with r_col4:
                        wc = "bt-profit" if result["win_rate"] >= 50 else "bt-loss"
                        st.markdown(f"""
                        <div class='metric-card'>
                            <div class='metric-label'>WIN RATE</div>
                            <div class='{wc}' style='font-size:1.3rem;'>
                                {result["win_rate"]}%
                            </div>
                        </div>""", unsafe_allow_html=True)

                    # Equity-Kurve
                    closed_trades = [t for t in result["trades"] if "capital_after" in t]
                    if closed_trades:
                        eq_values = [bt_capital] + [t["capital_after"] for t in closed_trades]
                        eq_labels = ["Start"] + [t.get("sell_time","?") for t in closed_trades]
                        colors_eq = ["#00e676" if v >= bt_capital else "#ff5252" for v in eq_values]

                        fig_eq = go.Figure()
                        fig_eq.add_trace(go.Scatter(
                            x=eq_labels, y=eq_values,
                            mode="lines+markers",
                            line=dict(color="#FFD700", width=2),
                            marker=dict(color=colors_eq, size=8),
                            name="Equity"
                        ))
                        fig_eq.add_hline(y=bt_capital, line_dash="dash",
                                         line_color="#5050a0", opacity=0.6)
                        fig_eq.update_layout(
                            title="📈 Equity Kurve",
                            paper_bgcolor="#080818",
                            plot_bgcolor="#0c0c1e",
                            font=dict(family="Share Tech Mono", color="#8888b0"),
                            height=250,
                            margin=dict(l=10, r=10, t=40, b=10),
                            xaxis=dict(gridcolor="#14143a"),
                            yaxis=dict(gridcolor="#14143a", tickprefix="$")
                        )
                        st.plotly_chart(fig_eq, width='stretch')

                    # Trade-Tabelle
                    if result["trades"]:
                        st.markdown("#### 📋 Trade-Liste")
                        trade_display = []
                        for t in result["trades"]:
                            if "pnl_pct" in t:
                                trade_display.append({
                                    "Kauf-Zeit":    t.get("time",""),
                                    "Kauf-Preis":   f"${t.get('price',0):,.4f}",
                                    "RSI bei Kauf": f"{t.get('rsi',0):.1f}",
                                    "Verkauf-Zeit": t.get("sell_time","offen"),
                                    "Verkauf-Preis":f"${t.get('sell_price',0):,.4f}",
                                    "PnL %":        f"{t.get('pnl_pct',0):+.2f}%",
                                    "Kapital nach": f"${t.get('capital_after',0):,.2f}"
                                })
                        if trade_display:
                            st.dataframe(pd.DataFrame(trade_display), use_container_width=True)
            else:
                st.error("❌ Keine Kerzendaten verfügbar.")


# ───────────────────────────────────────────────────────────────────────────────
# TAB 3: K1NG ANALYSE (Gemini AI)
# ───────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <div style='font-family: Orbitron; font-size:0.85rem; color:#FFD700;
                letter-spacing:3px; margin-bottom:16px;'>
        🦅 K1NG QUANTUM ANALYSE ENGINE
    </div>
    """, unsafe_allow_html=True)

    if not gemini_key:
        st.info("🔑 Bitte gib deinen **Gemini API Key** im Sidebar ein, um die KI-Analyse zu nutzen.")
        st.markdown("""
        <div style='font-family: Share Tech Mono; font-size:0.75rem; color:#5050a0;
                    padding:12px; background:#0a0a1e; border-radius:8px; border:1px solid #1e1e42;'>
            Kostenloser Key: https://aistudio.google.com/apikey<br>
            Paket benötigt: pip install google-genai>=1.0.0
        </div>
        """, unsafe_allow_html=True)
    else:
        ai_col1, ai_col2 = st.columns([2, 3])

        with ai_col1:
            analyse_type = st.radio(
                "🎯 Analyse-Typ",
                ["🌐 MARKET ANALYSIS", "🔍 LIQUIDITY SCAN", "⚡ ASSET QUANTUM SIGNAL"],
                key="analyse_type"
            )

            asset_options = ["BTCUSDT","ETHUSDT","SOLUSDT","WTI","GOLD","AAPL","MSFT","BNBUSDT","XRPUSDT"]
            signal_asset = st.selectbox("Asset für Signal", asset_options, key="sig_asset")
            use_search   = st.checkbox("🌐 Google Search Grounding", value=True)

        with ai_col2:
            custom_prompt = st.text_area(
                "Eigener Prompt (optional)",
                height=100,
                placeholder="z.B.: BTCUSDT FULL QUANTUM ANALYSIS mit aktuellem Marktkontext..."
            )

        if st.button("🦅 QUANTUM ANALYSE STARTEN", key="analyse_btn"):
            # Prompt aufbauen
            if custom_prompt.strip():
                final_prompt = custom_prompt.strip()
            elif "MARKET ANALYSIS" in analyse_type:
                final_prompt = (
                    "MARKET ANALYSIS – Führe eine vollständige globale Krypto-Marktanalyse durch. "
                    "Identifiziere die Top 3 Assets mit dem besten Setup, erkläre den aktuellen "
                    "Markttrend und gib Risikohinweise. Nutze aktuelle Daten."
                )
            elif "LIQUIDITY SCAN" in analyse_type:
                final_prompt = (
                    "LIQUIDITY SCAN BTCUSDT – Analysiere das aktuelle BTC/USDT Orderbuch. "
                    "Identifiziere Stop-Hunt-Zonen, Liquidations-Cluster, Buy/Sell-Side Liquidität "
                    "und institutionelle Order-Flow Muster. Nutze aktuelle Marktdaten."
                )
            else:
                final_prompt = (
                    f"{signal_asset} – Vollständige Quantum-Analyse. "
                    f"Erstelle ein vollständiges Trading Signal für {signal_asset} "
                    "im definierten Format mit allen 4 Targets, Stop-Loss und Risiko-Management."
                )

            with st.spinner("🦅 Quantum-Analyse läuft... (Gemini 2.5 Flash)"):
                result_text = call_gemini(gemini_key, final_prompt, use_search)

            st.session_state.last_analysis = result_text

            # Signal-Klasse bestimmen
            sig_class = "signal-neutral"
            rt_lower  = result_text.lower()
            if "long" in rt_lower and "short" not in rt_lower[:rt_lower.find("long")+50]:
                sig_class = "signal-long"
            elif "short" in rt_lower:
                sig_class = "signal-short"

            st.markdown(f"""
            <div class='analysis-box {sig_class}'>
{result_text}
            </div>
            """, unsafe_allow_html=True)

            # Telegram senden
            if tg_token and tg_chat:
                clean_text = f"🦅 K1NG QUANTUM SIGNAL\n\n{result_text}"
                if send_telegram(tg_token, tg_chat, clean_text):
                    st.success("📲 Signal wurde automatisch an Telegram gesendet!")
                else:
                    st.warning("⚠️ Telegram Versand fehlgeschlagen.")

        elif st.session_state.last_analysis:
            st.markdown("**Letzte Analyse:**")
            st.markdown(f"""
            <div class='analysis-box'>
{st.session_state.last_analysis}
            </div>
            """, unsafe_allow_html=True)


# ───────────────────────────────────────────────────────────────────────────────
# TAB 4: SIGNAL LOG
# ───────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <div style='font-family: Orbitron; font-size:0.85rem; color:#FFD700;
                letter-spacing:3px; margin-bottom:16px;'>
        📋 SIGNAL LOG & MARKTÜBERSICHT
    </div>
    """, unsafe_allow_html=True)

    # Multi-Asset Preise
    st.markdown("#### 🔢 Multi-Asset Live-Preise")
    all_syms = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT"]

    with st.spinner("Lade alle Preise..."):
        all_prices = fetch_live_prices(all_syms)

    price_data = []
    for sym, price in all_prices.items():
        price_data.append({
            "Asset": sym.replace("USDT",""),
            "Preis (USDT)": f"${price:,.4f}" if price > 0 else "N/A",
            "Pair": sym
        })

    if price_data:
        st.dataframe(
            pd.DataFrame(price_data),
            width='stretch',
            hide_index=True
        )

    st.markdown("---")
    st.markdown("#### 📜 Letztes gespeichertes Signal")

    if st.session_state.last_analysis:
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        <div style='font-family: Share Tech Mono; font-size:0.65rem;
                    color:#5050a0; letter-spacing:2px; margin-bottom:8px;'>
            ⏰ GENERIERT: {ts_now}
        </div>
        <div class='analysis-box'>
{st.session_state.last_analysis}
        </div>
        """, unsafe_allow_html=True)

        if st.button("📋 Signal kopieren / erneut senden"):
            if tg_token and tg_chat:
                send_telegram(tg_token, tg_chat, st.session_state.last_analysis)
                st.success("📲 Erneut an Telegram gesendet!")
            else:
                st.info("📋 Signal ist oben angezeigt. Telegram-Keys für automatischen Versand eintragen.")
    else:
        st.markdown("""
        <div style='font-family: Share Tech Mono; font-size:0.75rem; color:#3a3a6a;
                    text-align:center; padding:40px;'>
            Noch keine Analyse generiert.<br>
            Gehe zu → 🦅 K1NG ANALYSE → Quantum Analyse starten.
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ── FOOTER ───────────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style='text-align:center; padding:12px 0;
            font-family: Share Tech Mono; font-size:0.6rem;
            color:#2a2a5a; letter-spacing:3px;'>
    🦅 K1NG QUANTUM ULTIMATE v2.0 &nbsp;|&nbsp;
    Binance · CoinGecko · Gemini 2.5 Flash · Telegram &nbsp;|&nbsp;
    {datetime.now().strftime("%Y")} &nbsp;|&nbsp;
    ⚠️ NUR ZU BILDUNGSZWECKEN – KEIN FINANZIELLE BERATUNG
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# ── AUTO-REFRESH LOGIK ────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

#if st.session_state.auto_refresh:
   # time.sleep(30)
   # st.rerun()
