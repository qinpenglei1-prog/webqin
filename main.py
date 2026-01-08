import streamlit as st
import pandas as pd
import os

# --- 基础设置 ---
st.set_page_config(page_title="怪兽洗车CRM", layout="wide", page_icon="🚗")
FILE_NAME = "customer_data.csv"

# --- 数据读写函数 ---
def load_data():
    if not os.path.exists(FILE_NAME):
        return pd.DataFrame(columns=["姓名", "电话", "公司", "跟进状态", "备注", "添加日期"])
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

df = load_data()

# ============================
#    手机端专门优化：侧边栏提示
# ============================
# 这一行字只会在主界面显示，提醒你去点左上角的箭头
st.caption("👉 点左上角 **>** 箭头录入新客户")

# ============================
#    侧边栏：录入新客户
# ============================
with st.sidebar:
    st.header("📝 录入新客户")
    with st.form("add_customer_form", clear_on_submit=True):
        name = st.text_input("姓名", placeholder="例如：张三")
        phone = st.text_input("电话", type="default") # 手机上输入数字方便点
        company = st.text_input("车型/备注", placeholder="例如：奥迪A6") # 把公司改成车型更实用
        status = st.selectbox("状态", ["潜在", "意向", "成交", "流失"]) # 缩短字数适配手机
        
        submitted = st.form_submit_button("保存", type="primary")
        if submitted:
            if name:
                new_data = pd.DataFrame({
                    "姓名": [name],
                    "电话": [phone],
                    "公司": [company],
                    "跟进状态": [status],
                    "备注": [company], # 备注跟车型同步
                    "添加日期": [pd.Timestamp.now().strftime('%m-%d')] # 日期只留月-日
                })
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"已存：{name}")
                st.rerun()
            else:
                st.error("写个名字！")

# ============================
#    主页面：更紧凑的手机布局
# ============================
st.subheader("📊 经营概况")

# 计算数据
total = len(df)
deals = len(df[df["跟进状态"]=="成交"])
pipeline = len(df[df["跟进状态"].isin(["潜在", "意向"])])
rate = int((deals / total * 100)) if total > 0 else 0

# --- 布局优化：改成 2x2 排列 ---
# 这样手机上不会竖着排成一长条
c1, c2 = st.columns(2)
with c1:
    st.metric("总客数", total)
    st.metric("跟进中", pipeline)
with c2:
    st.metric("已成交", deals)
    st.metric("成交率", f"{rate}%")

st.divider() 

# --- 列表优化 ---
c_head, c_search = st.columns([1, 1.5])
with c_head:
    st.subheader("📋 客户表")
with c_search:
    search = st.text_input("搜", placeholder="搜姓名...", label_visibility="collapsed")

if search:
    show_df = df[df['姓名'].str.contains(search, na=False)]
else:
    show_df = df

# 只展示最核心的列，防止手机屏幕撑爆
# 隐藏了 "添加日期" 和 "备注"，只看 姓名-电话-状态-车型
st.dataframe(
    show_df[["姓名", "电话", "公司", "跟进状态"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "姓名": st.column_config.TextColumn("姓名", width="small"),
        "电话": st.column_config.TextColumn("电话", width="small"),
        "公司": st.column_config.TextColumn("车型", width="small"),
        "跟进状态": st.column_config.SelectboxColumn(
            "状态", 
            options=["潜在", "意向", "成交", "流失"],
            width="small"
        )
    }
)
