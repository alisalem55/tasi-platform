import sys
import subprocess

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
st.set_page_config(page_title="منصة تاسي الذكية لتنقيح وترتيب الأسهم", layout="wide")

st.markdown("""
    <div style="background-color:#0f172a; padding:25px; border-radius:12px; margin-bottom:25px; text-align:right; direction:rtl;">
        <h1 style="color:#f8fafc; margin:0; font-family:Sans-Serif;">🦅 منصة الصقر الذكية لترتيب وتنقيح الأسهم السعودية</h1>
        <p style="color:#38bdf8; margin:8px 0 0 0; font-size:16px; font-weight:bold;">
            فرز أسبوعي حاد حسب الأولوية وقوة النقاط | محرك بحث فوري برمز السهم | شارتات تفاعلية مدمجة
        </p>
    </div>
""", unsafe_allow_html=True)

# قائمة شاملة لأسهم السوق السعودي المدرجة في المنصة
TICKERS = {
    '1120': 'مصرف الراجحي', '1180': 'البنك الأهلي السعودي', '1150': 'مصرف الإنماء',
    '1140': 'بنك البلاد', '1020': 'بنك الجزيرة', '1030': 'البنك السعودي للاستثمار', 
    '1050': 'البنك السعودي الفرنسي', '1060': 'البنك السعودي الأول (SAB)', '1080': 'البنك العربي الوطني',
    '2222': 'أرامكو السعودية', '2010': 'سابك', '2082': 'أكوا باور', '5110': 'الكهرباء السعودية',
    '2002': 'المتقدمة', '2250': 'المجموعة السعودية', '2020': 'سابك للمغذيات الزراعية',
    '2310': 'سبكيم العالمية', '2050': 'التصنيع', '2380': 'بترورابغ',
    '7010': 'STC (الاتصالات السعودية)', '7020': 'اتحاد اتصالات (موبايلي)', '7030': 'زين السعودية',
    '7200': 'تداول السعودية', '7204': 'علم', '4260': 'المعمر لأنظمة المعلومات',
    '1211': 'معادن', '1304': 'اليمامة للحديد', '3020': 'أسمنت اليمامة', '3030': 'أسمنت السعودية', 
    '3040': 'أسمنت القصيم', '3050': 'أسمنت الجنوب', '3060': 'أسمنت ينبع',
    '2280': 'المراعي', '2270': 'سدافكو', '6010': 'نادك', '2050': 'صافولا', 
    '4002': 'المواساة', '4013': 'سليمان الحبيب', '4004': 'دله الصحية',
    '4300': 'دار الأركان', '4020': 'العقارية', '4150': 'الرياض للتعمير', '4250': 'جبل عمر',
    '4030': 'البحري', '4040': 'سابتكو', '4140': 'ساسكو', '8010': 'التعاونية للتأمين'
}

FINANCIAL_DATA = {
    '1120': {'PE': 19.2, 'Sector': 'البنوك'}, '1180': {'PE': 14.5, 'Sector': 'البنوك'},
    '1150': {'PE': 16.4, 'Sector': 'البنوك'}, '1140': {'PE': 17.1, 'Sector': 'البنوك'},
    '2222': {'PE': 16.0, 'Sector': 'الطاقة'}, '2010': {'PE': 24.1, 'Sector': 'البتروكيماويات'},
    '2082': {'PE': 35.4, 'Sector': 'المرافق'}, '7010': {'PE': 15.1, 'Sector': 'الاتصالات'},
    '4300': {'PE': 29.4, 'Sector': 'العقار'}, '2280': {'PE': 23.5, 'Sector': 'التغذية'}
}

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
    elif fin['PE'] > 26: points -= 1; justifications.append("مكرر متضخم")
        
    if fin['Sector'] == 'العقار': points -= 1; justifications.append("ضغوط عقارية")
    elif fin['Sector'] in ['الطاقة', 'البتروكيماويات']: points += 1; justifications.append("دعم نفطي")

    if points >= 1:
        return "🟢 شراء (BUY)", points, " | ".join(justifications)
    elif points == 0:
        return "🟠 انتظار (HOLD)", points, " | ".join(justifications)
    else:
        return "🔴 بيع (SELL)", points, " | ".join(justifications)

# --- حاسبة حجم الصفقة الجانبية ---
st.sidebar.markdown("<h2 style='text-align:right; color:#38bdf8;'>🧮 حاسبة إدارة المخاطر</h2>", unsafe_allow_html=True)
capital = st.sidebar.number_input("إجمالي رأس المال (ريال)", min_value=1000, value=50000, step=5000)
risk_percent = st.sidebar.slider("نسبة المخاطرة في الصفقة (%)", 1.0, 5.0, 2.0, 0.5)
entry_price = st.sidebar.number_input("سعر الدخول (ريال)", min_value=1.0, value=30.0, step=0.5)
sl_price = st.sidebar.number_input("سعر الوقف المقترح (SL)", min_value=0.5, value=29.25, step=0.5)

if entry_price > sl_price:
    allowed_loss = capital * (risk_percent / 100)
    shares_to_buy = int(allowed_loss / (entry_price - sl_price))
    st.sidebar.info(f" عدد الأسهم المستهدفة: **{shares_to_buy} سهم**\n\n السيولة المطلوبة: **{shares_to_buy * entry_price:.2f} ريال**")

# زر تحديث المنصة الرئيسي
if st.button("🔄 سحب أسعار وتحديث المنصة الآن", type="primary"):
    with st.spinner("جاري كشط وفلترة جزيئات تاسي من TradingView..."):
        try:
            tv = TvDatafeed()
        except Exception as conn_error:
            st.error(f"خطأ اتصال بسيرفرات التغذية الحية: {conn_error}")
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
                    take_profit = current_price * 1.05 if "🟢" in rec else current_price * 1.03
                    stop_loss = current_price * 0.975 if "🟢" in rec else current_price * 0.98
                    fin = FINANCIAL_DATA.get(symbol, {'PE': 'غير متوفر', 'Sector': 'عام'})
                    
                    final_report.append({
                        'الرمز': symbol, 'اسم السهم': name, 'القطاع': fin['Sector'],
                        'السعر الحالي': round(current_price, 2), 
                        'الهدف (TP)': round(take_profit, 2), 'الوقف (SL)': round(stop_loss, 2),
                        'مؤشر RSI': round(last_candle['RSI'], 1), 'مكرر P/E': fin['PE'], 
                        'قوة الإشارة (النقاط)': score, 'القرار والفلترة': rec, 'المبررات': reason
                    })
                time.sleep(0.1)
            except: continue

        st.session_state['df_display'] = pd.DataFrame(final_report)
        st.session_state['all_dfs'] = all_dfs

# معالجة وعرض البيانات بدون جملة شرطية معقدة لمنع أي خطأ مسافات نهائياً
if 'df_display' in st.session_state:
    df_display = st.session_state['df_display']
    all_dfs = st.session_state['all_dfs']
    
    def color_rows(val):
        if "🟢" in str(val): return 'background-color: #d4edda; color: #155724; font-weight: bold;'
        elif "🔴" in str(val): return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
        elif "🟠" in str(val): return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
        return ''

    # === الميزة 1: محرك البحث السريع بالرقم ===
    st.markdown("<h3 style='text-align:right; color:#38bdf8;'>🔍 الاستعلام الفني السريع عن شركة</h3>", unsafe_allow_html=True)
    search_code = st.text_input("أدخل رقم الرمز الرباعي للشركة هنا لفلترتها فوراً ورسم الشارت (مثال: 1120 أو 2222):", "").strip()
    
    if search_code:
        search_res = df_display[df_display['الرمز'] == search_code]
        if not search_res.empty:
            st.success(f"تم العثور على تحليل سهم: {search_res['اسم السهم'].values}")
            st.dataframe(search_res.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True)
            
            if search_code in all_dfs:
                s_df = all_dfs[search_code]
                fig_s = go.Figure()
                fig_s.add_trace(go.Scatter(x=s_df.index, y=s_df['close'], name='السعر اللحظي', line=dict(color='#06b6d4', width=2)))
                fig_s.add_trace(go.Scatter(x=s_df.index, y=s_df['SMA_20'], name='SMA20', line=dict(color='#f59e0b', dash='dash')))
                fig_s.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=300)
                st.plotly_chart(fig_s, use_container_width=True)
        else:
            st.warning("الرمز المدخل غير مدرج في القائمة الحالية، يرجى تشغيل التحديث أولاً.")

    # === الميزة 2: جدول فرص الشراء المرتبة بالأولوية القصوى ===
    st.markdown("<h3 style='text-align:right; color:#22c55e;'>🔥 توصيات الشراء الذهبية (مرتبة بالأولوية وقوة النقاط)</h3>", unsafe_allow_html=True)
    buy_df = df_display[df_display['القرار والفلترة'].str.contains("🟢", na=False)].sort_values(by='قوة الإشارة (النقاط)', ascending=False)
    
    if not buy_df.empty:
        st.dataframe(buy_df.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True, height=200)
    else:
        st.info("لا توجد فرص شراء صريحة مستوفية للشروط بالكامل حالياً، يفضل الانتظار.")

    # === الميزة 3: لوحة تحكم ومراقبة السوق الكامل الشامل ===
    st.markdown("<h3 style='text-align:right; color:#94a3b8;'>📋 جدول لوحة ومراقبة السوق الشامل (تاسي)</h3>", unsafe_allow_html=True)
    st.dataframe(df_display.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True, height=350)

# حالة الاستعداد قبل التحديث الأول
