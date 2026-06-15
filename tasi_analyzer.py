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

def save_device_locks(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_device_locks():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

if 'DEVICE_LOCKS' not in st.session_state:
    st.session_state['DEVICE_LOCKS'] = load_device_locks()

# 📋 قائمة المشتركين الثابتة والمحصنة من الحذف داخل الكود للأبد
STATIC_LICENSES = {
    "TASI-VIP-8899": {"owner": "أبو فهد", "expiry": "2026-12-31"},
    "TASI-PREMIUM-1122": {"owner": "أبو عبدالله", "expiry": "2026-12-31"},
    "TASI-HAMEED-77": {"owner": "حامد الطلحي", "expiry": "2027-01-01"},
    "TASI-E5AFC081": {"owner": "سعيد مشهر", "expiry": "2026-07-14"},
}

MASTER_ADMIN_KEY = "ADMIN-TASI-2026"

def get_strict_device_fingerprint():
    headers = st.context.headers
    user_agent = headers.get("User-Agent", "Unknown_Device")
    accept_lang = headers.get("Accept-Language", "Unknown_Lang")
    return f"{user_agent}_{accept_lang}"

# --- إعدادات واجهة منصة الصقر المحدثة بالهوية الفاخرة ---
st.set_page_config(page_title="منصة الصقر الذكية لتحليل الأسهم السعودية والتوصيات", layout="wide")

# حقن كود التصميم المطور لتجميل الخطوط وإلغاء القوائم الجانبية لتصبح المنصة بملء الشاشة
st.markdown("""
    <style>
        @import url('https://googleapis.com');
        html, body, .stApp { font-family: 'Cairo', sans-serif !important; direction: rtl; text-align: right; }
        #MainMenu, footer, header, .stAppDeployButton, [data-testid="stHeader"] {display: none !important;}
        [data-testid="stSidebar"] { display: none !important; }
        .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #0284c7 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🦅 منصة الصقر الذكية لتحليل الأسهم السعودية والتوصيات")
st.caption("نسخة الجداول الاحترافية والفرز المدمج الشامل وتوسيط الأرقام والرموز | نظام منع التزامن 🔒")
st.divider()
current_device_fingerprint = get_strict_device_fingerprint()
saved_key = controller.get("tasi_saved_license_key")

# لوحة المؤشرات الرقمية القياسية الصافية
card_col1, card_col2, card_col3 = st.columns(3)
with card_col1:
    st.metric(label="📊 الأسهم المغطاة", value="66 شركة قيادية")
with card_col2:
    st.metric(label="📈 وضع السوق الكلي", value="تحليل تقاطعي نشط")
with card_col3:
    if not saved_key:
        st.metric(label="🔑 حالة الحساب", value="بحاجة لتفعيل الاشتراك")
    else:
        st.metric(label="🔒 تفعيل الهوية", value="جهاز مصرح ومحمي")

st.write("")

user_key_active = saved_key
is_admin = False
is_access_granted = False
block_reason = ""

# شاشة الدخول التلقائية لمرة واحدة في السنة
if not saved_key:
    with st.expander("🔑 اضغط هنا لفتح نافذة تسجيل الدخول وتفعيل المنصة", expanded=True):
        st.write("أدخل مفتاح التفعيل الخاص بك (يقبل الأحرف الصغيرة والكبيرة دون اختلاف):")
        user_key = st.text_input("رمز الاشتراك السري:", "", type="password", key="modal_key_input").strip()
        user_key_upper = user_key.upper() if user_key else ""
        
        if st.button("💾 تفعيل وحفظ الهوية في المتصفح"):
            if user_key_upper == MASTER_ADMIN_KEY or user_key_upper in STATIC_LICENSES:
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
        st.info("🔒 مرحباً بك، الدخول نشط وتلقائي وبملء الشاشة الموزونة.")

# التحقق الصارم من التزامن
if user_key_active == MASTER_ADMIN_KEY:
    is_admin = True
    is_access_granted = True
elif user_key_active in STATIC_LICENSES:
    locks = load_device_locks()
    if user_key_active in locks and locks[user_key_active] != current_device_fingerprint:
        block_reason = "🚨 عذراً، هذا الاشتراك مفتوح حالياً على جهاز آخر! يرجى إغلاقه من الجهاز الأول لتتمكن من القراءة هنا."
    else:
        license_info = STATIC_LICENSES[user_key_active]
        expiry_date = datetime.strptime(license_info["expiry"], "%Y-%m-%d").date()
        if datetime.now().date() > expiry_date:
            block_reason = f"عذراً، اشتراكك منتهي الصلاحية منذ تاريخ: {license_info['expiry']}"
        else:
            is_access_granted = True

if not is_access_granted:
    st.error(block_reason if block_reason else "يرجى تسجيل الدخول بكود التفعيل السري المخصص لجهازك.")
    st.stop()

# لوحة التحكم الكلية للمشرف المضاف إليها صندوق التصدير الآمن لمنع الحذف
if is_admin:
    st.subheader("⚙️ لوحة التحكم وإدارة أقفال الأجهزة للمشرف")
    col1, col2, col3 = st.columns(3)
    with col1: sub_name = st.text_input("اسم المشترك الجديد للإنتاج:", "مبارك الدوسري")
    with col2: sub_days = st.number_input("مدة الصلاحية بالأيام:", min_value=1, max_value=365, value=30)
    with col3:
        st.write("")
        if st.button("✨ توليد صيغة الكود الجاهزة للنسخ"):
            raw_uuid = str(uuid.uuid4()).replace('-', '')
            clean_part = raw_uuid[:8].upper()
            generated_key = f"TASI-{clean_part}"
            calc_expiry = (datetime.now() + timedelta(days=sub_days)).strftime("%Y-%m-%d")
            st.success("🎉 تم التوليد بنجاح! انسخ السطر بالأسفل وضعه في الكود في القسم الأول:")
            st.code(f'"{generated_key}": {{"owner": "{sub_name}", "expiry": "{calc_expiry}"}},')
            
    st.write("📋 الأكواد والأسماء المسجلة والمثبتة حالياً في نظامك للأبد:")
    for key, info in STATIC_LICENSES.items():
        inner_col1, inner_col2, inner_col3 = st.columns(3)
        with inner_col1: st.write(f"👤 **المشترك:** {info['owner']} | 📅 **ينتهي:** {info['expiry']}")
        with inner_col2: st.code(key)
        with inner_col3: st.button("📋 نسخ", key=f"btn_copy_{key}")
        
    st.divider()
    st.write("📥 صندوق التصدير الكلي (انسخ هذا المربع بالكامل في حال تحديث الكود لكي لا تضيع الأسماء):")
    full_backup_text = "STATIC_LICENSES = " + json.dumps(STATIC_LICENSES, ensure_ascii=False, indent=4)
    st.text_area("قاعدة البيانات الاحتياطية المكتملة للتحديث:", value=full_backup_text, height=120)
    st.divider()

calc_exp = st.expander("🧮 حاسبة توزيع السيولة وإدارة المخاطر الصارمة قبل دخول الصفقة", expanded=False)
with calc_exp:
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1: capital = st.number_input("إجمالي رأس المال المتوفر (ريال)", min_value=1000, value=50000, step=5000)
    with c_col2: risk_percent = st.slider("نسبة المخاطرة القصوى مسموحة الصفقة (%)", 1.0, 5.0, 2.0, 0.5)
    with c_col3: entry_price = st.number_input("سعر دخول السهم الحالي (ريال)", min_value=1.0, value=30.0, step=0.5)
    with c_col4: sl_price = st.number_input("سعر الوقف الفني للسهم (SL)", min_value=0.5, value=29.25, step=0.5)
    if entry_price > sl_price:
        allowed_loss = capital * (risk_percent / 100)
        shares = int(allowed_loss / (entry_price - sl_price))
        st.success(f"عدد الأسهم الآمن للشراء: {shares} سهم | السيولة المطلوبة لتخصيصها: {shares * entry_price:.2f} ريال")
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
    '4040': 'سابتكو', '4140': 'ساسكو', '4190': 'جرير', '8010': 'التعاونية للتأمين', '8030': 'ميدغلف', '8210': 'بوبا العربية'
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
            bg_color = "#14532d" if "🟢" in item['القرار والفلترة'] else ("#7f1d1d" if "🔴" in item['القرار والفلترة'] else "#7c2d12")
            
            p_val = f"{float(item['السعر الحالي']):.2f}"
            t_val = f"{float(item['الهدف (TP)']):.2f}"
            s_val = f"{float(item['الوقف (SL)']):.2f}"
            r_val = f"{float(item['مؤشر RSI']):.1f}"
            pe_val = f"{float(item['مكرر P/E']):.1f}"
            sig_val = str(item['قوة الإشارة'])
            
            card_html = f'<div style="background-color:{bg_color}; padding:15px; border-radius:12px; margin-bottom:15px; border:1px solid #ffffff20; direction:rtl; text-align:right;">'
            card_html += '<div style="display:flex; justify-content:space-between; font-weight:bold; font-size:16px;">'
            card_html += f"<span>📈 {item['اسم السهم']} ({item['الرمز']})</span><span>{item['القرار والفلترة']}</span></div>"
            card_html += '<hr style="margin:8px 0; border:0; border-top:1px solid #ffffff20;">'
            card_html += '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:8px; font-size:13px; text-align:center;">'
            card_html += f"<div><b>السعر:</b><br>{p_val}</div><div><b>الهدف:</b><br>{t_val}</div><div><b>الوقف:</b><br>{s_val}</div>"
            card_html += f"<div><b>RSI:</b><br>{r_val}</div><div><b>P/E:</b><br>{pe_val}</div><div><b>النقاط:</b><br>{sig_val}</div></div></div>"
            st.markdown(card_html, unsafe_allow_html=True)
            
            s_df = all_dfs[search_code]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['close'], name='السعر', line=dict(color='#06b6d4', width=2.5)))
            fig.add_trace(go.Scatter(x=s_df.index, y=s_df['SMA_20'], name='SMA20', line=dict(color='#f59e0b', width=1.5, dash='dash')))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0f172a", plot_bgcolor="#0f172a", height=250, title=dict(text="منحنى الحركة السعرية لآخر 100 شمعة", x=0.5, xanchor='center'))
            st.plotly_chart(fig, use_container_width=True)

    # 2. جدول أولويات فرص الشراء الذهبية لكامل السوق مصممة بنظام البطاقات المرنة للجوال
    st.markdown("<h3 style='text-align:center; color:#22c55e; font-size:18px; font-weight:bold;'>🔥 فرص الشراء الذهبية لكامل السوق (حسب أولوية النقاط)</h3>", unsafe_allow_html=True)
    buy_df = df_display[df_display['القرار والفلترة'].str.contains("🟢", na=False)].sort_values(by='قوة الإشارة', ascending=False)
    
    if not buy_df.empty:
        for idx, item in buy_df.iterrows():
            p_val = f"{float(item['السعر الحالي']):.2f}"
            t_val = f"{float(item['الهدف (TP)']):.2f}"
            s_val = f"{float(item['الوقف (SL)']):.2f}"
            r_val = f"{float(item['مؤشر RSI']):.1f}"
            pe_val = f"{float(item['مكرر P/E']):.1f}"
            sig_val = str(item['قوة الإشارة'])
            
            b_html = '<div style="background-color:#14532d; padding:15px; border-radius:12px; margin-bottom:12px; border-right:6px solid #22c55e; direction:rtl; text-align:right; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);">'
            b_html += '<div style="display:flex; justify-content:space-between; font-weight:bold; font-size:15px; color:#f8fafc;">'
            b_html += f"<span>🟢 {item['اسم السهم']} (رمز: {item['الرمز']})</span><span style='color:#4ade80;'>{item['القرار والفلترة']}</span></div>"
            b_html += f"<div style='margin-top:2px; font-size:12px; color:#94a3b8;'>القطاع: {item['القطاع']}</div>"
            b_html += '<hr style="margin:8px 0; border:0; border-top:1px solid #ffffff10;">'
            b_html += '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px; font-size:12px; text-align:center; color:#e2e8f0;">'
            b_html += f"<div><b>السعر الحالي</b><br><span style='color:#38bdf8; font-weight:bold;'>{p_val}</span></div>"
            b_html += f"<div><b>الهدف (TP)</b><br><span style='color:#4ade80; font-weight:bold;'>{t_val}</span></div>"
            b_html += f"<div><b>الوقف (SL)</b><br><span style='color:#f87171; font-weight:bold;'>{s_val}</span></div>"
            b_html += f"<div><b>مؤشر RSI</b><br>{r_val}</div><div><b>مكرر P/E</b><br>{pe_val}</div>"
            b_html += f"<div><b>القوة الرقمية</b><br><span style='color:#c084fc; font-weight:bold;'>{sig_val} نقاط</span></div></div></div>"
            st.markdown(b_html, unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:#94a3b8;'>لا توجد فرص شراء مستوفية الشروط في السوق حالياً.</p>", unsafe_allow_html=True)

    # 3. جدول مراقبة السوق السعودي الشامل الكامل بنظام البطاقات الملكية المدمجة
    st.markdown("<h3 style='text-align:center; color:#94a3b8; font-size:18px; font-weight:bold;'>📋 شاشة مراقبة وتصنيف كامل شركات تاسي</h3>", unsafe_allow_html=True)
    for idx, item in df_display.iterrows():
        border_clr = "#22c55e" if "🟢" in item['القرار والفلترة'] else ("#ef4444" if "🔴" in item['القرار والفلترة'] else "#f59e0b")
        p_val = f"{float(item['السعر الحالي']):.2f}"
        t_val = f"{float(item['الهدف (TP)']):.2f}"
        s_val = f"{float(item['الوقف (SL)']):.2f}"
        r_val = f"{float(item['مؤشر RSI']):.1f}"
        pe_val = f"{float(item['مكرر P/E']):.1f}"
        sig_val = str(item['قوة الإشارة'])
        
        all_html = f'<div style="background-color:#111827; padding:14px; border-radius:10px; margin-bottom:10px; border-right:5px solid {border_clr}; direction:rtl; text-align:right;">'
        all_html += '<div style="display:flex; justify-content:space-between; font-weight:bold; font-size:14px; color:#f3f4f6;">'
        all_html += f"<span>🦅 {item['اسم السهم']} (الرمز: {item['الرمز']})</span><span>{item['القرار والفلترة']}</span></div>"
        all_html += '<hr style="margin:6px 0; border:0; border-top:1px solid #ffffff05;">'
        all_html += '<div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:4px; font-size:12px; text-align:center; color:#d1d5db;">'
        all_html += f"<div><b>السعر:</b> {p_val}</div><div><b>الهدف:</b> {t_val}</div><div><b>الوقف:</b> {s_val}</div>"
        all_html += f"<div><b>RSI:</b> {r_val}</div><div><b>P/E:</b> {pe_val}</div><div><b>قوة الإشارة:</b> {sig_val}</div></div></div>"
        st.markdown(all_html, unsafe_allow_html=True)
else:
    st.markdown("<p style='text-align:center; color:#94a3b8;'>المنصة في وضع الجاهزية والاستعداد المالي. اضغط على زر التحديث بالأعلى لتوليد ومراقبة كامل صفقات السوق السعودي.</p>", unsafe_allow_html=True)
