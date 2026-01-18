"""
Hip-Hop Noir 수사 본부 - Streamlit 웹 인터페이스
"""
import streamlit as st
from detective import ask_detective

# 페이지 설정
st.set_page_config(
    page_title="Hip-Hop Noir | Data Detective",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바
with st.sidebar:
    st.title("🕵️‍♂️ Hip-Hop Noir")
    st.markdown("### 수사 본부")
    st.markdown("---")
    
    st.markdown("""
    **사용 방법:**
    1. 아래 입력창에 질문을 입력하세요
    2. 자연어로 질문 가능 (예: '투팍을 누가 죽였어?')
    3. 추론이 필요한 질문 추천
    4. Enter를 누르거나 '수사 시작' 버튼을 클릭하세요
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 예시 질문")
    example_questions = [
        "투팍과 사이가 안 좋았던 사람은 누구야?",
        "Death Row Records와 대립했던 갱단은 어디야?",
        "투팍 사망 당일 MGM Grand에서 무슨 일이 있었어?",
        "가장 유력한 용의자는 누구고 왜?",
        "갱단 간 전쟁과 투팍 사건의 연관성은?",
    ]
    
    for example in example_questions:
        if st.button(f"📌 {example[:30]}...", key=f"example_{hash(example)}", use_container_width=True):
            st.session_state['question'] = example

# 메인 영역
st.title("🕵️‍♂️ Hip-Hop Noir: Data Detective")
st.markdown("### 90년대 힙합 씬 범죄 추론 시스템")
st.markdown("---")

# 세션 상태 초기화
if 'history' not in st.session_state:
    st.session_state['history'] = []

# 질문 입력
col1, col2 = st.columns([5, 1])

with col1:
    question = st.text_input(
        "🔍 질문을 입력하세요:",
        value=st.session_state.get('question', ''),
        key='input_question',
        placeholder="예: 투팍 사건의 가장 유력한 용의자는 누구인가?"
    )

with col2:
    submit_button = st.button("수사 시작", type="primary", use_container_width=True)

# 질문 처리
if submit_button or (question and question not in [h['question'] for h in st.session_state['history']]):
    if question.strip():
        # 중복 체크
        if any(h['question'] == question for h in st.session_state['history']):
            st.warning("이미 수사한 질문입니다. 아래 기록을 확인하세요.")
        else:
            with st.spinner("⏳ 데이터베이스 조회 및 추론 중... (잠시만 기다려주세요)"):
                result = ask_detective(question)
                answer = result.get('result', '답변을 생성할 수 없습니다.')
                
                # 히스토리에 추가
                st.session_state['history'].append({
                    'question': question,
                    'answer': answer,
                    'intermediate_steps': result.get('intermediate_steps', [])
                })
                
                st.session_state['question'] = ''  # 입력창 초기화
                st.rerun()

# 대화 히스토리 표시
if st.session_state['history']:
    st.markdown("---")
    st.markdown("### 📋 수사 기록")
    
    # 최신부터 표시
    for i, record in enumerate(reversed(st.session_state['history']), 1):
        with st.expander(f"🔍 질문 {len(st.session_state['history']) - i + 1}: {record['question']}", expanded=(i == 1)):
            st.markdown("**📋 프로파일러 보고서:**")
            st.markdown(record['answer'])
            
            # Cypher 쿼리 표시 (접을 수 있음)
            if record.get('intermediate_steps'):
                with st.expander("🔧 실행된 Cypher 쿼리 (디버그)"):
                    for step in record['intermediate_steps']:
                        if 'query' in step:
                            st.code(step['query'], language='cypher')

# 히스토리 초기화 버튼
if st.session_state['history']:
    st.markdown("---")
    if st.button("🗑️ 수사 기록 삭제", type="secondary"):
        st.session_state['history'] = []
        st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Hip-Hop Noir Data Detective | Powered by Neo4j + LangChain + GPT-4o</small>
</div>
""", unsafe_allow_html=True)

