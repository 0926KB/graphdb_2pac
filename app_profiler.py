# -*- coding: utf-8 -*-
"""
AI 범죄 프로파일러 - 확률 기반 추론 엔진
관계 가중치를 분석하여 범인일 확률을 계산합니다.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

# 1. 설정 및 연결
load_dotenv()
st.set_page_config(page_title="Criminal Profiler AI", page_icon="⚖️", layout="wide")

st.title("⚖️ AI 범죄 프로파일러 (Probability Engine)")
st.markdown("""
이 에이전트는 **단순 검색**을 넘어, 그래프 내의 관계를 분석하여 **범인일 확률(Culpability Score)**을 계산합니다.
""")

# 사이드바 설정
with st.sidebar:
    st.header("🔍 수사 설정")
    sensitivity = st.slider("수사 강도 (Inference Level)", 0.0, 1.0, 0.0, help="높을수록 창의적인 추론을 합니다.")
    
    st.divider()
    st.markdown("### 📊 관계 가중치")
    st.markdown("""
    | 관계 | 점수 |
    |------|------|
    | `SHOT_AT`, `KILLED` | 99% |
    | `HIRED_HITMAN`, `ORDERED_HIT` | 95% |
    | `GAVE_WEAPON`, `RODE_IN` | 70% |
    | `BEEF_WITH`, `RIVAL_OF` | 30% |
    """)
    
    st.divider()
    neo4j_uri = os.getenv("NEO4J_URI", "Not set")
    st.success(f"✅ DB 연결됨")
    st.caption(f"{neo4j_uri[:30]}...")

# 2. Neo4j & LLM 연결
@st.cache_resource
def get_graph():
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

@st.cache_resource
def get_llm(_sensitivity):
    return ChatOpenAI(model="gpt-4o", temperature=_sensitivity)

graph = get_graph()
llm = get_llm(sensitivity)

def get_evidence_from_db():
    """데이터베이스에서 투팍 관련 모든 증거를 가져옵니다."""
    
    # 투팍을 향한 모든 관계
    query1 = """
    MATCH (a)-[r]->(t)
    WHERE t.id CONTAINS 'Tupac' OR t.id CONTAINS 'tupac'
    RETURN a.id as suspect, type(r) as relation, t.id as victim
    """
    
    # Multi-hop 관계 (A -> B -> Tupac)
    query2 = """
    MATCH path = (a)-[r1]->(b)-[r2]->(t)
    WHERE (t.id CONTAINS 'Tupac' OR t.id CONTAINS 'tupac')
    AND a.id <> b.id
    RETURN a.id as mastermind, type(r1) as relation1, b.id as middleman, type(r2) as relation2, t.id as victim
    LIMIT 20
    """
    
    # Puff Daddy의 모든 관계
    query3 = """
    MATCH (p)-[r]->(t)
    WHERE p.id CONTAINS 'Puff' OR p.id CONTAINS 'Diddy'
    RETURN p.id as suspect, type(r) as relation, t.id as target
    """
    
    # 모든 용의자들
    query4 = """
    MATCH (a)-[r]->(t)
    WHERE (t.id CONTAINS 'Tupac' OR t.id CONTAINS 'tupac')
    AND type(r) IN ['SHOT_AT', 'KILLED', 'HIRED_HITMAN', 'ORDERED_HIT', 'OFFERED_BOUNTY', 
                    'ALLEGEDLY_ORCHESTRATED_MURDER_OF', 'GAVE_WEAPON', 'SUSPECTED_KILLER_OF']
    RETURN DISTINCT a.id as suspect, collect(DISTINCT type(r)) as relations
    """
    
    results = {
        "direct_relations": graph.query(query1),
        "multi_hop": graph.query(query2),
        "puff_daddy": graph.query(query3),
        "suspects": graph.query(query4)
    }
    
    return results

def format_evidence(evidence):
    """증거를 문자열로 포맷팅"""
    formatted = "=== 데이터베이스 증거 ===\n\n"
    
    formatted += "1. 투팍을 향한 직접 관계:\n"
    for r in evidence["direct_relations"][:15]:
        formatted += f"   - {r['suspect']} -[:{r['relation']}]-> {r['victim']}\n"
    
    formatted += "\n2. Multi-hop 관계 (배후 -> 중간자 -> 피해자):\n"
    for r in evidence["multi_hop"][:10]:
        formatted += f"   - {r['mastermind']} -[:{r['relation1']}]-> {r['middleman']} -[:{r['relation2']}]-> {r['victim']}\n"
    
    formatted += "\n3. Puff Daddy의 관계:\n"
    for r in evidence["puff_daddy"][:10]:
        formatted += f"   - {r['suspect']} -[:{r['relation']}]-> {r['target']}\n"
    
    formatted += "\n4. 주요 용의자 목록:\n"
    for r in evidence["suspects"]:
        formatted += f"   - {r['suspect']}: {r['relations']}\n"
    
    return formatted

def analyze_with_llm(question, evidence_str):
    """LLM으로 증거를 분석하여 프로파일링"""
    
    prompt = f"""
    당신은 Neo4j 지식 그래프를 분석하여 범인을 지목하는 'AI 수석 프로파일러'입니다.
    아래 데이터베이스 증거를 분석하여 **범인일 확률**을 계산하세요.

    [⚠️ 추론 규칙 (Scoring Logic)]
    1. **실행범 (The Executor):** `SHOT_AT`, `KILLED`, `SUSPECTED_KILLER_OF` → **확률 99%**
    2. **설계자 (The Mastermind):** `HIRED_HITMAN`, `ORDERED_HIT`, `OFFERED_BOUNTY`, `ALLEGEDLY_ORCHESTRATED_MURDER_OF` → **확률 95%**
    3. **공범 (Accomplice):** `GAVE_WEAPON`, `RODE_IN`, `ORCHESTRATED_MURDER_OF` → **확률 70%**
    4. **동기 보유 (Suspect):** `BEEF_WITH`, `RIVAL_OF`, `ATTACKED` → **확률 30%**

    [데이터베이스 증거]
    {evidence_str}

    [사용자 질문]
    {question}

    [답변 형식]
    ### 🚨 유력 용의자 리포트
    
    1. **[실제 이름]** (역할: 실행범/배후/공범)
       - **범행 확률:** XX%
       - **증거:** 데이터베이스에서 발견된 실제 관계 설명
       - **추론:** 왜 이 사람이 범인인지 논리적으로 설명
    
    (확률 순으로 나열)

    ---
    ### 📊 최종 결론
    - **직접 실행범:** [실제 이름] (확률 XX%)
    - **배후 조종자:** [실제 이름] (확률 XX%)
    - **청부 체인:** A → B → C → 피해자 (실제 이름으로)
    """
    
    response = llm.invoke(prompt)
    return response.content

# 4. 채팅 인터페이스
if "profiler_messages" not in st.session_state:
    st.session_state["profiler_messages"] = [
        {"role": "assistant", "content": "🕵️‍♂️ 사건 파일을 분석할 준비가 되었습니다. 누구를 프로파일링할까요?\n\n**추천 질문:**\n- 투팍 사건의 범인과 배후를 확률 높은 순으로 알려줘\n- 퍼프 대디의 범행 확률은?\n- 올랜도 앤더슨은 왜 용의자야?"}
    ]

for msg in st.session_state.profiler_messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("예: 투팍 사건의 범인과 배후를 확률 높은 순으로 알려줘"):
    st.session_state.profiler_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🕵️‍♂️ 데이터베이스 조회 중..."):
            try:
                # 1. DB에서 증거 수집
                evidence = get_evidence_from_db()
                evidence_str = format_evidence(evidence)
                
                # 디버그: 증거 표시
                with st.expander("🔍 수집된 증거 보기"):
                    st.code(evidence_str)
                
            except Exception as e:
                st.error(f"DB 조회 실패: {e}")
                st.stop()
        
        with st.spinner("🧠 프로파일링 분석 중..."):
            try:
                # 2. LLM으로 분석
                result = analyze_with_llm(prompt, evidence_str)
                st.markdown(result)
                st.session_state.profiler_messages.append({"role": "assistant", "content": result})
            except Exception as e:
                st.error(f"프로파일링 실패: {e}")
