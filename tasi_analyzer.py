import sys
import subprocess
import uuid
import os
import json
from datetime import datetime, timedelta

# التأكد من استدعاء الحزم السحابية المطلوبة للرسوم والويب والملفات التخزينية
import streamlit as st
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
import time
import plotly.graph_objects as go
from streamlit_cookies_controller import CookieController

# استدعاء متحكم الذاكرة الصلبة للجهاز (Cookies)
controller = CookieController()
DB_FILE = "secure_licenses_db.json"

def save_licenses_to_storage(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_licenses_from_storage():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "TASI-VIP-8899": {"owner": "أبو فهد", "expiry": "2026-12-31", "role": "user"},
            "TASI-PREMIUM-1122": {"owner": "أبو عبدالله", "expiry": "2026-12-31", "role": "user"}
        }
        save_licenses_to_storage(initial_data)
        return initial_data
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

if 'SYSTEM_LICENSES' not in st.session_state:
    st.session_state['SYSTEM_LICENSES'] = load_licenses_from_storage()

MASTER_ADMIN_KEY = "ADMIN-TASI-2026"

def get_device_fingerprint():
    headers = st.context.headers
    user_agent = headers.get("User-Agent", "Unknown_Device")
    accept_lang = headers.get("Accept-Language", "Unknown_Lang")
    return f"{user_agent}_{accept_lang}"

# --- إعدادات واجهة منصة الصقر المحدثة بالهوية الفاخرة ---
st.set_page_config(page_title="منصة صقر تاسي للتحليل الفني والمالي للأعضاء", layout="wide")

# حقن كود التصميم المطور لإلغاء تداخل النصوص والخطوط العمودية في المنتصف نهائياً على الجوال
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        html, body, [data-testid="stSidebar"], .stApp { font-family: 'Cairo', sans-serif !important; direction: rtl !text-align: right; }
        #MainMenu, footer, header, .stAppDeployButton, [data-testid="stHeader"] {display: none !important;}
        [data-testid="stSidebar"] { min-width: 320px !important; max-width: 350px !important; z-index: 99999 !important; }
        [data-testid="stSidebarUserContent"] { direction: rtl !important; text-align: right !important; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #0284c7 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color:#0f172a; padding:30px; border-radius:16px; margin-bottom:25px; border-bottom: 4px solid #0284c7; text-align:right;">
        <h1 style="color:#f8fafc; margin:0; font-weight:700; font-size:28px;">🦅 منصة الصقر الذكية لتحليل الأسهم السعودية والتوصيات</h1>
        <p style="color:#38bdf8; margin:8px 0 0 0; font-size:15px; font-weight:500;">
            المحطة التفاعلية الفاخرة للفرز المدمج وتحديد المستهدفات اللحظية | نسخة التوليد الدائم 🔒
        </p>
    </div>
""", unsafe_allow_html=True)

card_col1, card_col2, card_col3 = st.columns(3)
with card_col1:
    st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #38bdf8; text-align:center;">
        <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold;"> الأسهم المغطاة</p>
        <h3 style="color:#f8fafc; margin:5px 0 0 0; font-size:22px;">66 شركة قيادية</h3>
    </div>""", unsafe_allow_html=True)
with card_col2:
    st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #22c55e; text-align:center;">
        <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold;"> وضع السوق الكلي</p>
        <h3 style="color:#22c55e; margin:5px 0 0 0; font-size:22px;">تحليل تقاطعي نشط</h3>
    </div>""", unsafe_allow_html=True)
with card_col3:
    st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #a855f7; text-align:center;">
        <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold;"> إدارة الأموال</p>
        <h3 style="color:#a855f7; margin:5px 0 0 0; font-size:22px;">حاسبة مخاطر ذكية</h3>
    </div>""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
current_device_id = get_device_fingerprint()
saved_key = controller.get("tasi_saved_license_key")

st.sidebar.markdown("<h2 style='text-align:right; color:#38bdf8; font-size:20px; font-weight:700;'>🔐 مركز التوثيق والأمان</h2>", unsafe_allow_html=True)

if not saved_key:
    user_key = st.sidebar.text_input("أدخل مفتاح التفعيل السري (لمرة واحدة فقط):", "", type="password").strip()
    if st.sidebar.button("💾 تفعيل وحفظ في هذا الجهاز"):
        if user_key == MASTER_ADMIN_KEY or user_key in st.session_state['SYSTEM_LICENSES']:
            controller.set("tasi_saved_license_key", user_key)
            st.sidebar.success("تم تفعيل الجهاز بنجاح!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.sidebar.error("المفتاح غير صحيح!")
    user_key_active = user_key
else:
    user_key_active = saved_key
    st.sidebar.markdown(f"<div style='background-color:#0f172a; padding:12px; border-radius:8px; border-right:4px solid #22c55e; color:#e2e8f0; font-size:14px; font-weight:bold; text-align:center;'>🔒 تم التفعيل التلقائي للجهاز</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 تسجيل الخروج / مسح الجهاز"):
        controller.remove("tasi_saved_license_key")
        st.rerun()

is_admin = False
is_access_granted = False
block_reason = ""

if user_key_active == MASTER_ADMIN_KEY:
    is_admin = True
    is_access_granted = True
    st.sidebar.success("🔓 المشرف: نشط")
elif user_key_active in st.session_state['SYSTEM_LICENSES']:
    license_info = st.session_state['SYSTEM_LICENSES'][user_key_active]
    expiry_date = datetime.strptime(license_info["expiry"], "%Y-%m-%d").date()
    if datetime.now().date() > expiry_date:
        block_reason = f"عذراً، هذا الاشتراك منتهي منذ تاريخ: {license_info['expiry']}"
    else:
        is_access_granted = True
        st.sidebar.success(f"👤 العضو: {license_info['owner']}")
elif user_key_active:
    block_reason = "مفتاح التفعيل غير مسجل بنظام الصقر!"

if not is_access_granted:
    display_msg = block_reason if block_reason else "يرجى إدخال مفتاح التفعيل السري وحفظه في جهازك لفتح محطة التداول الفورية."
    st.markdown(f"""
        <div style="background-color:#7f1d1d; padding:35px; border-radius:14px; margin-top:30px; text-align:right; border-right:8px solid #ef4444;">
            <h2 style="color:#fee2e2; margin:0; font-weight:bold; font-size:22px;">🔒 محطة التداول مغلقة (منطقة مدفوعة للأعضاء)</h2>
            <p style="color:#fca5a5; margin:12px 0 0 0; font-size:15px; font-weight:bold;">
                {display_msg}
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# لوحة الإدارة المصححة والمحمية بالكامل من أخطاء الـ AttributeError
if is_admin:
    st.markdown("<div style='background-color:#1e1b4b; padding:20px; border-radius:14px; border:1px solid #4338ca; margin-bottom:25px;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:right; color:#c084fc; margin:0 0 15px 0; font-size:20px; font-weight:bold;'>⚙️ لوحة الإدارة السرية للتحكم بالاشتراكات</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        sub_name = st.text_input("اسم المشترك الجديد:", "حامد الطلحي")
    with col2:
        sub_days = st.number_input("مدة صلاحية المفتاح بالأيام:", min_value=1, max_value=365, value=30)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ توليد وتثبيت الكود السري", type="secondary"):
            # تصحيح البرمجة: استخراج النص بدقة تامة من الـ UUID ليعمل التوليد دون مشاكل
            raw_uuid = str(uuid.uuid4())
            clean_part = raw_uuid.split('-')[0].upper()
            new_key = f"TASI-{clean_part}"
            calc_expiry = (datetime.now() + timedelta(days=sub_days)).strftime("%Y-%m-%d")
            
            st.session_state['SYSTEM_LICENSES'][new_key] = {"owner": sub_name, "expiry": calc_expiry, "role": "user"}
            save_licenses_to_storage(st.session_state['SYSTEM_LICENSES'])
            st.success(f"🎉 تم توليد الكود وحفظه بنجاح للأبد للمشترك {sub_name}! الكود السري: {new_key}")
            
    st.markdown("<p style='text-align:right; font-weight:bold; color:#e9d5ff; margin-top:15px;'>📋 قائمة المفاتيح المحفوظة بشكل دائم في السيرفر:</p>", unsafe_allow_html=True)
    db_df = pd.DataFrame.from_dict(st.session_state['SYSTEM_LICENSES'], orient='index').reset_index().rename(columns={'index':'المفتاح السري', 'owner':'اسم المشترك', 'expiry':'تاريخ الانتهاء', 'role':'الفئة'})
    st.dataframe(db_df, use_container_width=True, height=180)
    st.markdown("</div>", unsafe_allow_html=True)

# --- حاسبة المخاطر الجانبية الشغالة دائماً ---
st.sidebar.markdown("<h3 style='text-align:right; color:#c084fc; font-size:17px; font-weight:700;'>🧮 حاسبة توزيع السيولة</h3>", unsafe_allow_html=True)
capital = st.sidebar.number_input("إجمالي رأس المال (ريال)", min_value=1000, value=50000, step=5000)
risk_percent = st.sidebar.slider("نسبة المخاطرة في الصفقة (%)", 1.0, 5.0, 2.0, 0.5)
entry_price = st.sidebar.number_input("سعر الدخول (ريال)", min_value=1.0, value=30.0, step=0.5)
sl_price = st.sidebar.number_input("سعر الوقف (SL)", min_value=0.5, value=29.25, step=0.5)
if entry_price > sl_price:
    allowed_loss = capital * (risk_percent / 100)
    shares = int(allowed_loss / (entry_price - sl_price))
    st.sidebar.info(f"الأسهم المستهدفة: **{shares} سهم**\n\nالسيولة المطلوبة: **{shares * entry_price:.2f} ريال**")
# ================= مصفوفة كامل أسهم السوق السعودي (تاسي) موحدة وجاهزة بعد إضافة جرير =================
TICKERS = {
    '1010': 'بنك الرياض', '1020': 'بنك الجزيرة', '1030': 'الاستثمار', '1050': 'الفرنسي',
    '1060': 'الأول (SAB)', '1080': 'العربي الوطني', '1120': 'مصرف الراجحي', '1140': 'بنك البلاد',
    '1150': 'مصرف الإنماء', '1180': 'البنك الأهلي السعودي',
    '2082': 'أكوا باور', '2222': 'أرامكو السعودية', '4030': 'البحري', '5110': 'الكهرباء السعودية', '2083': 'الدريس',
    '2010': 'سابك', '1211': 'معادن', '2020': 'سابك للمغذيات', '2250': 'المجموعة السعودية', '2310': 'سبكيم العالمية', 
    '2050': 'التصنيع', '2380': 'بترورابغ', '2002': 'المتقدمة', '1304': 'اليمامة للحديد',
    '3010': 'أسمنت العربية', '3020': 'أسمنت اليمامة', '3030': 'أسمنت السعودية', '3040': 'أسمنت القصيم',
    '3050': 'أسمنت الجنوب', '3060': 'أسمنت ينبع', '3080': 'أسمنت الشرقية', '3003': 'أسمنت المدينة',
    '7010': 'STC (الاتصالات)', '7020': 'موبايلي', '7030': 'زين السعودية', '7200': 'تداول السعودية', '7204': 'علم', '4260': 'المعمر',
    '4001': 'أسواق العثيم', '4002': 'المواساة', '4004': 'دله الصحية', '4007': 'الحمادي', '4013': 'سليمان الحبيب',
    '2280': 'المراعي', '2270': 'سدافكو', '6010': 'نادك', '2050': 'صافولا', '2100': 'وفرة',
    '4300': 'دار الأركان', '4020': 'العقارية', '4150': 'الرياض للتعمير', '4250': 'جبل عمر', '4321': 'سينومي سنترز',
    '4040': 'سابتكو', '4140': 'ساسكو', '4190': 'جرير', '8010': 'التعاونية للتأمين', '8020': 'ميدغلف', '8210': 'بوبا العربية'
}

FINANCIAL_DATA = {
    '1120': {'PE': 19.2, 'Sector': 'البنوك'}, '1180': {'PE': 14.5, 'Sector': 'البنوك'},
    '1150': {'PE': 16.4, 'Sector': 'البنوك'}, '2222': {'PE': 16.0, 'Sector': 'الطاقة'},
    '2010': {'PE': 24.1, 'Sector': 'البتروكيماويات'}, '7010': {'PE': 15.1, 'Sector': 'الاتصالات'},
    '4190': {'PE': 15.8, 'Sector': 'الخدمات الاستهلاكية'}
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
    if tech_row['close'] > tech_row['SMA_20'] and tech_row['RSI'] < 65: points += 1
    elif tech_row['close'] < tech_row['SMA_20'] or tech_row['RSI'] > 75: points -= 1
    if tech_row['MACD_Line'] > tech_row['Signal_Line']: points += 1
    else: points -= 1
    fin = FINANCIAL_DATA.get(ticker, {'PE': 20.0, 'Sector': 'أخرى'})
    if fin['PE'] < 17: points += 1
    if points >= 1: return "🟢 شراء (BUY)", points
    elif points == 0: return "🟠 انتظار (HOLD)", points
    else: return "🔴 بيع (SELL)", points
if st.button("🔄 سحب أسعار وتحديث كامل السوق الآن", type="primary"):
    with st.spinner("جاري جلب وتحليل كامل أسهم تاسي (أكثر من 66 شركة قيادية)..."):
        try:
            tv = TvDatafeed()
        except:
            st.error("خطأ اتصال بسيرفرات الأسعار.")
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
                    rec, score = combine_and_decide(symbol, last_candle)
                    current_price = last_candle['close']
                    fin = FINANCIAL_DATA.get(symbol, {'PE': 'غير متوفر', 'Sector': 'عام'})
                    
                    final_report.append({
                        'الرمز': symbol, 'اسم السهم': name, 'القطاع': fin['Sector'],
                        'السعر الحالي': round(current_price, 2), 
                        'الهدف (TP)': round(current_price * 1.05, 2), 'الوقف (SL)': round(current_price * 0.975, 2),
                        'مؤشر RSI': round(last_candle['RSI'], 1), 'مكرر P/E': fin['PE'], 
                        'قوة الإشارة': score, 'القرار والفلترة': rec
                    })
                time.sleep(0.04)
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

    # 1. محرك الاستعلام السريع برقم السهم والشارت
    st.markdown("<h3 style='text-align:right; color:#38bdf8; font-size:18px; font-weight:bold;'>🔍 الاستعلام الفني الفوري برقم السهم</h3>", unsafe_allow_html=True)
    search_code = st.text_input("أدخل رمز السهم من السوق لرسم شارت الحركة فوراً (مثال: 1120):", "").strip()
    if search_code and search_code in all_dfs:
        search_res = df_display[df_display['الرمز'] == search_code]
        if not search_res.empty:
            st.dataframe(search_res.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True)
            s_df = all_dfs[search_code]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['close'], name='السعر', line=dict(color='#06b6d4', width=2.5)))
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['SMA_20'], name='SMA20', line=dict(color='#f59e0b', width=1.5, dash='dash')))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=250, title=dict(text="منحنى الحركة السعرية التفاعلي لآخر 100 شمعة", x=0.9, xanchor='right'))
            st.plotly_chart(fig, use_container_width=True)

    # 2. جدول فرص الشراء الذهبية المرتبة للأولويات لكامل السوق
    st.markdown("<h3 style='text-align:right; color:#22c55e; font-size:18px; font-weight:bold;'>🔥 فرص الشراء الذهبية لكامل السوق (حسب أولوية النقاط)</h3>", unsafe_allow_html=True)
    buy_df = df_display[df_display['القرار والفلترة'].str.contains("🟢", na=False)].sort_values(by='قوة الإشارة', ascending=False)
    if not buy_df.empty:
        st.dataframe(buy_df.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True)
    else:
        st.info("لا توجد فرص شراء مستوفية الشروط في السوق حالياً.")

    # 3. جدول مراقبة السوق السعودي الشامل الكامل
    st.markdown("<h3 style='text-align:right; color:#94a3b8; font-size:18px; font-weight:bold;'>📋 جدول ومراقبة السوق السعودي الشامل الكامل</h3>", unsafe_allow_html=True)
    st.dataframe(df_display.style.map(color_rows, subset=['القرار والفلترة']), use_container_width=True, height=450)
else:
    st.info("المنصة في وضع الجاهزية والاستعداد المالي. اضغط على زر التحديث بالأعلى لتوليد ومراقبة كامل صفقات السوق السعودي.")
