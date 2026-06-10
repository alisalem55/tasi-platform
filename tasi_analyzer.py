import sys
import subprocess
from datetime import datetime

# التأكد من تثبيت الحزم المطلوبة
for package in ["streamlit", "plotly"]:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])

import streamlit as st
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import time
import plotly.graph_objects as go

# --- إعدادات واجهة منصة الويب الاحترافية ---
st.set_page_config(page_title="منصة تاسي الذكية المقسمة", layout="wide")

st.markdown("""
    <div style="background-color:#0f172a; padding:25px; border-radius:12px; margin-bottom:25px; text-align:right; direction:rtl;">
        <h1 style="color:#f8fafc; margin:0; font-family:Sans-Serif;">🦅 منصة الصقر الذكية - نظام القطاعات المجزأة (تاسي)</h1>
        <p style="color:#38bdf8; margin:8px 0 0 0; font-size:16px; font-weight:bold;">
            تحليل السوق السعودي مقسم إلى 4 أجزاء لتسريع السحب ومنع التعليق | حماية مشفرة 🔒
        </p>
    </div>
""", unsafe_allow_html=True)

# ================= قاعدة بيانات المشتركين والمفاتيح =================
ACTIVE_LICENSES = {
    "TASI-VIP-8899": {"owner": "أبو فهد", "expiry": "2026-12-31"},
    "TASI-PREMIUM-1122": {"owner": "أبو عبدالله", "expiry": "2026-12-31"}
}

# شاشة تفعيل الحماية والاشتراكات الجانبية
st.sidebar.markdown("<h2 style='text-align:right; color:#38bdf8;'>🔑 حماية الاشتراكات</h2>", unsafe_allow_html=True)
user_key = st.sidebar.text_input("أدخل مفتاح التفعيل السري:", "", type="password").strip()

is_access_granted = False
if user_key and user_key in ACTIVE_LICENSES:
    expiry_date = datetime.strptime(ACTIVE_LICENSES[user_key]["expiry"], "%Y-%m-%d").date()
    if datetime.now().date() <= expiry_date:
        is_access_granted = True
        st.sidebar.success(f"مرحباً {ACTIVE_LICENSES[user_key]['owner']}! الاشتراك نشط.")
    else:
        st.sidebar.error("المفتاح منتهي!")
elif user_key:
    st.sidebar.error("المفتاح غير صحيح!")

if not is_access_granted:
    st.markdown("""
        <div style="background-color:#7f1d1d; padding:30px; border-radius:12px; margin-top:50px; text-align:right; direction:rtl;">
            <h2 style="color:#fee2e2; margin:0;">🔒 محطة التداول مغلقة (منطقة مدفوعة)</h2>
            <p style="color:#fca5a5; margin:10px 0 0 0; font-size:16px;">
                يرجى إدخال مفتاح التفعيل السري في شريط الحماية الجانبي لفتح أجزاء المنصة.
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- حاسبة المخاطر الجانبية ---
st.sidebar.markdown("<h3 style='text-align:right; color:#a855f7;'>🧮 حاسبة إدارة المخاطر</h3>", unsafe_allow_html=True)
capital = st.sidebar.number_input("إجمالي رأس المال (ريال)", min_value=1000, value=50000, step=5000)
risk_percent = st.sidebar.slider("نسبة المخاطرة في الصفقة (%)", 1.0, 5.0, 2.0, 0.5)
entry_price = st.sidebar.number_input("سعر الدخول (ريال)", min_value=1.0, value=30.0, step=0.5)
sl_price = st.sidebar.number_input("سعر الوقف (SL)", min_value=0.5, value=29.25, step=0.5)
if entry_price > sl_price:
    allowed_loss = capital * (risk_percent / 100)
    shares = int(allowed_loss / (entry_price - sl_price))
    st.sidebar.info(f"الأسهم المستهدفة: **{shares} سهم**\n\nالسيولة المطلوبة: **{shares * entry_price:.2f} ريال**")
# ================= لوحة اختيار الأجزاء الأربعة لتفادي ثقل البيانات =================
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='text-align:right; color:#22c55e;'>📂 اختر جزء السوق للتحليل</h3>", unsafe_allow_html=True)
market_part = st.sidebar.radio(
    "انقر لتحديث قطاع محدد:",
    ["الجزء 1: البنوك والطاقة والاتصالات", 
     "الجزء 2: المواد الأساسية والأسمنت", 
     "الجزء 3: الرعاية والأغذية والزراعة", 
     "الجزء 4: العقارات والنقل والتأمين"]
)

# تصفية الشركات بناءً على الجزء المختار
TICKERS = {}
if "الجزء 1" in market_part:
    TICKERS = {
        '1010': 'بنك الرياض', '1020': 'بنك الجزيرة', '1030': 'الاستثمار', '1050': 'الفرنسي',
        '1060': 'الأول (SAB)', '1080': 'العربي الوطني', '1120': 'مصرف الراجحي', '1140': 'بنك البلاد',
        '1150': 'مصرف الإنماء', '1180': 'البنك الأهلي السعودي', '2082': 'أكوا باور', '2222': 'أرامكو السعودية', 
        '5110': 'الكهرباء السعودية', '7010': 'STC (الاتصالات)', '7020': 'موبايلي', '7030': 'زين السعودية', '7040': 'عذيب'
    }
elif "الجزء 2" in market_part:
    TICKERS = {
        '2010': 'سابك', '1211': 'معادن', '2020': 'سابك للمغذيات', '2250': 'المجموعة السعودية', '2310': 'سبكيم العالمية', 
        '2050': 'التصنيع', '2380': 'بترورابغ', '2002': 'المتقدمة', '1304': 'اليمامة للحديد', '1320': 'أنابيب الشرق',
        '3010': 'أسمنت العربية', '3020': 'أسمنت اليمامة', '3030': 'أسمنت السعودية', '3040': 'أسمنت القصيم',
        '3050': 'أسمنت الجنوب', '3060': 'أسمنت ينبع', '3080': 'أسمنت الشرقية', '3003': 'أسمنت المدينة'
    }
elif "الجزء 3" in market_part:
    TICKERS = {
        '4001': 'أسواق العثيم', '4002': 'المواساة', '4004': 'دله الصحية', '4007': 'الحمادي', '4013': 'سليمان الحبيب',
        '2280': 'المراعي', '2270': 'sadafco', '6010': 'نادك', '2050': 'صافولا', '2100': 'وفرة', '2281': 'تنمية',
        '6020': 'جاكو', '6040': 'تبوك الزراعية', '6050': 'الأسماك', '6060': 'الشرقية الزراعية'
    }
else:
    TICKERS = {
        '4300': 'دار الأركان', '4020': 'العقارية', '4150': 'الرياض للتعمير', '4250': 'جبل عمر', '4321': 'سينومي سنترز', '4220': 'إعمار',
        '4040': 'سابتكو', '4140': 'ساسكو', '4210': 'الأبحاث والإعلام', '1832': 'سيرا', '8010': 'التعاونية للتأمين', 
        '8020': 'ميدغلف', '8030': 'ملاذ', '8120': 'الدرع العربي', '8150': 'أسيج', '8210': 'بوبا العربية'
    }

FINANCIAL_DATA = {
    '1120': {'PE': 19.2, 'Sector': 'البنوك'}, '1180': {'PE': 14.5, 'Sector': 'البنوك'},
    '2222': {'PE': 16.0, 'Sector': 'الطاقة'}, '2010': {'PE': 24.1, 'Sector': 'البتروكيماويات'}
}
# ================= خوارزمية المعادلات الرقمية والتنقيح =================
def calculate_indicators(df):
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-10)
    df['RSI'] = 100 - (100 / (1 + rs))
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD_Line'] = exp1 - exp2
    df['Signal_Line'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()
    return df

def combine_and_decide(ticker, tech_row):
    points = 0
    justifications = []
    if tech_row['close'] > tech_row['SMA_20'] and tech_row['RSI'] < 65: points += 1
    elif tech_row['close'] < tech_row['SMA_20'] or tech_row['RSI'] > 75: points -= 1
    if tech_row['MACD_Line'] > tech_row['Signal_Line']: points += 1; justifications.append("ماكد إيجابي")
    else: points -= 1; justifications.append("ماكد سلبي")
    fin = FINANCIAL_DATA.get(ticker, {'PE': 20.0, 'Sector': 'أخرى'})
    if fin['PE'] < 17: points += 1; justifications.append("مكرر جاذب")
    if points >= 1: return "🟢 شراء (BUY)", points, " | ".join(justifications)
    elif points == 0: return "🟠 انتظار (HOLD)", points, " | ".join(justifications)
    else: return "🔴 بيع (SELL)", points, " | ".join(justifications)
# ================= معالجة العرض والجداول والرسوم البيانية =================
if st.button(f"🔄 تحديث {market_part} الآن", type="primary"):
    with st.spinner(f"جاري كشط بيانات {market_part} بسرعة فائقة..."):
        try:
            tv = TvDatafeed()
        except Exception as e:
            st.error(f"خطأ اتصال: {e}")
            st.stop()

        final_report = []
        all_dfs = {}
        
        for symbol, name in TICKERS.items():
            try:
                df = tv.get_hist(symbol=symbol, exchange='TADAWUL', interval=Interval.in_daily, n_bars=100)
                if df is not None and not df.empty:
                    df = calculate_indicators(df)
                    all_dfs[symbol] = df
                    last_candle = df.iloc[-1]
                    rec, score, reason = combine_and_decide(symbol, last_candle)
                    current_price = last_candle['close']
                    fin = FINANCIAL_DATA.get(symbol, {'PE': 'غير متوفر', 'Sector': 'عام'})
                    
                    final_report.append({
                        'الرمز': symbol, 'اسم السهم': name, 'القطاع': fin['Sector'],
                        'السعر الحالي': round(current_price, 2), 
                        'الهدف (TP)': round(current_price * 1.05, 2), 'الوقف (SL)': round(current_price * 0.975, 2),
                        'مؤشر RSI': round(last_candle['RSI'], 1), 'مكرر P/E': fin['PE'], 
                        'قوة الإشارة': score, 'القرار والفلترة': rec, 'المبررات': reason
                    })
                time.sleep(0.05)
            except: continue

        st.session_state['df_display'] = pd.DataFrame(final_report)
        st.session_state['all_dfs'] = all_dfs

if 'df_display' in st.session_state:
    df_display = st.session_state['df_display']
    all_dfs = st.session_state['all_dfs']
    
    def color_rows(val):
        if "🟢" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif "🔴" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        elif "🟠" in str(val): return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
        return ''

    # 1. الاستعلام الفني السريع
    st.markdown("<h3 style='text-align:right; color:#38bdf8;'>🔍 الاستعلام الفني السريع برقم السهم</h3>", unsafe_allow_html=True)
    search_code = st.text_input("أدخل رمز السهم من هذا الجزء لرسم شارت الحركة فوراً (مثال: 1120):", "").strip()
    if search_code and search_code in all_dfs:
        search_res = df_display[df_display['الرمز'] == search_code]
        if not search_res.empty:
            st.dataframe(search_res.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True)
            s_df = all_dfs[search_code]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['close'], name='السعر', line=dict(color='#06b6d4', width=2)))
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['SMA_20'], name='SMA20', line=dict(color='#f59e0b', dash='dash')))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=250)
            st.plotly_chart(fig, use_container_width=True)

    # 2. توصيات الشراء الذهبية المرتبة للجزء الحالي
    st.markdown(f"<h3 style='text-align:right; color:#22c55e;'>🔥 فرص الشراء الذهبية في {market_part}</h3>", unsafe_allow_html=True)
    buy_df = df_display[df_display['القرار والفلترة'].str.contains("🟢", na=False)].sort_values(by='قوة الإشارة', ascending=False)
    if not buy_df.empty:
        st.dataframe(buy_df.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True)
    else:
        st.info("لا توجد فرص شراء مستوفية الشروط في هذا الجزء حالياً.")

    # 3. جدول مراقبة القطاعات المحددة الشامل
    st.markdown(f"<h3 style='text-align:right; color:#94a3b8;'>📋 جدول ومراقبة أسهم {market_part}</h3>", unsafe_allow_html=True)
    st.dataframe(df_display.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True, height=350)
else:
    st.info("المنصة في وضع الجاهزية. اختر الجزء من اليسار ثم اضغط على زر التحديث بالأعلى لتوليد البيانات الفورية.")
