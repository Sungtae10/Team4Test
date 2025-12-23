import streamlit as st
import time
import pandas as pd
import datetime
import altair as alt

# 1. 페이지 설정
st.set_page_config(
    page_title="Meeting Agent",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 스타일링 (네이버 스타일 + 다크모드 완벽 해결 + 가독성 강화)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');
    
    /* [핵심] 다크모드일 때도 무조건 흰색 배경/검은 글씨로 고정 */
    [data-testid="stAppViewContainer"] {
        background-color: #f5f6f7 !important;
        color: #333333 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0) !important;
    }
    
    /* 기본 폰트 설정 */
    .stApp {
        font-family: 'Nanum Gothic', sans-serif;
    }

    /* 텍스트 색상 강제 지정 (다크모드 방지) */
    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: #1e1e23 !important;
    }
    .stCaption, .caption {
        color: #888888 !important;
    }

    /* 입력창 스타일 (다크모드에서도 흰색 유지) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #dadada !important;
    }

    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #ffffff;
        border-bottom: 1px solid #e3e7eb;
        padding: 0 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 54px;
        background-color: transparent;
        border: none;
        color: #777 !important;
        font-size: 15px;
        font-weight: 600;
        margin-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #03C75A !important;
        border-bottom: 3px solid #03C75A !important;
    }

    /* 버튼 스타일 */
    div.stButton > button[type="primary"] {
        background-color: #03C75A !important;
        border: 1px solid #03cf5d !important;
        color: white !important;
        font-weight: 800 !important;
    }
    div.stButton > button[type="secondary"] {
        background-color: white !important;
        border: 1px solid #d1d1d1 !important;
        color: #333 !important;
    }

    /* 리포트 헤더 */
    .report-header { 
        font-size: 18px; 
        font-weight: bold; 
        color: #333 !important; 
        margin-bottom: 10px; 
        border-left: 4px solid #03C75A; 
        padding-left: 10px; 
    }
    
    /* 카드 스타일 */
    .strategy-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e3e7eb;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .sub-text { font-size: 14px; color: #666 !important; line-height: 1.6; }

    /* 뱃지 */
    .badge-high { background-color: #ffe3e3; color: #c0392b !important; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-med { background-color: #fff3cd; color: #856404 !important; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }
    .badge-low { background-color: #d4edda; color: #155724 !important; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; }

</style>
""", unsafe_allow_html=True)

# --- 데이터 및 상태 초기화 ---
if 'page' not in st.session_state: st.session_state.page = 'login'
if 'selected_meeting' not in st.session_state: st.session_state.selected_meeting = None
if "approvals" not in st.session_state:
    st.session_state.approvals = [
        {"id": 1, "item": "Q1 마케팅 집행 예산안", "owner": "김성태", "status": "대기", "amount": "₩50,000,000", "desc": "SNS 및 검색 광고비 증액분"},
        {"id": 2, "item": "AWS 서버 스케일업 비용", "owner": "박훈용", "status": "대기", "amount": "₩12,500,000", "desc": "베타 오픈 대비 인스턴스 확보"},
        {"id": 3, "item": "UI/UX 외주 용역 계약", "owner": "전혜나", "status": "완료", "amount": "₩8,000,000", "desc": "아이콘 및 일러스트 제작"},
    ]
if "analysis_done" not in st.session_state: st.session_state.analysis_done = False

HISTORY_DB = [
    {"id": 1, "title": "Q4 마케팅 성과 리뷰", "date": "2024.12.22", "type": "Marketing", "duration": "58분", "summary": "SNS 광고 효율 15% 증가, 예산 증액 확정"},
    {"id": 2, "title": "백엔드 API 긴급 점검", "date": "2024.12.21", "type": "DevOps", "duration": "35분", "summary": "로그인 지연 이슈 해결, Redis 도입 결정"},
    {"id": 3, "title": "신규 앱 UI/UX 디자인 회의", "date": "2024.12.20", "type": "Design", "duration": "1시간 20분", "summary": "다크모드 컬러셋 확정, 아이콘 스타일 변경"},
]
TEAM_MEMBERS = ["김성태 (PM)", "고영후 (Dev)", "공채헌 (Dev)", "박지성 (Fullstack)", "박훈용 (Infra)", "전혜나 (Design)"]

# ==========================================
# 🟩 [Page 0] 로그인
# ==========================================
def show_login_page():
    st.write("")
    st.write("")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("""
            <div style="text-align:center; margin-bottom:30px;">
                <h1 style="color:#03C75A !important; font-size:40px; margin-bottom:10px;">Meeting Agent</h1>
                <p style="color:#999 !important; font-size:14px;">Enterprise Collaboration Suite v5.3</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.text_input("아이디", placeholder="사번 또는 이메일 입력")
            st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
            st.checkbox("로그인 상태 유지")
            st.write("")
            if st.button("로그인", type="primary", use_container_width=True):
                with st.spinner("접속 중..."): time.sleep(0.5)
                st.session_state.page = 'home'
                st.rerun()
            
            st.markdown("""
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 20px; font-size: 13px; color: #8e8e8e !important;">
                <span>비밀번호 찾기</span> | <span>아이디 찾기</span> | <span>회원가입</span>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 🏠 [Page 1] 홈 대시보드
# ==========================================
def show_homepage():
    with st.sidebar:
        st.markdown("### Meeting Agent")
        st.caption("Ver 5.3.0")
        st.markdown("---")
        st.write("👤 **김성태 PM**님")
        st.caption("전략기획팀 | 팀장")
        st.markdown("---")
        if st.button("로그아웃", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()

    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("워크스페이스")
        st.caption(f"오늘의 업무 현황입니다. | {datetime.date.today().strftime('%Y년 %m월 %d일')}")
    with c2:
        st.write("")
        if st.button("➕ 새 회의 시작", type="primary", use_container_width=True):
            st.session_state.page = 'app'
            st.rerun()

    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("이번 주 회의", "14건", "+3")
        m2.metric("결재 대기", "2건", "Urgent")
        m3.metric("남은 예산", "₩15.2M", "-20%")
        m4.metric("팀 성과 지수", "92.5", "+1.2")

    st.write("")
    
    col_left, col_right = st.columns([1.2, 1.8])
    with col_left:
        with st.container(border=True):
            st.subheader("📊 프로젝트 진행률")
            source = pd.DataFrame({"category": ["완료", "진행중", "지연"], "value": [65, 25, 10]})
            base = alt.Chart(source).encode(theta=alt.Theta("value", stack=True))
            pie = base.mark_arc(outerRadius=100, innerRadius=60).encode(
                color=alt.Color("category", scale=alt.Scale(domain=["완료", "진행중", "지연"], range=["#03C75A", "#8ce99a", "#adb5bd"])),
                tooltip=["category", "value"]
            )
            text = base.mark_text(radius=120).encode(
                text=alt.Text("value", format=".0f"),
                order=alt.Order("value", sort="descending"),
                color=alt.value("black")
            )
            st.altair_chart(pie + text, use_container_width=True)

    with col_right:
        with st.container(border=True):
            c_head1, c_head2 = st.columns([3, 1])
            c_head1.subheader("🗂️ 최근 회의 기록")
            c_head2.caption("전체보기 >")
            
            for meeting in HISTORY_DB:
                with st.container():
                    c_icon, c_info, c_btn = st.columns([0.5, 3.5, 1])
                    with c_icon: st.markdown("📄")
                    with c_info:
                        st.markdown(f"**{meeting['title']}**")
                        st.caption(f"{meeting['type']} | {meeting['date']} | {meeting['duration']}")
                    with c_btn:
                        if st.button("상세", key=f"d_{meeting['id']}", use_container_width=True):
                            st.session_state.selected_meeting = meeting
                            st.session_state.page = 'detail'
                            st.rerun()
                    st.divider()

# ==========================================
# 🔎 [Page 2] 상세 분석
# ==========================================
def show_detail_page():
    data = st.session_state.selected_meeting
    with st.sidebar:
        if st.button("⬅️ 뒤로가기", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    st.title(f"{data['title']}")
    st.caption(f"문서번호: 2024-REQ-{data['id']:03d} | 생성일: {data['date']}")

    t1, t2, t3 = st.tabs(["📝 핵심 요약", "📊 데이터 분석", "✅ Action Item"])
    with t1:
        st.success(f"**요약:** {data['summary']}")
        st.markdown("**상세 내용:** 회의 초반 10분간 성과 브리핑 진행...")
    with t2:
        c1, c2 = st.columns(2)
        c1.metric("발언 점유율", "김성태 (45%)", "Highest")
        c2.metric("긍정어 빈도", "85회", "High")
        chart_data = pd.DataFrame({'Time': [1,2,3,4,5], 'Score': [3,5,4,6,5]})
        st.line_chart(chart_data)
    with t3:
        st.checkbox("경영지원팀 예산안 전달", value=True)
        st.button("📥 PDF 다운로드", type="primary")

# ==========================================
# 🚀 [Page 3] 메인 앱 (전략 리포트 대폭 강화!)
# ==========================================
def show_app_page():
    with st.sidebar:
        if st.button("⬅️ 나가기", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()
        st.markdown("---")
        st.selectbox("진행자", TEAM_MEMBERS, label_visibility="collapsed")
        st.caption("현재 회의 세션이 기록되고 있습니다.")
    
    st.title("Q1 신규 서비스 런칭 전략 회의")
    st.caption("참석자: 김성태, 고영후, 박훈용, 전혜나 | 2024.12.23 14:00")

    tab1, tab2, tab3, tab4 = st.tabs(["1. 회의 준비", "2. 실시간 진행", "3. 전략 리포트", "4. 결재 관리"])

    with tab1:
        c1, c2 = st.columns(2)
        c1.info("⚠️ **이슈:** AWS 예산 초과")
        c2.success("📌 **식순:** 비용 절감 -> API 배포")

    with tab2:
        col_rec, col_chat = st.columns(2)
        with col_rec:
            st.subheader("실시간 기록")
            if st.toggle("녹음 시작"):
                st.write("**김성태**: 회의 시작하겠습니다.")
        with col_chat:
            st.subheader("AI 비서")
            st.chat_input("질문 입력...")

    # [탭 3] 전략 리포트 심화
    with tab3:
        c_head, c_btn = st.columns([3, 1])
        c_head.subheader("📊 AI Strategic Report")
        if c_btn.button("⚡ 심층 분석 실행", type="primary", use_container_width=True):
            with st.spinner("AI가 대화 맥락, 감정, 리스크 요인을 종합 분석 중입니다..."):
                time.sleep(1.5)
            st.session_state.analysis_done = True
        
        if st.session_state.analysis_done:
            # 1. 종합 요약 (Executive Summary)
            st.markdown('<div class="report-header">Executive Summary (종합 요약)</div>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("""
                * **결정 사항:** 마케팅 확장을 보류하고 **'서버 안정화'**를 최우선 과제로 선정함.
                * **주요 이슈:** 베타 오픈 직전 트래픽 스파이크에 대한 대비책이 부족하다는 지적.
                * **향후 계획:** 다음 주까지 RI 계약 체결 및 부하 테스트(Load Test) 완료 예정.
                """)
            
            st.write("")
            
            # 2. 상세 전략 및 리스크 (2단 분리)
            col_strat, col_risk = st.columns([1, 1])
            
            with col_strat:
                st.markdown('<div class="report-header">Future Strategy (향후 전략)</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="strategy-card">
                    <strong style="color:#03C75A;">[Short-term] 인프라 최적화</strong><br>
                    <span class="sub-text">- 불필요한 인스턴스 정리 및 Auto-scaling 정책 재수립<br>- 예상 비용 절감 효과: 월 250만원</span><br><br>
                    <strong style="color:#333;">[Mid-term] 사용자 경험 개선</strong><br>
                    <span class="sub-text">- 로그인 속도 0.5초 이내 단축 목표<br>- 에러 로그 모니터링 시스템(Sentry) 도입</span>
                </div>
                """, unsafe_allow_html=True)

            with col_risk:
                st.markdown('<div class="report-header">Risk Assessment (리스크 분석)</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="strategy-card">
                    <div style="margin-bottom:8px;">
                        <span class="badge-high">High Risk</span> <strong style="color:#333;">예산 초과</strong>
                        <div class="sub-text">현재 추세라면 Q1 예산 15% 초과 예상. 긴급 예산 조정 필요.</div>
                    </div>
                    <div style="margin-bottom:8px;">
                        <span class="badge-med">Medium Risk</span> <strong style="color:#333;">보안 취약점</strong>
                        <div class="sub-text">결제 모듈 연동 시 SSL 인증서 갱신 이슈 확인됨.</div>
                    </div>
                    <div>
                        <span class="badge-low">Low Risk</span> <strong style="color:#333;">일정 지연</strong>
                        <div class="sub-text">디자인 리소스 전달이 1일 지연되었으나 개발 일정엔 영향 없음.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")

            # 3. 상세 업무 분장 (테이블 형식)
            st.markdown('<div class="report-header">Action Plan (상세 업무 분장)</div>', unsafe_allow_html=True)
            
            # DataFrame으로 깔끔하게 표현
            task_df = pd.DataFrame([
                {"담당자": "김성태 (PM)", "업무": "추가 예산 기안 작성 및 결재 상신", "마감일": "2024-12-24", "우선순위": "높음"},
                {"담당자": "박훈용 (Infra)", "업무": "AWS RI 계약 체결 및 비용 보고서", "마감일": "2024-12-26", "우선순위": "높음"},
                {"담당자": "고영후 (Dev)", "업무": "로그인 API 핫픽스 배포", "마감일": "2024-12-25", "우선순위": "중간"},
                {"담당자": "전혜나 (Design)", "업무": "앱스토어 스크린샷 리사이징", "마감일": "2024-12-28", "우선순위": "낮음"},
                {"담당자": "공채헌 (Dev)", "업무": "어드민 대시보드 UI 개선", "마감일": "2024-12-30", "우선순위": "중간"},
                {"담당자": "박지성 (Fullstack)", "업무": "DB 인덱싱 최적화", "마감일": "2024-12-27", "우선순위": "높음"},
            ])
            st.dataframe(
                task_df, 
                use_container_width=True,
                column_config={
                    "우선순위": st.column_config.SelectboxColumn(
                        "우선순위",
                        options=["높음", "중간", "낮음"],
                        required=True,
                    )
                }
            )
            
            st.caption("💡 위 테이블은 수정 가능하며, 수정 내용은 DB에 자동 반영됩니다.")

    with tab4:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.subheader("📅 캘린더")
            st.date_input("날짜", datetime.date.today())
        with c2:
            st.subheader("✅ 결재 센터")
            for idx, item in enumerate(st.session_state.approvals):
                with st.container(border=True):
                    st.write(f"**{item['item']}** ({item['status']})")
                    if item['status'] == '대기':
                        if st.button("승인", key=idx):
                            st.session_state.approvals[idx]['status'] = "완료"
                            st.rerun()

# ==========================================
# 🔄 라우터
# ==========================================
if st.session_state.page == 'login': show_login_page()
elif st.session_state.page == 'home': show_homepage()
elif st.session_state.page == 'detail': show_detail_page()
elif st.session_state.page == 'app': show_app_page()