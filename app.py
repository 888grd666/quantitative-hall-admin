import streamlit as st
import requests

st.set_page_config(page_title="管理员客服后台", page_icon="🎯")

API = "https://quantitative-hall.888grd.workers.dev"
KEY = "sss6668aa996688"
ADMIN_USER = "sss6668"
ADMIN_PASS = "aa996688"

HDR = {"x-admin-key": KEY, "Content-Type": "application/json"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "chat_user_id" not in st.session_state:
    st.session_state.chat_user_id = None

def login_user(username, password):
    if username == ADMIN_USER and password == ADMIN_PASS:
        st.session_state.logged_in = True
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.chat_user_id = None

def get(path):
    try:
        r = requests.get(API + path, headers=HDR, timeout=30)
        return r.json()
    except:
        return []

def post(path, data):
    try:
        r = requests.post(API + path, headers=HDR, json=data, timeout=30)
        return r.json()
    except:
        return {"success": False, "msg": "连接失败"}

st.markdown("""
<style>
.stButton>button {width: 100%;}
.chat-box {background: #f4f7f9; border-radius: 10px; padding: 15px; max-height: 400px; overflow-y: auto;}
.user-msg {background: white; padding: 10px 15px; border-radius: 15px; margin: 8px 0; max-width: 75%;}
.admin-msg {background: #1877f2; color: white; padding: 10px 15px; border-radius: 15px; margin: 8px 0; max-width: 75%; margin-left: 25%; text-align: right;}
.chat-input {display: flex; gap: 10px; align-items: center;}
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; font-size: 60px;'>🎯</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>管理员客服后台</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.form("login_form"):
        st.markdown("### 🔐 管理员登录")
        username = st.text_input("管理员账号", placeholder="请输入账号")
        password = st.text_input("管理员密码", type="password", placeholder="请输入密码")
        submitted = st.form_submit_button("登录", type="primary")
        if submitted:
            if login_user(username, password):
                st.success("登录成功！")
                st.rerun()
            else:
                st.error("账号或密码错误")
    st.markdown("---")
    st.caption(f"账号: {ADMIN_USER} / 密码: {ADMIN_PASS}")
    st.stop()

st.markdown("<h1 style='text-align: center; font-size: 60px;'>🎯</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>客服管理中心</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    st.success("🟢 已登录 | 点击右上角刷新页面")
with col2:
    if st.button("🚪 退出"):
        logout()
        st.rerun()

auto_refresh = st.checkbox("🔄 自动刷新", value=True)

st.markdown("---")

users = get("/api/admin/users")
trades = get("/api/admin/trades")
all_msgs = get("/api/admin/all-messages")

total_pending = len([t for t in (trades if isinstance(trades, list) else []) if t.get("status") == "pending"])

if total_pending > 0:
    st.error(f"🔔 您有 {total_pending} 条交易订单待结算！")
    st.markdown("""
    <audio autoplay>
        <source src="https://assets.mixkit.co/active_storage/sfx/2358/2358-preview.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

if st.session_state.chat_user_id:
    chat_uid = str(st.session_state.chat_user_id)
    chat_user = next((u for u in (users if isinstance(users, list) else []) if str(u.get("id", "")) == chat_uid), None)
    chat_username = chat_user.get("username", "-") if chat_user else "-"
    
    st.markdown("---")
    st.markdown("### 💬 与 " + chat_username + " 聊天")
    
    if st.button("← 返回用户列表"):
        st.session_state.chat_user_id = None
        st.rerun()
    
    chat_msgs = [m for m in (all_msgs if isinstance(all_msgs, list) else []) if str(m.get("user_id", "")) == chat_uid]
    
    st.markdown("#### 聊天记录：")
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for m in chat_msgs:
        content = m.get("content", "")
        t = str(m.get("created_at", ""))[:19] if m.get("created_at") else ""
        if m.get("sender") == "user":
            st.markdown(f'<div class="user-msg"><b>👤 用户</b> <small style="color:gray;">{t}</small><br>{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="admin-msg"><b>📋 客服</b> <small style="color:#ddd;">{t}</small><br>{content}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("#### 发送消息：")
    
    reply = st.text_area("输入回复内容", height=80, key="chat_reply", placeholder="输入回复内容...")
    
    col_send, col_space = st.columns([1, 1])
    with col_send:
        if st.button("📤 发送文字", type="primary"):
            if reply:
                res = post("/api/chat/send", {"userId": chat_uid, "sender": "admin", "content": f"<div>{reply}</div>"})
                if res.get("success"):
                    st.success("✅ 消息已发送")
                    st.rerun()
                else:
                    st.error("❌ 发送失败")
            else:
                st.warning("请输入回复内容")
    
    st.markdown("---")
    st.markdown("**🖼️ 发送图片：**")
    img_url = st.text_input("图片URL", placeholder="输入图片链接...", key="img_url")
    if img_url:
        st.markdown(f'<img src="{img_url}" style="max-width:200px;border-radius:8px;margin:10px 0;">', unsafe_allow_html=True)
        if st.button("🖼️ 发送图片"):
            img_html = f'<img src="{img_url}" style="max-width:150px;border-radius:8px;">'
            res = post("/api/chat/send", {"userId": chat_uid, "sender": "admin", "content": f"<div>{img_html}</div>"})
            if res.get("success"):
                st.success("✅ 图片已发送")
                st.rerun()
            else:
                st.error("❌ 发送失败")
    
    st.markdown("---")
    st.stop()

if users and isinstance(users, list):
    st.subheader(f"👥 用户列表 (共 {len(users)} 人)")
    
    for user in users:
        uid = user.get("id", "-")
        username = user.get("username", "-")
        password = user.get("password", "-")
        real_name = user.get("real_name") or "未填写"
        phone = user.get("phone") or "未绑定"
        uid_code = user.get("uid", "-")
        principal = user.get("principal", 0)
        profit = user.get("profit", 0)
        is_verified = "✅ 已实名" if user.get("is_verified") else "⏳ 未实名"
        created = str(user.get("created_at", ""))[:19] if user.get("created_at") else "-"
        
        user_trades = [t for t in (trades if isinstance(trades, list) else []) if str(t.get("user_id", "")) == str(uid)]
        pending_trades = [t for t in user_trades if t.get("status") == "pending"]
        user_msgs = [m for m in (all_msgs if isinstance(all_msgs, list) else []) if str(m.get("user_id", "")) == str(uid)]
        user_msg_count = len([m for m in user_msgs if m.get("sender") == "user"])
        
        header_text = f"👤 {username} | ID: {uid} | 余额: ¥{principal:.2f}"
        if user_msg_count > 0:
            header_text += f" | 🔔 {user_msg_count} 条新消息"
        
        with st.expander(header_text):
            col_info, col_del = st.columns([3, 1])
            with col_info:
                st.markdown(f"""
                **基本信息:**
                - 账号: `{username}`
                - 密码: `{password}`
                - 姓名: {real_name}
                - 手机: {phone}
                - UID: {uid_code}
                - 实名: {is_verified}
                - 注册时间: {created}
                
                **账户信息:**
                - 💰 余额: ¥{principal:.2f}
                - 📈 盈亏: ¥{profit:.2f}
                - 📊 待结算订单: {len(pending_trades)} 条
                """)
            with col_del:
                st.markdown("**⚠️ 危险操作:**")
                del_user = st.text_input("账号", placeholder="账号", key=f"delu_{uid}")
                del_pwd = st.text_input("密码", type="password", placeholder="密码", key=f"delp_{uid}")
                if st.button("🗑️ 删除", key=f"delbtn_{uid}"):
                    if del_user and del_pwd:
                        res = post("/api/admin/delete-user", {"userId": int(uid), "adminUser": del_user, "adminPass": del_pwd})
                        if res.get("success"):
                            st.success("✅ 已删除")
                            st.rerun()
                        else:
                            st.error(f"❌ {res.get('msg', '失败')}")
                    else:
                        st.warning("输入账号密码")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**💰 账户操作:**")
                add_amount = st.number_input("充值金额", value=0.0, min_value=0.0, step=100.0, format="%.2f", key=f"bal_{uid}")
                if st.button("💰 充值", key=f"adj_{uid}"):
                    if add_amount > 0:
                        res = post("/api/admin/user/balance", {"userId": int(uid), "amount": float(add_amount)})
                        if res.get("success"):
                            st.success(f"✅ +¥{add_amount:.2f}")
                            st.rerun()
                        else:
                            st.error(f"❌ {res.get('msg')}")
                
                set_amount = st.number_input("直接修改余额", value=float(principal), min_value=0.0, step=100.0, format="%.2f", key=f"set_{uid}")
                pwd = st.text_input("管理员密码", type="password", placeholder="密码", key=f"pwd_{uid}")
                if st.button("✅ 确认修改", key=f"setbtn_{uid}"):
                    if pwd:
                        res = post("/api/admin/set-balance", {"userId": int(uid), "balance": float(set_amount), "adminPwd": pwd})
                        if res.get("success"):
                            st.success(f"✅ ¥{set_amount:.2f}")
                            st.rerun()
                        else:
                            st.error("❌ 失败")
            
            with c2:
                st.markdown("**📊 订单结算:**")
                if pending_trades:
                    for trade in pending_trades:
                        tid = trade.get("id")
                        symbol = trade.get("symbol", "-")
                        amount = trade.get("amount", 0)
                        direction = "🟢看涨" if trade.get("direction") == "up" else "🔴看跌"
                        cw, cl = st.columns(2)
                        with cw:
                            if st.button(f"🟢 盈利", key=f"win_{tid}"):
                                res = post("/api/admin/trade/settle", {"tradeId": int(tid), "result": "win"})
                                if res.get("success"):
                                    st.success("✅ 结算成功")
                                    st.rerun()
                        with cl:
                            if st.button(f"🔴 亏损", key=f"loss_{tid}"):
                                res = post("/api/admin/trade/settle", {"tradeId": int(tid), "result": "loss"})
                                if res.get("success"):
                                    st.success("✅ 结算成功")
                                    st.rerun()
                        st.markdown(f"**{symbol}** | ¥{amount:.0f} | {direction}")
                        st.markdown("---")
                else:
                    st.caption("暂无待结算订单")
        
        col_btn, col_space = st.columns([1, 4])
        with col_btn:
            if st.button(f"💬 消息回复 {username}", key=f"chat_btn_{uid}"):
                st.session_state.chat_user_id = uid
                st.rerun()
        
        st.markdown("---")

else:
    st.info("暂无用户数据，请检查后端连接")

st.markdown("---")
st.markdown(f"**账号:** {ADMIN_USER} | **后台:** https://huggingface.co/spaces/666sss/quantitative-hall-admin")

if auto_refresh:
    import time
    time.sleep(10)
    st.rerun()
