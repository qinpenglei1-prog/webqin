import streamlit as st
import pandas as pd
import os

# --- 基础设置 ---
st.set_page_config(page_title="我的CRM系统", layout="wide") 
FILE_NAME = "customer_data.csv"

# --- 数据读写函数 ---
def load_data():
    if not os.path.exists(FILE_NAME):
        data = {
            "姓名": ["张三", "李四"],
            "电话": ["13800138000", "13900139000"],
            "公司": ["建设集团", "科技公司"],
            "跟进状态": ["已成交", "潜在客户"],
            "备注": ["已签一年合同", "对Q3产品感兴趣"],
            "添加日期": ["2026-01-08", "2026-01-08"]
        }
        return pd.DataFrame(data)
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

df = load_data()

# ============================
#    左侧边栏
# ============================
st.sidebar.header("📝 录入新客户")
st.sidebar.write("在下方输入新的销售线索详情。")

with st.sidebar.form("add_customer_form", clear_on_submit=True):
    name = st.text_input("姓名", placeholder="例如：张三")
    phone = st.text_input("电话", placeholder="例如：138xxxxxxxxx")
    company = st.text_input("公司/单位", placeholder="例如：某某公司")
    status = st.selectbox("跟进状态", ["潜在客户", "意向强烈", "已成交", "已流失"])
    notes = st.text_area("备注（选填）", placeholder="会议记录、关键需求等...")
    
    submitted = st.form_submit_button("保存客户", type="primary")
    if submitted:
        if name and phone:
            new_data = pd.DataFrame({
                "姓名": [name],
                "电话": [phone],
                "公司": [company],
                "跟进状态": [status],
                "备注": [notes],
                "添加日期": [pd.Timestamp.now().strftime('%Y-%m-%d')]
            })
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.sidebar.success(f"已添加：{name}")
            st.rerun()
        else:
            st.sidebar.error("姓名和电话是必填项！")

# ============================
#    主页面区域
# ============================
st.subheader("📊 数据概览")

total_customers = len(df)
deals_won = len(df[df["跟进状态"]=="已成交"])
in_pipeline = len(df[df["跟进状态"].isin(["潜在客户", "意向强烈"])])
win_rate = (deals_won / total_customers * 100) if total_customers > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("总客户数", total_customers)
col2.metric("已成交", deals_won, delta=f"+{deals_won} 本月新")
col3.metric("跟进中", in_pipeline)
col4.metric("成交率", f"{win_rate:.1f}%")

st.divider() 

col_header, col_search = st.columns([2, 1])
with col_header:
    st.header("📋 最近客户列表")
with col_search:
    search_term = st.text_input("🔍 搜索客户...", placeholder="输入姓名或公司查找", label_visibility="collapsed")

if search_term:
    filtered_df = df[df.apply(lambda row: search_term.lower() in str(row.values).lower(), axis=1)]
else:
    filtered_df = df

display_df = filtered_df[["姓名", "电话", "公司", "跟进状态", "添加日期", "备注"]]
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True, 
    column_config={
        "跟进状态": st.column_config.SelectboxColumn("跟进状态", options=["潜在客户", "意向强烈", "已成交", "已流失"], required=True),
        "备注": st.column_config.TextColumn("备注/详情", width="large"),
        "添加日期": st.column_config.DateColumn("添加日期", format="YYYY-MM-DD")
    }
)
