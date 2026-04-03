import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date as date_type

st.set_page_config(page_title="MATUMBRO QUANT", page_icon="🪝", layout="wide", initial_sidebar_state="collapsed")

if "tk" not in st.session_state:
    st.session_state.tk = "NVDA"

QUICK_TICKERS = ["NVDA","GOOG","AVGO","ORCL","QQQ","MU","MRVL","COHR","TSEM","LITE","NBIS"]
PUDGE = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/pudge.png"
DOMAINS = {
    "AAPL":"apple.com","MSFT":"microsoft.com","GOOGL":"google.com","GOOG":"google.com",
    "AMZN":"amazon.com","NVDA":"nvidia.com","META":"meta.com","TSLA":"tesla.com",
    "AVGO":"broadcom.com","NFLX":"netflix.com","AMD":"amd.com","ADBE":"adobe.com",
    "QCOM":"qualcomm.com","INTC":"intel.com","TXN":"ti.com","AMAT":"appliedmaterials.com",
    "MU":"micron.com","LRCX":"lamresearch.com","KLAC":"kla.com","MRVL":"marvell.com",
    "ON":"onsemi.com","SMCI":"supermicro.com","CRWD":"crowdstrike.com",
    "PANW":"paloaltonetworks.com","DDOG":"datadoghq.com","NET":"cloudflare.com",
    "SNOW":"snowflake.com","PLTR":"palantir.com","COIN":"coinbase.com","ABNB":"airbnb.com",
    "UBER":"uber.com","PYPL":"paypal.com","SHOP":"shopify.com","ARM":"arm.com",
    "NBIS":"nebius.com","COHR":"coherent.com","LITE":"lumentum.com","AAOI":"ao-inc.com",
    "QQQ":"invesco.com","SOFI":"sofi.com","HOOD":"robinhood.com","RIVN":"rivian.com",
    "TSEM":"towersemi.com","SMH":"vaneck.com","SOXX":"ishares.com","COST":"costco.com",
    "MELI":"mercadolibre.com","ORCL":"oracle.com",
}

def _wl_cb():
    v=st.session_state.get("wl_radio",""); t=v.replace("$","").strip()
    if t: st.session_state.tk=t

def _sr_cb():
    v=st.session_state.get("srch","").upper().strip()
    if not v: return
    try:
        test=yf.Ticker(v); info=test.info
        if info and (info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")):
            st.session_state.tk=v
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
    if d["price"] and d["prev"]: d["chg"]=d["price"]-d["prev"]; d["chg_pct"]=d["chg"]/d["prev"]
    d["mcap"]=i.get("marketCap");d["pe_t"]=i.get("trailingPE");d["pe_f"]=i.get("forwardPE")
    d["peg"]=i.get("pegRatio");d["ps"]=i.get("priceToSalesTrailing12Months")
    d["pb"]=i.get("priceToBook");d["ev_ebitda"]=i.get("enterpriseToEbitda")
    d["rev_g"]=i.get("revenueGrowth");d["gm"]=i.get("grossMargins")
    d["om"]=i.get("operatingMargins");d["pm"]=i.get("profitMargins")
    d["eps_t"]=i.get("trailingEps");d["eps_f"]=i.get("forwardEps")
    d["roe"]=i.get("returnOnEquity");d["roa"]=i.get("returnOnAssets")
    d["short_pct"]=i.get("shortPercentOfFloat")
    d["tgt_mean"]=i.get("targetMeanPrice");d["tgt_high"]=i.get("targetHighPrice")
    d["tgt_low"]=i.get("targetLowPrice")
    d["rec"]=i.get("recommendationKey","—").upper();d["n_a"]=i.get("numberOfAnalystOpinions")
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
    :root{--jm:'JetBrains Mono',monospace;--sg:'Space Grotesk',sans-serif}
    .stApp{font-family:var(--sg)}
    .block-container{padding-top:0.1rem!important;padding-bottom:0!important;max-width:100%!important}
    header[data-testid="stHeader"]{display:none!important}
    div[data-testid="stHorizontalBlock"]{gap:0.2rem!important}
    div[data-testid="stVerticalBlock"]{gap:0.04rem!important}
    div[data-testid="stMetric"]{background:#0d1520;border:1px solid #1e293b;border-radius:5px;padding:3px 6px!important}
    div[data-testid="stMetric"]:hover{border-color:#3b82f6}
    div[data-testid="stMetric"] label{color:#536580!important;font-family:var(--jm)!important;font-size:0.46rem!important;text-transform:uppercase;min-height:0!important;padding:0!important;margin:0!important;line-height:1!important}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"]{color:#e2e8f0!important;font-family:var(--jm)!important;font-weight:600!important;font-size:0.7rem!important;line-height:1.15!important}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"]{font-family:var(--jm)!important;font-size:0.5rem!important}
    .ot{width:100%;border-collapse:collapse;font-family:var(--jm);font-size:0.56rem}
    .ot th{color:#4a6080;text-transform:uppercase;font-size:0.44rem;padding:2px 4px;border-bottom:1px solid #1e293b;text-align:left}
    .ot td{color:#d0d8e4;padding:2px 4px;border-bottom:1px solid #111827}
    .ot .fl{color:#f97316;font-weight:700}.ot .ca{color:#22c55e}.ot .pu{color:#ef4444}
    div[data-testid="stRadio"]>label{display:none!important}
    div[data-testid="stRadio"] div[role="radiogroup"]{gap:1px!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label{font-family:var(--jm)!important;font-size:0.62rem!important;font-weight:700!important;padding:5px 0!important;background:#0d1520;border:1px solid #1a2535;border-radius:4px;justify-content:center;min-height:0!important;color:#7a8fa5!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:#2563eb;color:#60a5fa!important}
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"]{border-color:#2563eb!important;background:#0c1528!important;color:#60a5fa!important}
    .fl{font-family:var(--jm);font-size:0.82rem;color:#c0ccd8;padding:0;margin:0}
    .fl .rw{display:flex;justify-content:space-between;align-items:center;padding:3.5px 0;border-bottom:1px solid #111a28}
    .fl .rw:last-child{border-bottom:none}
    .fl .lb{color:#5a7090;font-size:0.68rem;text-transform:uppercase;letter-spacing:0.02em}
    .fl .vl{color:#e2e8f0;font-weight:600;text-align:right;font-size:0.82rem}
    .fl .vl.g{color:#22c55e}.fl .vl.r{color:#ef4444}.fl .vl.b{color:#60a5fa}
    .fl .hd{font-size:0.58rem;text-transform:uppercase;letter-spacing:0.06em;color:#3d5068;border-bottom:1px solid #172033;padding:5px 0 2px 0;margin-top:4px;font-weight:600}
    textarea{font-family:var(--jm)!important;font-size:0.7rem!important;background:#080d16!important;border-color:#1a2535!important;color:#c0ccd8!important}
    button[title="View fullscreen"]{display:none!important}
    .stTextInput label,.stTextArea label{font-size:0.5rem!important;font-family:var(--jm)!important;color:#3d5068!important}
</style>
""",unsafe_allow_html=True)

# ── FETCH ──
ticker=st.session_state.tk
try: d=fetch(ticker)
except Exception as e: st.error(f"Error: {e}"); st.stop()

rec=d.get("rec","—");rec_clean=rec.replace("_"," ")
if rec in ["BUY","STRONG_BUY","STRONGBUY","OUTPERFORM"]: bc="#22c55e";bbg="rgba(34,197,94,0.15)"
elif rec in ["SELL","UNDERPERFORM","STRONG_SELL","STRONGSELL"]: bc="#ef4444";bbg="rgba(239,68,68,0.15)"
else: bc="#eab308";bbg="rgba(234,179,8,0.15)"

# ══ TITLE — big pudge, text shifted right ══
st.markdown(f"""
<div style="display:flex;align-items:center;gap:0;padding:0 0 2px 0;">
    <img src="{PUDGE}" style="width:80px;height:80px;filter:drop-shadow(0 0 10px rgba(220,38,38,0.6));flex-shrink:0;" />
    <h1 style="margin:0;padding-left:20px;font-size:3rem;font-weight:800;font-family:var(--jm);
        background:linear-gradient(90deg,#ef4444 0%,#f97316 40%,#eab308 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:0.05em;line-height:1;">
        MATUMBRO QUANT</h1>
</div>
""",unsafe_allow_html=True)

# ══ HEADER — aligned with main columns ══
hw,hc,hf,ht=st.columns([0.55,5.45,2.0,2.0])
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
            <span style="font-family:var(--sg);font-size:1.8rem;font-weight:800;color:#f1f5f9;line-height:1;">{d['name']}</span>
            <span style="font-family:var(--jm);font-size:0.95rem;color:#64748b;font-weight:500;">{ticker} · {d['sector']}</span>
            <span style="font-family:var(--jm);font-size:0.95rem;font-weight:800;
                color:{bc};background:{bbg};padding:3px 14px;border-radius:5px;
                border:1px solid {bc}40;">{rec_clean}</span>
        </div>
        <div style="display:flex;align-items:baseline;gap:10px;">
            <span style="font-family:var(--jm);font-size:1.5rem;font-weight:700;color:#f1f5f9;">{ps}</span>
            <span style="font-family:var(--jm);font-size:0.9rem;font-weight:700;color:{chg_c};background:{chg_bg};padding:3px 10px;border-radius:4px;">{cstr}</span>
        </div>
    </div>
    """,unsafe_allow_html=True)
with hf: st.write("")
with ht:
    st.text_input("s",placeholder="Any ticker → Enter",key="srch",on_change=_sr_cb,label_visibility="collapsed")

# ══ MAIN ══
wl,cc,fc,tc=st.columns([0.55,5.45,2.0,2.0])

with wl:
    wl_labels=[f"${t}" for t in QUICK_TICKERS]
    cur=f"${ticker}" if ticker in QUICK_TICKERS else None
    idx=wl_labels.index(cur) if cur in wl_labels else 0
    st.radio("w",wl_labels,index=idx,key="wl_radio",on_change=_wl_cb,label_visibility="collapsed")

with cc:
    ch=f"""<div style="border-radius:6px;overflow:hidden;border:1px solid #1a2535;">
    <div style="height:556px;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
    {{"autosize":true,"symbol":"{ticker}","interval":"D","timezone":"Asia/Singapore","theme":"dark","style":"1",
    "locale":"en","backgroundColor":"rgba(13,21,32,1)","gridColor":"rgba(26,37,53,0.5)",
    "allow_symbol_change":false,"hide_top_toolbar":false,"hide_legend":false,"save_image":false,
    "calendar":false,"hide_volume":false,"support_host":"https://www.tradingview.com",
    "studies":["STD;SMA","STD;RSI"]}}
    </script></div></div>"""
    st.components.v1.html(ch,height=571)
    st.markdown('<div style="font-family:var(--jm);font-size:0.48rem;text-transform:uppercase;letter-spacing:0.08em;color:#3d5068;border-bottom:1px solid #172033;padding-bottom:1px;margin:3px 0 2px 0;">⚡ Options Flow</div>',unsafe_allow_html=True)
    osumm,ounu=fetch_opts(ticker)
    if osumm:
        o1,o2,o3,o4=st.columns(4)
        o1.metric("Call Vol",f"{osumm['cv']:,}"); o2.metric("Put Vol",f"{osumm['pv']:,}")
        o3.metric("P/C Ratio",f"{osumm['pcr']:.2f}"); o4.metric("🚨 Unusual",str(osumm["unc"]))
        if ounu is not None and len(ounu)>0:
            tbl="<table class='ot'><tr><th>Type</th><th>Strike</th><th>Exp</th><th>Vol</th><th>OI</th><th>V/OI</th><th>IV</th><th></th></tr>"
            for _,r in ounu.iterrows():
                tc2="ca" if r["T"]=="CALL" else "pu"; fl="🔥" if r["voi"]>5 else "⚠️"
                tbl+=f"<tr><td class='{tc2}'>{r['T']}</td><td>${r['K']:.0f}</td><td>{r['exp']}</td><td>{r['vol']:,}</td><td>{r['oi']:,}</td><td class='fl'>{r['voi']:.1f}x</td><td>{r['iv']}%</td><td>{fl}</td></tr>"
            tbl+="</table>"; st.markdown(tbl,unsafe_allow_html=True)
        else: st.caption("No unusual activity")
    else: st.caption("Options: refresh if not loading")

# ──── F COLUMN ────
with fc:
    def fr(l,v,c=""): return f'<div class="rw"><span class="lb">{l}</span><span class="vl{" "+c if c else ""}">{v}</span></div>'
    ed=d.get("earn_date")
    if ed:
        da=(ed-date_type.today()).days
        ct="📢 TODAY" if da==0 else (f"{da} DAYS AWAY" if da>0 else f"{abs(da)}D AGO")
        ec="#60a5fa" if da>0 else "#f97316"
        st.markdown(f"""<div style="background:linear-gradient(135deg,#0c1528,#131a2e);border:1px solid #2563eb;border-radius:8px;padding:10px 14px;margin-bottom:6px;text-align:center;">
        <div style="font-family:var(--jm);font-size:0.55rem;text-transform:uppercase;letter-spacing:0.1em;color:#3b82f6;margin-bottom:4px;">📅 NEXT EARNINGS</div>
        <div style="font-family:var(--jm);font-size:1.6rem;font-weight:800;color:#f1f5f9;line-height:1.1;">{ed.strftime('%b %d, %Y')}</div>
        <div style="font-family:var(--jm);font-size:1rem;font-weight:700;color:{ec};margin-top:4px;">⏰ {ct}</div>
        </div>""",unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#0c1528;border:1px solid #1e293b;border-radius:8px;padding:10px;margin-bottom:6px;text-align:center;">
        <div style="font-family:var(--jm);font-size:0.55rem;text-transform:uppercase;color:#3d5068;">📅 NEXT EARNINGS</div>
        <div style="font-family:var(--jm);font-size:1.2rem;font-weight:700;color:#4a6080;margin-top:4px;">TBD</div></div>""",unsafe_allow_html=True)
    h='<div class="fl">'
    h+='<div class="hd">📊 Valuation</div>'
    h+=fr("Market Cap",fmt(d.get("mcap"),"$",1))
    h+=fr("Trailing P/E",fmt(d.get("pe_t"),"x"))
    h+=fr("Forward P/E",fmt(d.get("pe_f"),"x"))
    h+=fr("PEG Ratio",fmt(d.get("peg"),"x"))
    h+=fr("P/S Ratio",fmt(d.get("ps"),"x"))
    h+=fr("P/B Ratio",fmt(d.get("pb"),"x"))
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
    h+='</div>'
    st.markdown(h,unsafe_allow_html=True)

# ──── T COLUMN ────
with tc:
    def tr2(l,v,c=""): return f'<div class="rw"><span class="lb">{l}</span><span class="vl{" "+c if c else ""}">{v}</span></div>'
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
    h2+='<div class="hd">📐 MA Position</div>'
    if d.get("price") and d.get("50ma"):
        d50=(d["price"]-d["50ma"])/d["50ma"]*100
        h2+=tr2("vs 50D MA",f"{d50:+.1f}%","g" if d50>0 else "r")
    if d.get("price") and d.get("200ma"):
        d200=(d["price"]-d["200ma"])/d["200ma"]*100
        h2+=tr2("vs 200D MA",f"{d200:+.1f}%","g" if d200>0 else "r")
    if d.get("price") and d.get("52h"):
        off=(d["price"]-d["52h"])/d["52h"]*100
        h2+=tr2("Off 52W High",f"{off:.1f}%","r" if off<-10 else "")
    h2+='<div class="hd">🎯 Analyst Consensus</div>'
    h2+=tr2("Rating",rec_clean,"g" if "BUY" in rec else ("r" if "SELL" in rec else ""))
    h2+=tr2("# Analysts",str(d.get("n_a") or "—"))
    h2+=tr2("Target Mean",fmt(d.get("tgt_mean"),"p"))
    h2+=tr2("Target High",fmt(d.get("tgt_high"),"p"))
    h2+=tr2("Target Low",fmt(d.get("tgt_low"),"p"))
    if d.get("price") and d.get("tgt_mean"):
        up=(d["tgt_mean"]-d["price"])/d["price"]
        h2+=tr2("Implied Upside",f"{up*100:+.1f}%","g" if up>0 else "r")
    h2+='<div class="hd">🛒 Entry Levels</div>'
    ls=[];p=d.get("price")
    if p:
        for lb,k in [("50D MA","50ma"),("200D MA","200ma"),("52W Low","52l")]:
            v2=d.get(k)
            if v2 and v2<p: ls.append((lb,v2,(p-v2)/p*100))
        ls.sort(key=lambda x:x[1],reverse=True)
    cx=["g","b",""]
    for i2,(lb,v2,pct) in enumerate(ls[:3]):
        h2+=tr2(lb,f"${v2:,.2f} (-{pct:.1f}%)",cx[min(i2,2)])
    if not ls: h2+=tr2("Status","At/below key MAs","")
    h2+='</div>'
    st.markdown(h2,unsafe_allow_html=True)

    # PASTE BOX right under T column
    st.markdown('<div style="font-family:var(--jm);font-size:0.52rem;text-transform:uppercase;letter-spacing:0.06em;color:#3d5068;border-bottom:1px solid #172033;padding-bottom:1px;margin:6px 0 2px 0;">📝 Paste Box</div>',unsafe_allow_html=True)
    intel=st.text_area("i",placeholder="Paste tweets, Patreon, articles for AI analysis...",height=100,label_visibility="collapsed",key="intel")
    if intel: st.caption(f"📄 {len(intel.split())} words · Phase 3 ready")
