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

# استدعاء متحكم الذاكرة الدائمة للجهاز (Cookies) لمدة سنة كاملة
controller = CookieController()
DB_FILE = "secure_device_locks.json"

# دالة لحفظ أقفال الأجهزة في السيرفر لمنع التشارك
def save_device_locks(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# دالة لقراءة أقفال الأجهزة المسجلة
def load_device_locks():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

if 'DEVICE_LOCKS' not in st.session_state:
    st.session_state['DEVICE_LOCKS'] = load_device_locks()

# 📋 [تم التثبيت النهائي هنا] قاعدة بيانات المشتركين الرسمية والصلبة داخل صلب الكود
if 'STATIC_LICENSES' not in st.session_state:
    st.session_state['STATIC_LICENSES'] = {
        "TASI-VIP-8899": {"owner": "أبو فهد", "expiry": "2026-12-31"},
        "TASI-PREMIUM-1122": {"owner": "أبو عبدالله", "expiry": "2026-12-31"},
        "TASI-HAMEED-77": {"owner": "حامد الطلحي", "expiry": "2027-01-01"},
        "TASI-SULTAN-99": {"owner": "أبو سلطان", "expiry": "2027-01-01"},
    }

MASTER_ADMIN_KEY = "ADMIN-TASI-2026"

# --- خوارزمية ذكية بديلة للـ IP: استخراج البصمة الفريدة والصلبة لجهاز المستخدم لمنع التشارك ---
def get_strict_device_fingerprint():
    headers = st.context.headers
    user_agent = headers.get("User-Agent", "Unknown_Device")
    accept_lang = headers.get("Accept-Language", "Unknown_Lang")
    return f"{user_agent}_{accept_lang}"

# --- إعدادات واجهة منصة الصقر المحدثة بالهوية الفاخرة ---
st.set_page_config(page_title="منصة الصقر الذكية لتحليل الأسهم السعودية والتوصيات", layout="wide")

# حقن كود التصميم المطور لإجبار كافة الجداول، والنصوص، والأرقام على التمركز في المنتصف تماماً (Center)
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        html, body, .stApp { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
        #MainMenu, footer, header, .stAppDeployButton, [data-testid="stHeader"] {display: none !important;}
        [data-testid="stSidebar"] { display: none !important; }
        
        /* إجبار خلايا وعناوين الجداول على التمركز التام بوسط الشاشة */
        .stDataFrame th, .stDataFrame td { text-align: center !important; justify-content: center !important; }
        div[data-testid="stMarkdownContainer"] > p { text-align: center !important; }
        .stNumberInput input { text-align: center !important; }
        
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #0284c7 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color:#0f172a; padding:30px; border-radius:16px; margin-bottom:25px; border-bottom: 4px solid #0284c7; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); text-align:center; direction:rtl;">
        <h1 style="color:#f8fafc; margin:0; font-weight:700; font-size:28px; text-align:center;">🦅 منصة الصقر الذكية لتحليل الأسهم السعودية والتوصيات</h1>
        <p style="color:#38bdf8; margin:8px 0 0 0; font-size:15px; font-weight:500; text-align:center;">
            نسخة التمركز البصري الشامل وتوسيط الأرقام والرموز | نظام حماية المتصفحات المشتركة 🔒
        </p>
    </div>
""", unsafe_allow_html=True)
current_device_fingerprint = get_strict_device_fingerprint()
saved_key = controller.get("tasi_saved_license_key")

# لوحة المؤشرات الرقمية الذكية (Dashboard Cards) موسطة بالكامل
card_col1, card_col2, card_col3 = st.columns(3)
with card_col1:
    st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #38bdf8; text-align:center;">
        <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold; text-align:center;"> الأسهم المغطاة</p>
        <h3 style="color:#f8fafc; margin:5px 0 0 0; font-size:22px; text-align:center;">66 شركة قيادية</h3>
    </div>""", unsafe_allow_html=True)
with card_col2:
    st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #22c55e; text-align:center;">
        <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold; text-align:center;"> وضع السوق الكلي</p>
        <h3 style="color:#22c55e; margin:5px 0 0 0; font-size:22px; text-align:center;">تحليل تقاطعي نشط</h3>
    </div>""", unsafe_allow_html=True)
with card_col3:
    if not saved_key:
        st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #ef4444; text-align:center;">
            <p style="color:#fca5a5; margin:0; font-size:14px; font-weight:bold; text-align:center;">🔑 حالة الحساب</p>
            <p style="color:#fee2e2; margin:5px 0 0 0; font-size:16px; font-weight:bold; text-align:center;">يرجى تفعيل الاشتراك أدناه</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background-color:#1e293b; padding:15px; border-radius:12px; border-right:6px solid #22c55e; text-align:center;">
            <p style="color:#94a3b8; margin:0; font-size:14px; font-weight:bold; text-align:center;">🔒 تفعيل الهوية</p>
            <p style="color:#22c55e; margin:5px 0 0 0; font-size:16px; font-weight:bold; text-align:center;">الجهاز مصرح ومحمي</p>
        </div>""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

user_key_active = saved_key
is_admin = False
is_access_granted = False
block_reason = ""

# شاشة الدخول المنبثقة التلقائية لمرة واحدة في السنة
if not saved_key:
    with st.expander("🔑 اضغط هنا لفتح نافذة تسجيل الدخول وتفعيل المنصة", expanded=True):
        st.markdown("<div style='text-align:center; font-weight:bold;'>أدخل مفتاح التفعيل الخاص بك (يقبل الأحرف الصغيرة والكبيرة دون اختلاف):</div>", unsafe_allow_html=True)
        user_key = st.text_input("رمز الاشتراك السري:", "", type="password", key="modal_key_input").strip()
        
        user_key_upper = user_key.upper() if user_key else ""
        
        if st.button("💾 تفعيل وحفظ الهوية في المتصفح"):
            if user_key_upper == MASTER_ADMIN_KEY or user_key_upper in st.session_state['STATIC_LICENSES']:
                locks = st.session_state['DEVICE_LOCKS'] if 'DEVICE_LOCKS' in st.session_state else load_device_locks()
                if user_key_upper in locks and locks[user_key_upper] != current_device_fingerprint:
                    st.error("🚨 عذراً، هذا الكود مستخدم حالياً في جهاز آخر! يرجى تسجيل الخروج منه أولاً.")
                else:
                    if user_key_upper != MASTER_ADMIN_KEY:
                        locks[user_key_upper] = current_device_fingerprint
                        save_device_locks(locks)
                    controller.set("tasi_saved_license_key", user_key_upper)
                    st.success("🎉 تم التفعيل والاتصال بالمنصة بنجاح!")
                    time.sleep(0.8)
                    st.rerun()
            else:
                st.error("عذراً، رمز التفعيل غير صحيح أو غير مسجل!")
    user_key_active = user_key_upper
else:
    user_key_active = saved_key.upper() if saved_key else ""
    out_col1, out_col2 = st.columns(2)
    with out_col2:
        if st.button("🚪 خروج ومسح الجهاز"):
            locks = load_device_locks()
            if user_key_active in locks:
                del locks[user_key_active]
                save_device_locks(locks)
            controller.remove("tasi_saved_license_key")
            st.rerun()
    with out_col1:
        st.markdown(f"<p style='text-align:center; font-weight:bold; color:#22c55e; padding-top:8px;'>🔒 مرحباً بك، الدخول نشط وتلقائي وبملء الشاشة الموزونة.</p>", unsafe_allow_html=True)

# التحقق الصارم من التزامن بدون تجميد الكود للأبد
if user_key_active == MASTER_ADMIN_KEY:
    is_admin = True
    is_access_granted = True
elif user_key_active in st.session_state['STATIC_LICENSES']:
    locks = load_device_locks()
    if user_key_active in locks and locks[user_key_active] != current_device_fingerprint:
        block_reason = "🚨 عذراً، هذا الاشتراك مفتوح حالياً على جهاز آخر! يرجى إغلاقه من الجهاز الأول لتتمكن من القراءة هنا."
    else:
        license_info = st.session_state['STATIC_LICENSES'][user_key_active]
        expiry_date = datetime.strptime(license_info["expiry"], "%Y-%m-%d").date()
        if datetime.now().date() > expiry_date:
            block_reason = f"عذراً، اشتراكك منتهي الصلاحية منذ تاريخ: {license_info['expiry']}"
        else:
            is_access_granted = True

if not is_access_granted:
    st.markdown(f"""
        <div style="background-color:#7f1d1d; padding:35px; border-radius:14px; margin-top:10px; text-align:center; border-right:8px solid #ef4444;">
            <h2 style="color:#fee2e2; margin:0; text-align:center;">🔒 محطة التداول مقفلة (منع التزامن)</h2>
            <p style="color:#fca5a5; margin:12px 0 0 0; font-size:15px; font-weight:bold; text-align:center;">{block_reason if block_reason else "يرجى تسجيل الدخول بكود التفعيل السري المخصص لجهازك."}</p>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# لوحة المشرف لإنتاج صياغة الأكواد الجاهزة وتوسيط مستعرض البيانات اليدوي
if is_admin:
    st.markdown("<div style='background-color:#1e1b4b; padding:20px; border-radius:14px; border:1px solid #4338ca; margin-bottom:25px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#c084fc; margin:0 0 15px 0; font-size:20px; font-weight:bold;'>⚙️ لوحة التحكم وإدارة أقفال الأجهزة للمشرف</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: sub_name = st.text_input("اسم المشترك الجديد للإنتاج:", "مبارك الدوسري")
    with col2: sub_days = st.number_input("مدة الصلاحية بالأيام:", min_value=1, max_value=365, value=30)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ توليد صيغة الكود الجاهزة للنسخ"):
            raw_uuid = str(uuid.uuid4()).replace('-', '')
            clean_part = raw_uuid[:8].upper()
            generated_key = f"TASI-{clean_part}"
            calc_expiry = (datetime.now() + timedelta(days=sub_days)).strftime("%Y-%m-%d")
            
            # إضافة المشترك الجديد حياً للقائمة الحالية للموقع
            st.session_state['STATIC_LICENSES'][generated_key] = {"owner": sub_name, "expiry": calc_expiry}
            st.success("🎉 تم التوليد وإضافته حياً! انسخ السطر وضعه في الكود بالقسم الأول لحفظه دائماً:")
            st.code(f'"{generated_key}": {{"owner": "{sub_name}", "expiry": "{calc_expiry}"}},')
            
    st.markdown("<p style='text-align:center; font-weight:bold; color:#e9d5ff; margin-top:15px;'>📋 الأكواد والأسماء المسجلة والمثبتة حالياً في نظامك للأبد (موسطة تلقائياً):</p>", unsafe_allow_html=True)
    for key, info in st.session_state['STATIC_LICENSES'].items():
        inner_col1, inner_col2, inner_col3 = st.columns(3)
        with inner_col1: st.markdown(f"<p style='text-align:center;'>👤 **المشترك:** {info['owner']} | 📅 **ينتهي:** {info['expiry']}</p>", unsafe_allow_html=True)
        with inner_col2: st.code(key)
        with inner_col3: st.button("📋 نسخ", key=f"btn_copy_{key}")
    st.markdown("</div>", unsafe_allow_html=True)

calc_exp = st.expander("🧮 حاسبة توزيع السيولة وإدارة المخاطر الصارمة قبل دخول الصفقة (توسيط رقمي تام)", expanded=False)
with calc_exp:
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1: capital = st.number_input("إجمالي رأس المال المتوفر (ريال)", min_value=1000, value=50000, step=5000)
    with c_col2: risk_percent = st.slider("نسبة المخاطرة القصوى مسموحة الصفقة (%)", 1.0, 5.0, 2.0, 0.5)
    with c_col3: entry_price = st.number_input("سعر دخول السهم الحالي (ريال)", min_value=1.0, value=30.0, step=0.5)
    with c_col4: sl_price = st.number_input("سعر الوقف الفني للسهم (SL)", min_value=0.5, value=29.25, step=0.5)
    if entry_price > sl_price:
        allowed_loss = capital * (risk_percent / 100)
        shares = int(allowed_loss / (entry_price - sl_price))
        st.info(f"📈 **خطة إدارة رأس المال موسطة:** عدد الأسهم الآمن للشراء: **{shares} سهم** | السيولة المطلوبة لتخصيصها: **{shares * entry_price:.2f} ريال**")
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
                    current_price = float(last_candle['close'])
                    fin = FINANCIAL_DATA.get(symbol, {'PE': 20.0, 'Sector': 'عام'})
                    
                    final_report.append({
                        'الرمز': str(symbol).strip(), 
                        'اسم السهم': str(name).strip(), 
                        'القطاع': fin['Sector'],
                        'السعر الحالي': current_price, 
                        'الهدف (TP)': float(current_price * 1.05), 
                        'الوقف (SL)': float(current_price * 0.975),
                        'مؤشر RSI': float(last_candle['RSI']), 
                        'مكرر P/E': float(fin['PE']), 
                        'قوة الإشارة': int(score), 
                        'القرار والفلترة': str(rec).strip()
                    })
                time.sleep(0.04)
            except: continue

        st.session_state['df_display'] = pd.DataFrame(final_report)
        st.session_state['all_dfs'] = all_dfs

if 'df_display' in st.session_state:
    df_display = st.session_state['df_display']
    all_dfs = st.session_state['all_dfs']

    # 1. محرك الاستعلام السريع برقم السهم والشارت التفاعلي الموسط
    st.markdown("<h3 style='text-align:center; color:#38bdf8; font-size:18px; font-weight:bold;'>🔍 الاستعلام الفني الفوري برقم السهم</h3>", unsafe_allow_html=True)
    search_code = st.text_input("أدخل رمز السهم من السوق لرسم شارت الحركة فوراً (مثال: 1120):", "", key="center_search_box").strip()
    if search_code and search_code in all_dfs:
        search_res = df_display[df_display['الرمز'] == search_code]
        if not search_res.empty:
            item = search_res.iloc[0]
            bg_color = "#1e4620" if "🟢" in item['القرار والفلترة'] else ("#7f1d1d" if "🔴" in item['القرار والفلترة'] else "#7c2d12")
            st.markdown(f"""
                <div style="background-color:{bg_color}; padding:15px; border-radius:12px; margin-bottom:15px; border:1px solid #ffffff20; direction:rtl; text-align:right;">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:16px;">
                        <span>📈 {item['اسم السهم']} ({item['الرمز']})</span>
                        <span>{item['القرار والفلترة']}</span>
                    </div>
                    <hr style="margin:8px 0; border:0; border-top:1px solid #ffffff20;">
                    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; font-size:13px; text-align:center;">
                        <div><b>السعر:</b><br>{float(item['السعر الحالي']):.2f}</div>
                        <div><b>الهدف:</b><br>{float(item['الهدف (TP)']):.2f}</div>
                        <div><b>الوقف:</b><br>{float(item['الوقف (SL)']):.2f}</div>
                        <div><b>RSI:</b><br>{float(item['مؤشر RSI']):.1f}</div>
                        <div><b>P/E:</b><br>{float(item['مكرر P/E']):.1f}</div>
                        <div><b>النقاط:</b><br>{item['قوة الإشارة']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            s_df = all_dfs[search_code]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['close'], name='السعر', line=dict(color='#06b6d4', width=2.5)))
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['SMA_20'], name='SMA20', line=dict(color='#f59e0b', width=1.5, dash='dash')))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=250, title=dict(text="منحنى الحركة السعرية التفاعلي لآخر 100 شمعة", x=0.5, xanchor='center'))
            st.plotly_chart(fig, use_container_width=True)

    # 2. جدول أولويات فرص الشراء الذهبية لكامل السوق مصممة بنظام البطاقات المرنة للجوال
    st.markdown("<h3 style='text-align:center; color:#22c55e; font-size:18px; font-weight:bold;'>🔥 فرص الشراء الذهبية لكامل السوق (حسب أولوية النقاط)</h3>", unsafe_allow_html=True)
    buy_df = df_display[df_display['القرار والفلترة'].str.contains("🟢", na=False)].sort_values(by='قوة الإشارة', ascending=False)
    
    if not buy_df.empty:
        for idx, item in buy_df.iterrows():
            st.markdown(f"""
                <div style="background-color:#14532d; padding:15px; border-radius:12px; margin-bottom:12px; border-right:6px solid #22c55e; direction:rtl; text-align:right; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:15px; color:#f8fafc;">
                        <span>🟢 {item['اسم السهم']} (رمز: {item['الرمز']})</span>
                        <span style="color:#4ade80;">{item['القرار والفلترة']}</span>
                    </div>
                    <div style="margin-top:2px; font-size:12px; color:#94a3b8;">القطاع: {item['القطاع']}</div>
                    <hr style="margin:8px 0; border:0; border-top:1px solid #ffffff10;">
                    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; font-size:12px; text-align:center; color:#e2e8f0;">
                        <div><b>السعر الحالي</b><br><span style="color:#38bdf8; font-weight:bold;">{float(item['السعر الحالي']):.2f}</span></div>
                        <div><b>الهدف (TP)</b><br><span style="color:#4ade80; font-weight:bold;">{float(item['الهدف (TP)']):.2f}</span></div>
                        <div><b>الوقف (SL)</b><br><span style="color:#f87171; font-weight:bold;">{float(item['الوقف (SL)']):.2f}</span></div>
                        <div><b>مؤشر RSI</b><br>{float(item['مؤشر RSI']):.1f}</div>
                        <div><b>مكرر P/E</b><br>{float(item['مكرر P/E']):.1f}</div>
                        <div><b>القوة الرقمية</b><br><span style="color:#c084fc; font-weight:bold;">{item['
