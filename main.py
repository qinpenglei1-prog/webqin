import streamlit as st
import pandas as pd
import os
import time

# ==========================================
# 1. 系统配置与 VI 设计 (美车怪兽·怪兽绿)
# ==========================================
st.set_page_config(
    page_title="美车怪兽管理系统 Pro",
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义 CSS (把按钮和进度条改成怪兽绿)
st.markdown("""
    <style>
    /* 主色调定义 */
    :root {
        --monster-green: #00E676; 
    }
    /* 按钮样式 */
    div.stButton > button {
        background-color: var(--monster-green);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #00C853;
        color: white;
    }
    /* 侧边栏背景微调 */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    /* 标题颜色 */
    h1, h2, h3 {
        font-family: '微软雅黑';
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 模拟数据库 (用户表 & 客户表)
# ==========================================
FILE_CUSTOMER = "customer_data.csv"

# 模拟用户账号 (实际开发应该放数据库)
# 格式：用户名: {"密码", "角色", "姓名"}
USERS = {
    "boss": {"password": "888", "role": "admin", "name": "老板"},
    "staff1": {"password": "123", "role": "user", "name": "员工小王"},
    "staff2": {"password": "123", "role": "user", "name": "员工小李"},
}

def load_data():
    if not os.path.exists(FILE_CUSTOMER):
        return pd.DataFrame(columns=["姓名", "电话", "车型", "业务类型", "跟进状态", "跟进人", "录入时间"])
    return pd.read_csv(FILE_CUSTOMER)

def save_data(df):
    df.to_csv(FILE_CUSTOMER, index=False)

# ==========================================
# 3. 登录模块 (Session 状态管理)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ''
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ''

def login():
    st.markdown("<h1 style='text-align: center; color: #00E676;'>🦖 美车怪兽内部系统</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("账号")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("安全登录")
            
            if submitted:
                if username in USERS and USERS[username]['password'] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = USERS[username]['role']
                    st.session_state['user_name'] = USERS[username]['name']
                    st.success("登录成功！跳转中...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("账号或密码错误")

def logout():
    st.session_state['logged_in'] = False
    st.rerun()

# ==========================================
# 4. 主系统逻辑
# ==========================================
def main_system():
    # 侧边栏：用户信息
    with st.sidebar:
        # 这里可以用 st.image("logo.png") 换成你的logo
        st.write(f"欢迎你，**{st.session_state['user_name']}**")
        if st.session_state['user_role'] == 'admin':
            st.info("身份：管理员 (BOSS)")
        else:
            st.success("身份：销售专员")
        
        if st.button("退出登录"):
            logout()
            
    # 读取数据
    df = load_data()

    # --- 页面布局：使用 Tab 标签页 ---
    if st.session_state['user_role'] == 'admin':
        tab1, tab2, tab3 = st.tabs(["📊 老板驾驶舱", "📝 客户录入", "📋 数据总表"])
    else:
        # 员工只能看到两个标签
        tab2, tab3 = st.tabs(["📝 客户录入", "📋 我的客户"])
        tab1 = None

    # --- Tab 1: 老板驾驶舱 (仅管理员可见) ---
    if tab1:
        with tab1:
            st.subheader("全公司经营概览")
            # 关键指标
            total_customers = len(df)
            deals = len(df[df['跟进状态'] == '已成交'])
            money = deals * 9800 # 假设客单价9800
            
            m1, m2, m3 = st.columns(3)
            m1.metric("累计客户", total_customers)
            m2.metric("累计成交数", deals)
            m3.metric("预估营收", f"¥{money:,}")
            
            st.divider()
            
            # 图表区
            c1, c2 = st.columns(2)
            with c1:
                st.caption("各状态客户分布")
                if not df.empty:
                    status_counts = df['跟进状态'].value_counts()
                    st.bar_chart(status_counts, color="#00E676")
            with c2:
                st.caption("员工绩效排行")
                if not df.empty:
                    staff_counts = df['跟进人'].value_counts()
                    st.bar_chart(staff_counts)

    # --- Tab 2: 客户录入 (全员可见) ---
    with tab2:
        st.subheader("录入新的销售线索")
        with st.form("add_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("客户姓名")
                phone = st.text_input("联系电话")
                car_type = st.text_input("车型", placeholder="如：宝马5系")
            with col_b:
                biz_type = st.selectbox("意向产品", ["洗车机-普通版", "洗车机-豪华版", "耗材", "其他"])
                status = st.selectbox("跟进状态", ["潜在", "意向", "已成交", "流失"])
            
            submit = st.form_submit_button("提交录入")
            
            if submit:
                if name:
                    new_row = pd.DataFrame({
                        "姓名": [name], "电话": [phone], "车型": [car_type],
                        "业务类型": [biz_type], "跟进状态": [status],
                        "跟进人": [st.session_state['user_name']], # 自动记录是谁录入的
                        "录入时间": [pd.Timestamp.now().strftime('%Y-%m-%d')]
                    })
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.toast(f"✅ 成功录入：{name}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("姓名不能为空")

    # --- Tab 3: 数据列表 (权限控制) ---
    with tab3:
        # 搜索框
        search = st.text_input("🔍 搜索客户...", label_visibility="collapsed")
        
        # 筛选逻辑：老板看全部，员工只看自己的
        if st.session_state['user_role'] == 'admin':
            show_df = df
            st.caption("当前显示：全公司数据")
        else:
            show_df = df[df['跟进人'] == st.session_state['user_name']]
            st.caption("当前显示：仅我的数据")
            
        if search:
            show_df = show_df[show_df.apply(lambda row: search in str(row.values), axis=1)]
            
        st.dataframe(show_df, use_container_width=True, hide_index=True)

# ==========================================
# 程序入口
# ==========================================
if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_system()
    else:
        login()
