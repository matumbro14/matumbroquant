import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date as date_type

st.set_page_config(page_title="MATUMBRO QUANT", page_icon="🪝", layout="wide", initial_sidebar_state="collapsed")
if "tk" not in st.session_state: st.session_state.tk="NVDA"

QUICK_TICKERS=["NVDA","GOOG","AVGO","ORCL","QQQ","MU","MRVL","COHR","TSEM","LITE","NBIS","ASML","TCEHY","AWWE"]
# Raigor Stonehoof = Earthshaker (WC3 DotA Tauren Chieftain model)
RAIGOR="https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/earthshaker.png"
DOMAINS={"AAPL":"apple.com","MSFT":"microsoft.com","GOOGL":"google.com","GOOG":"google.com","AMZN":"amazon.com","NVDA":"nvidia.com","META":"meta.com","TSLA":"tesla.com","AVGO":"broadcom.com","NFLX":"netflix.com","AMD":"amd.com","ADBE":"adobe.com","QCOM":"qualcomm.com","INTC":"intel.com","MU":"micron.com","MRVL":"marvell.com","SMCI":"supermicro.com","CRWD":"crowdstrike.com","PANW":"paloaltonetworks.com","NET":"cloudflare.com","PLTR":"palantir.com","COIN":"coinbase.com","ARM":"arm.com","NBIS":"nebius.com","COHR":"coherent.com","LITE":"lumentum.com","QQQ":"invesco.com","TSEM":"towersemi.com","ORCL":"oracle.com","SOFI":"sofi.com","HOOD":"robinhood.com","ASML":"asml.com","TCEHY":"tencent.com","AWWE":"awwe.com"}
US_TOP=["AAPL","MSFT","GOOGL","GOOG","AMZN","NVDA","META","TSLA","AVGO","NFLX","AMD","ADBE","QCOM","INTC","TXN","AMAT","MU","LRCX","KLAC","MRVL","ON","SMCI","CRWD","PANW","DDOG","NET","SNOW","PLTR","COIN","ABNB","UBER","PYPL","SHOP","ARM","NBIS","COHR","LITE","AAOI","QQQ","SOFI","HOOD","RIVN","TSEM","SMH","SOXX","COST","MELI","ORCL","V","MA","JPM","BAC","WFC","GS","MS","UNH","JNJ","PG","HD","DIS","CRM","IBM","NOW","INTU","ISRG","LLY","PFE","MRK","ABBV","BA","RTX","LMT","GE","CAT","DE","HON","UPS","FDX","XOM","CVX","COP","SLB","NEE","SPY","IWM","DIA","VOO","VTI","ASML","TCEHY","AWWE"]

def _wl_cb():
    v=st.session_state.get("wl_radio","");t=v.replace("$","").strip()
    if t: st.session_state.tk=t
def _sr_cb():
    v=st.session_state.get("srch","").upper().strip()
    if not v: return
    try:
        t=yf.Ticker(v);i=t.info
        if i and (i.get("currentPrice") or i.get("regularMarketPrice") or i.get("previousClose")): st.session_state.tk=v
    except: pass
def get_logo(t):
    dm=DOMAINS.get(t,f"{t.lower()}.com")
    return f"https://www.google.com/s2/favicons?domain={dm}&sz=128"
def fmt(v,s="n",d=2):
    if v is None or (isinstance(v,float) and pd.isna(v)): return "—"
    if s=="$":
        if abs(v)>=1e12: return f"${v/1e12:.{d}f}T"
        if abs(v)>=1e9: return f"${v/1e9:.{d}f}B"
        if abs(v)>=1e6: return f"${v/1e6:.{d}f}M"
        return f"${v:,.{d}f}"
    if s=="%": return f"{v*100:.{d}f}%" if abs(v)<10 else f"{v:.{d}f}%"
    if s=="x": return f"{v:.{d}f}x"
    if s=="p": return f"${v:,.{d}f}"
    return f"{v:,.{d}f}"
def sdate(v):
    if v is None: return None
    if isinstance(v,date_type) and not isinstance(v,datetime): return v
    try: return v.date()
    except: pass
    try: return pd.Timestamp(v).date()
    except: return None

@st.cache_data(ttl=300)
def fetch(ticker):
    stk=yf.Ticker(ticker);i=stk.info;d={}
    d["name"]=i.get("longName") or i.get("shortName",ticker)
    d["sector"]=i.get("sector","—")
    d["price"]=i.get("currentPrice") or i.get("regularMarketPrice")
    d["prev"]=i.get("previousClose") or i.get("regularMarketPreviousClose")
    d["vol"]=i.get("volume") or i.get("regularMarketVolume")
    d["avg_vol"]=i.get("averageVolume")
    d["52h"]=i.get("fiftyTwoWeekHigh");d["52l"]=i.get("fiftyTwoWeekLow")
    d["50ma"]=i.get("fiftyDayAverage");d["200ma"]=i.get("twoHundredDayAverage")
    d["beta"]=i.get("beta")
    d["chg"]=0;d["chg_pct"]=0
    if d["price"] and d["prev"]: d["chg"]=d["price"]-d["prev"];d["chg_pct"]=d["chg"]/d["prev"]
    d["mcap"]=i.get("marketCap");d["pe_t"]=i.get("trailingPE");d["pe_f"]=i.get("forwardPE")
    d["ev_ebitda"]=i.get("enterpriseToEbitda")
    d["rev_g"]=i.get("revenueGrowth");d["gm"]=i.get("grossMargins")
    d["om"]=i.get("operatingMargins");d["pm"]=i.get("profitMargins")
    d["eps_t"]=i.get("trailingEps");d["eps_f"]=i.get("forwardEps")
    d["fcf"]=i.get("freeCashflow")
    d["roe"]=i.get("returnOnEquity");d["roa"]=i.get("returnOnAssets")
    d["short_pct"]=i.get("shortPercentOfFloat")
    d["tgt_mean"]=i.get("targetMeanPrice");d["tgt_high"]=i.get("targetHighPrice")
    d["tgt_low"]=i.get("targetLowPrice")
    d["rec"]=i.get("recommendationKey","—").upper();d["n_a"]=i.get("numberOfAnalystOpinions")
    d["fcf_y"]=(d["fcf"]/d["mcap"]) if d.get("fcf") and d.get("mcap") and d["mcap"]>0 else None
    d["earn_date"]=None
    try:
        cal=stk.calendar
        if isinstance(cal,dict):
            ed=cal.get("Earnings Date")
            if ed and len(ed)>0: d["earn_date"]=sdate(ed[0])
    except: pass
    if d["earn_date"] is None:
        try:
            edf=stk.earnings_dates
            if edf is not None and len(edf)>0:
                fut=edf[edf.index>=pd.Timestamp.now()]
                d["earn_date"]=sdate(fut.index[0]) if len(fut)>0 else sdate(edf.index[0])
        except: pass
    return d

@st.cache_data(ttl=3600)
def fetch_rsi(ticker,period=14):
    try:
        h=yf.Ticker(ticker).history(period="3mo")
        if h is None or len(h)<period+1: return None
        delta=h["Close"].diff()
        gain=delta.where(delta>0,0).rolling(window=period).mean()
        loss=(-delta.where(delta<0,0)).rolling(window=period).mean()
        rs=gain/loss;rsi=100-(100/(1+rs))
        return round(rsi.iloc[-1],1)
    except: return None

@st.cache_data(ttl=600)
def fetch_opts(ticker):
    try:
        stk=yf.Ticker(ticker);dates=stk.options
        if not dates: return None,None
        rows=[]
        for exp in dates[:3]:
            try: chain=stk.option_chain(exp)
            except: continue
            for side,df in [("CALL",chain.calls),("PUT",chain.puts)]:
                for _,r in df.iterrows():
                    try:
                        rv=r.get("volume");roi=r.get("openInterest")
                        if rv is None or roi is None: continue
                        if pd.isna(rv) or pd.isna(roi): continue
                        v=int(float(rv));oi=int(float(roi))
                        if v<=0 or oi<=0: continue
                        ratio=v/oi
                        riv=r.get("impliedVolatility",0)
                        iv=round(float(riv)*100,1) if riv and not pd.isna(riv) else 0
                        rows.append({"T":side,"exp":exp,"K":r["strike"],"vol":v,"oi":oi,"voi":round(ratio,2),"iv":iv,"unusual":ratio>2.0 and v>100})
                    except: continue
        if not rows: return None,None
        df=pd.DataFrame(rows)
        cv=int(df[df["T"]=="CALL"]["vol"].sum());pv=int(df[df["T"]=="PUT"]["vol"].sum())
        summ={"cv":cv,"pv":pv,"pcr":round(pv/cv,2) if cv>0 else 0,"unc":int(df["unusual"].sum())}
        unu=df[df["unusual"]].sort_values("vol",ascending=False).head(6)
        return summ,unu
    except: return None,None

# ── CSS ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');
    :root{--jm:'JetBrains Mono',monospace;--sg:'Space Grotesk',sans-serif;--bg:#0a0f1a;--card:#0d1520;--border:#1a2535;--txt:#e2e8f0;--dim:#4a6080}
    :root,.stApp{color-scheme:dark!important;background:var(--bg)!important;color:var(--txt)!important}
    .stApp{font-family:var(--sg)}
    .block-container{padding-top:0.1rem!important;padding-bottom:0!important;max-width:100%!important}
    header[data-testid="stHeader"]{display:none!important}
    div[data-testid="stHorizontalBlock"]{gap:0.6rem!important}
    div[data-testid="stVerticalBlock"]{gap:0.04rem!important}
    div[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:5px;padding:3px 6px!important}
    div[data-testid="stMetric"]:hover{border-color:#3b82f6}
    div[data-testid="stMetric"] label{color:#536580!important;font-family:var(--jm)!important;font-size:0.46rem!important;text-transform:uppercase;min-height:0!important;padding:0!important;margin:0!important;line-height:1!important}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"]{color:var(--txt)!important;font-family:var(--jm)!important;font-weight:600!important;font-size:0.7rem!important;line-height:1.15!important}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"]{font-family:var(--jm)!important;font-size:0.5rem!important}
    .ot{width:100%;border-collapse:collapse;font-family:var(--jm);font-size:0.56rem}
    .ot th{color:var(--dim);text-transform:uppercase;font-size:0.44rem;padding:2px 4px;border-bottom:1px solid var(--border);text-align:left}
    .ot td{color:#d0d8e4;padding:2px 4px;border-bottom:1px solid #111827}
    .ot .fl{color:#f97316;font-weight:700}.ot .ca{color:#22c55e}.ot .pu{color:#ef4444}
    div[data-testid="stRadio"]>label{display:none!important}
    div[data-testid="stRadio"] div[role="radiogroup"]{gap:1px!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label{font-family:var(--jm)!important;font-size:0.6rem!important;font-weight:700!important;padding:5px 4px!important;background:var(--card);border:1px solid var(--border);border-radius:4px;justify-content:center;min-height:0!important;color:#7a8fa5!important;white-space:nowrap!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:#2563eb;color:#60a5fa!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"]{border-color:#2563eb!important;background:#0c1528!important;color:#60a5fa!important}
    .fl{font-family:var(--jm);font-size:0.82rem;color:#c0ccd8;padding:0;margin:0}
    .fl .rw{display:flex;justify-content:space-between;align-items:center;padding:3.5px 0;border-bottom:1px solid #111a28}
    .fl .rw:last-child{border-bottom:none}
    .fl .lb{color:#5a7090;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.02em}
    .fl .vl{color:var(--txt);font-weight:600;text-align:right;font-size:0.82rem}
    .fl .vl.g{color:#22c55e}.fl .vl.r{color:#ef4444}.fl .vl.b{color:#60a5fa}.fl .vl.y{color:#eab308}
    .fl .hd{font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em;color:#3d5068;border-bottom:1px solid #172033;padding:5px 0 2px 0;margin-top:4px;font-weight:600}
    button[title="View fullscreen"]{display:none!important}
    .stTextInput label{font-size:0.5rem!important;font-family:var(--jm)!important;color:#3d5068!important}
    .stLinkButton>a{font-family:var(--jm)!important;font-size:0.58rem!important;font-weight:600!important;padding:8px 6px!important;min-height:0!important;border-radius:5px!important;text-align:center!important}
</style>
""",unsafe_allow_html=True)

# ── FETCH ──
ticker=st.session_state.tk
try: d=fetch(ticker)
except Exception as e: st.error(f"Error: {e}");st.stop()
rsi_val=fetch_rsi(ticker)
rec=d.get("rec","—");rec_clean=rec.replace("_"," ")
if rec in ["BUY","STRONG_BUY","STRONGBUY","OUTPERFORM"]: bc="#22c55e";bbg="rgba(34,197,94,0.15)"
elif rec in ["SELL","UNDERPERFORM","STRONG_SELL","STRONGSELL"]: bc="#ef4444";bbg="rgba(239,68,68,0.15)"
else: bc="#eab308";bbg="rgba(234,179,8,0.15)"
yf_options=f"https://finance.yahoo.com/quote/{ticker}/options/"
twitter_url=f"https://x.com/search?q=%23{ticker}&src=typed_query&f=live"

# ══════════ TITLE + SEARCH ══════════
t1,t2=st.columns([8.5,1.5])
with t1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0;padding:0;">
        <img src="{RAIGOR}" style="width:80px;height:80px;filter:drop-shadow(0 0 10px rgba(180,120,40,0.6));flex-shrink:0;" />
        <h1 style="margin:0;padding-left:16px;font-size:3rem;font-weight:800;font-family:var(--jm);
            background:linear-gradient(90deg,#ef4444 0%,#f97316 40%,#eab308 100%);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:0.05em;line-height:1;">
            MATUMBRO QUANT</h1>
    </div>""",unsafe_allow_html=True)
with t2:
    # ← THIS IS THE 60px SPACER ABOVE SEARCH BAR (change this value to adjust) →
    st.markdown('<div style="height:35px;"></div>',unsafe_allow_html=True)
    sv=st.text_input("s",placeholder="US ticker → Enter",key="srch",on_change=_sr_cb,label_visibility="collapsed")
    if sv and len(sv)>=1:
        q=sv.upper().strip()
        matches=[t for t in US_TOP if t.startswith(q) and t!=q][:5]
        if matches:
            st.markdown(f'<div style="font-family:var(--jm);font-size:0.55rem;color:#60a5fa;margin-top:-6px;">{"  ·  ".join(matches)}</div>',unsafe_allow_html=True)

# ← THIS IS THE HORIZONTAL DIVIDER LINE →
st.markdown('<div style="border-bottom:2px solid #1e293b;margin:4px 0 0 0;"></div>',unsafe_allow_html=True)

# ← THIS IS THE 30px SPACER BELOW THE DIVIDER LINE (change this value to adjust) →
st.markdown('<div style="height:35px;"></div>',unsafe_allow_html=True)

# ══════════ STOCK HEADER ══════════
# Column widths: watchlist wider (0.75) to fit $TCEHY and $AWWE on one line
hw,hc,hf,ht=st.columns([0.75,5.25,2.0,2.0])
lg=get_logo(ticker)
chg_c="#22c55e" if d["chg"]>=0 else "#ef4444"
chg_bg="rgba(34,197,94,0.1)" if d["chg"]>=0 else "rgba(239,68,68,0.1)"
cs="+" if d["chg"]>=0 else ""
ps=f"${d['price']:,.2f}" if d["price"] else "—"
cstr=f"{cs}{d['chg']:.2f} ({cs}{d['chg_pct']*100:.2f}%)" if d["price"] else ""

with hw: st.write("")
with hc:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;padding:0 0 2px 0;">
        <div style="display:flex;align-items:center;gap:10px;padding-left:4px;">
            <img src="{lg}" style="width:42px;height:42px;border-radius:8px;background:#fff;padding:2px;" onerror="this.style.display='none'" />
            <div>
                <div style="font-family:var(--sg);font-size:1.45rem;font-weight:800;color:#f1f5f9;line-height:1;">{d['name']}</div>
                <div style="font-family:var(--jm);font-size:0.85rem;color:#64748b;margin-top:2px;">
                    {ticker} · {d['sector']}
                    <span style="font-size:0.85rem;font-weight:800;color:{bc};background:{bbg};padding:2px 10px;border-radius:4px;border:1px solid {bc}40;margin-left:8px;">{rec_clean}</span>
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:baseline;gap:10px;">
            <span style="font-family:var(--jm);font-size:1.5rem;font-weight:700;color:#f1f5f9;">{ps}</span>
            <span style="font-family:var(--jm);font-size:0.9rem;font-weight:700;color:{chg_c};background:{chg_bg};padding:3px 10px;border-radius:4px;">{cstr}</span>
        </div>
    </div>""",unsafe_allow_html=True)
with hf: st.write("")
with ht: st.write("")

# ← THIS IS THE 30px GAP BETWEEN STOCK HEADER AND CHART →
st.markdown('<div style="height:30px;"></div>',unsafe_allow_html=True)

# ══════════ MAIN 4-COL LAYOUT ══════════
wl,cc2,fc,tc=st.columns([0.75,5.25,2.0,2.0])

# ──── WATCHLIST ────
with wl:
    wl_labels=[f"${t}" for t in QUICK_TICKERS]
    cur=f"${ticker}" if ticker in QUICK_TICKERS else None
    idx=wl_labels.index(cur) if cur in wl_labels else 0
    st.radio("w",wl_labels,index=idx,key="wl_radio",on_change=_wl_cb,label_visibility="collapsed")

# ──── CHART + OPTIONS ────
with cc2:
    ch=f"""<div style="border-radius:6px;overflow:hidden;border:1px solid var(--border);">
    <div style="height:556px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
    {{"autosize":true,"symbol":"{ticker}","interval":"D","timezone":"Asia/Singapore","theme":"dark","style":"1",
    "locale":"en","backgroundColor":"rgba(10,15,26,1)","gridColor":"rgba(26,37,53,0.5)",
    "allow_symbol_change":false,"hide_top_toolbar":false,"hide_legend":false,"save_image":false,
    "calendar":false,"hide_volume":false,"support_host":"https://www.tradingview.com",
    "studies":["STD;SMA","STD;RSI"]}}
    </script></div></div>"""
    st.components.v1.html(ch,height=571)
    st.markdown(f'<div style="font-family:var(--jm);font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;color:#3d5068;padding-bottom:10px;margin:10px 0 2px 0;">⚡ Options Flow · <a href="{yf_options}" target="_blank" style="color:#3b82f6;text-decoration:none;">Open Yahoo Finance ↗</a></div>',unsafe_allow_html=True);st.markdown('<div style="height:20px;"></div>',unsafe_allow_html=True)
    osumm,ounu=fetch_opts(ticker)
    if osumm:
        o1,o2,o3,o4=st.columns(4)
        o1.metric("Call Vol",f"{osumm['cv']:,}");o2.metric("Put Vol",f"{osumm['pv']:,}")
        o3.metric("P/C Ratio",f"{osumm['pcr']:.2f}");o4.metric("🚨 Unusual",str(osumm["unc"]))
        if ounu is not None and len(ounu)>0:
            tbl="<table class='ot'><tr><th>Type</th><th>Strike</th><th>Exp</th><th>Vol</th><th>OI</th><th>V/OI</th><th>IV</th><th></th></tr>"
            for _,r in ounu.iterrows():
                tc2="ca" if r["T"]=="CALL" else "pu";fl="🔥" if r["voi"]>5 else "⚠️"
                tbl+=f"<tr><td class='{tc2}'>{r['T']}</td><td>${r['K']:.0f}</td><td>{r['exp']}</td><td>{r['vol']:,}</td><td>{r['oi']:,}</td><td class='fl'>{r['voi']:.1f}x</td><td>{r['iv']}%</td><td>{fl}</td></tr>"
            tbl+="</table>";st.markdown(tbl,unsafe_allow_html=True)
        else: st.caption("No unusual activity")
    else: st.caption("Options: refresh if not loading")

# ──── F COLUMN: Earnings → Twitter → Valuation → EPS → Margins → Cash Flow ────
with fc:
    def fr(l,v,c=""): return f'<div class="rw"><span class="lb">{l}</span><span class="vl{" "+c if c else ""}">{v}</span></div>'

    # EARNINGS BOX
    ed=d.get("earn_date")
    if ed:
        da=(ed-date_type.today()).days
        ct="📢 TODAY" if da==0 else (f"{da} DAYS AWAY" if da>0 else f"{abs(da)}D AGO")
        ec="#60a5fa" if da>0 else "#f97316"
        ed_str=ed.strftime("%d/%m/%Y")
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0c1528,#131a2e);border:1px solid #2563eb;border-radius:8px;padding:10px 14px;text-align:center;">
        <div style="font-family:var(--jm);font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;margin-bottom:4px;">📅 NEXT EARNINGS</div>
        <div style="font-family:var(--jm);font-size:1.6rem;font-weight:800;color:#f1f5f9;line-height:1.1;">{ed_str}</div>
        <div style="font-family:var(--jm);font-size:1rem;font-weight:700;color:{ec};margin-top:4px;">⏰ {ct}</div>
        </div>""",unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#0c1528;border:1px solid #1e293b;border-radius:8px;padding:10px;text-align:center;">
        <div style="font-family:var(--jm);font-size:0.55rem;text-transform:uppercase;color:#3d5068;">📅 NEXT EARNINGS</div>
        <div style="font-family:var(--jm);font-size:1.2rem;font-weight:700;color:var(--dim);margin-top:4px;">TBD</div></div>""",unsafe_allow_html=True)

    # 30px gap → Twitter button
    st.markdown('<div style="height:35px;"></div>',unsafe_allow_html=True)
    st.link_button(f"🐦  #{ticker} on X / Twitter", twitter_url, use_container_width=True)

    # 30px gap → Valuation
    st.markdown('<div style="height:20px;"></div>',unsafe_allow_html=True)

    h='<div class="fl">'
    h+='<div class="hd">📊 Valuation</div>'
    h+=fr("Market Cap",fmt(d.get("mcap"),"$",1))
    h+=fr("Trailing P/E",fmt(d.get("pe_t"),"x"))
    h+=fr("Forward P/E",fmt(d.get("pe_f"),"x"))
    h+=fr("EV/EBITDA",fmt(d.get("ev_ebitda"),"x"))
    h+='<div class="hd">💵 EPS</div>'
    h+=fr("EPS Trailing",f"${d['eps_t']:.2f}" if d.get("eps_t") else "—")
    h+=fr("EPS Forward",f"${d['eps_f']:.2f}" if d.get("eps_f") else "—")
    eg=None
    if d.get("eps_t") and d.get("eps_f") and d["eps_t"]>0: eg=(d["eps_f"]-d["eps_t"])/abs(d["eps_t"])
    h+=fr("EPS Growth",f"{eg*100:+.1f}%" if eg is not None else "—","g" if eg and eg>0 else ("r" if eg and eg<0 else ""))
    h+='<div class="hd">📈 Margins & Growth</div>'
    h+=fr("Revenue Growth",fmt(d.get("rev_g"),"%",1),"g" if d.get("rev_g") and d["rev_g"]>0 else "")
    h+=fr("Gross Margin",fmt(d.get("gm"),"%",1))
    h+=fr("Operating Margin",fmt(d.get("om"),"%",1))
    h+=fr("Net Margin",fmt(d.get("pm"),"%",1))
    h+=fr("ROE",fmt(d.get("roe"),"%",1))
    h+=fr("ROA",fmt(d.get("roa"),"%",1))
    h+='<div class="hd">💰 Cash Flow</div>'
    h+=fr("Free Cash Flow",fmt(d.get("fcf"),"$",1))
    h+=fr("FCF Yield",fmt(d.get("fcf_y"),"%",1),"g" if d.get("fcf_y") and d["fcf_y"]>0.03 else "")
    h+='</div>'
    st.markdown(h,unsafe_allow_html=True)

# ──── T COLUMN: Price Target → Price Context → Technicals → Entry ────
with tc:
    def tr2(l,v,c=""): return f'<div class="rw"><span class="lb">{l}</span><span class="vl{" "+c if c else ""}">{v}</span></div>'

    # PRICE TARGET SLIDER
    tl=d.get("tgt_low") or 0;tm=d.get("tgt_mean") or 0;th2=d.get("tgt_high") or 0;cp=d.get("price") or 0
    if th2>0 and tl>0 and th2>tl:
        rng=th2-tl
        cp_pct=max(0,min(100,((cp-tl)/rng)*100))
        tm_pct=max(0,min(100,((tm-tl)/rng)*100))
        na_count=d.get("n_a") or "—"
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:6px;padding:8px 10px;">
            <div style="font-family:var(--jm);font-size:0.5rem;text-transform:uppercase;color:var(--dim);margin-bottom:6px;">🎯 Price Target · {na_count} analysts</div>
            <div style="position:relative;height:36px;margin:8px 0;">
                <div style="position:absolute;top:16px;left:0;right:0;height:3px;background:#1e293b;border-radius:2px;"></div>
                <div style="position:absolute;top:16px;left:0;width:{cp_pct}%;height:3px;background:linear-gradient(90deg,#3b82f6,#60a5fa);border-radius:2px;"></div>
                <div style="position:absolute;top:8px;left:{tm_pct}%;transform:translateX(-50%);text-align:center;z-index:2;">
                    <div style="font-family:var(--jm);font-size:0.72rem;font-weight:700;color:#60a5fa;background:var(--card);padding:1px 6px;border-radius:3px;border:1px solid #3b82f6;">${tm:,.0f}</div>
                    <div style="font-family:var(--jm);font-size:0.4rem;color:#3b82f6;">Avg</div>
                </div>
            </div>
            <div style="display:flex;justify-content:space-between;font-family:var(--jm);">
                <span style="font-size:0.6rem;color:#ef4444;">${tl:,.0f} <span style="font-size:0.4rem;color:var(--dim);">Low</span></span>
                <span style="font-size:0.6rem;color:var(--txt);">Current ${cp:,.0f}</span>
                <span style="font-size:0.6rem;color:#22c55e;">${th2:,.0f} <span style="font-size:0.4rem;color:var(--dim);">High</span></span>
            </div>
        </div>""",unsafe_allow_html=True)
    else:
        st.caption("Price targets N/A")

    # ← 30px GAP BETWEEN PRICE TARGET AND PRICE CONTEXT →
    st.markdown('<div style="height:30px;"></div>',unsafe_allow_html=True)

    # TECHNICAL DATA
    h2='<div class="fl">'
    h2+='<div class="hd">📦 Price Context</div>'
    h2+=tr2("52W High",fmt(d.get("52h"),"p"))
    h2+=tr2("52W Low",fmt(d.get("52l"),"p"))
    h2+=tr2("50D MA",fmt(d.get("50ma"),"p"))
    h2+=tr2("200D MA",fmt(d.get("200ma"),"p"))
    h2+=tr2("Beta",f"{d['beta']:.2f}" if d.get("beta") else "—")
    h2+='<div class="hd">📊 Volume</div>'
    h2+=tr2("Volume",fmt(d.get("vol"),"$",0))
    vr=d["vol"]/d["avg_vol"] if d.get("vol") and d.get("avg_vol") and d["avg_vol"]>0 else None
    h2+=tr2("Vol/Avg",f"{vr:.2f}x" if vr else "—","g" if vr and vr>1.5 else ("r" if vr and vr<0.5 else ""))
    h2+='<div class="hd">📐 Technicals</div>'
    if rsi_val is not None:
        rsi_c="r" if rsi_val>70 else ("g" if rsi_val<30 else ("y" if rsi_val>60 else ""))
        h2+=tr2("RSI (14)",f"{rsi_val}",rsi_c)
    else: h2+=tr2("RSI (14)","—")
    if d.get("price") and d.get("50ma"):
        d50=(d["price"]-d["50ma"])/d["50ma"]*100
        h2+=tr2("vs 50D MA",f"{d50:+.1f}%","g" if d50>0 else "r")
    if d.get("price") and d.get("200ma"):
        d200=(d["price"]-d["200ma"])/d["200ma"]*100
        h2+=tr2("vs 200D MA",f"{d200:+.1f}%","g" if d200>0 else "r")
    if d.get("price") and d.get("52h"):
        off=(d["price"]-d["52h"])/d["52h"]*100
        h2+=tr2("Off 52W High",f"{off:.1f}%","r" if off<-10 else "")
    h2+=tr2("Short % Float",fmt(d.get("short_pct"),"%",1))
    h2+='<div class="hd">🛒 Entry Levels</div>'
    ls=[];p=d.get("price")
    if p:
        for lb,k in [("50D MA","50ma"),("200D MA","200ma"),("52W Low","52l")]:
            v2=d.get(k)
            if v2 and v2<p: ls.append((lb,v2,(p-v2)/p*100))
        ls.sort(key=lambda x:x[1],reverse=True)
    cxx=["g","b",""]
    for i2,(lb,v2,pct) in enumerate(ls[:3]):
        h2+=tr2(lb,f"${v2:,.2f} (-{pct:.1f}%)",cxx[min(i2,2)])
    if not ls: h2+=tr2("Status","At/below key MAs","")
    h2+='</div>'
    st.markdown(h2,unsafe_allow_html=True)
