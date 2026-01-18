# -*- coding: utf-8 -*-
"""
Hip-Hop Noir Detective - 자연어 질문 → Cypher 쿼리 → 답변 챗봇
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# 1. 환경 변수 로드 (.env 파일에서 접속 정보 가져옴)
load_dotenv()

# 2. 페이지 설정
st.set_page_config(page_title="Hip-Hop Noir Detective", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ 90s Hip-Hop Noir Investigator")
st.caption("Neo4j 지식 그래프를 바탕으로 사건을 재구성합니다.")
st.markdown("---")

# 3. 시스템 연결 체크
if not os.getenv("OPENAI_API_KEY") or not os.getenv("NEO4J_URI"):
    st.error("🔴 .env 파일 설정이 감지되지 않았습니다. API Key와 DB 주소를 확인하세요.")
    st.stop()

# 4. 체인 생성 (리소스 캐싱)
@st.cache_resource
def get_chain():
    # LLM 설정 (똑똑한 GPT-4o 권장)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Neo4j 연결
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    # ★ 탐정 페르소나 프롬프트 (여기가 핵심!)
    # LLM에게 "넌 단순한 검색기가 아니라 탐정이야"라고 최면을 겁니다.
    template = """
    당신은 1990년대 힙합 범죄 사건을 전문으로 다루는 시니컬한 프로파일러입니다.
    Neo4j 그래프 데이터베이스에 저장된 '사실(Fact)'만을 근거로 대답해야 합니다.
    
    [지시사항]
    1. 사용자의 질문을 분석하여 관련된 노드(Rapper, Gang, Event)와 관계(BEEF_WITH, ATTACKED)를 찾으세요.
    2. 데이터베이스에 명시된 정보가 없다면 "관련 기록을 찾을 수 없습니다"라고 답하세요.
    3. 답변은 느와르 영화의 독백처럼 서술하고, 찾은 단서(증거)를 구체적으로 언급하세요.
    4. 만약 '투팍이 누구를 죽였다(KILLED)' 같은 이상한 데이터가 있다면, "데이터상으로는 그렇게 나오지만, 기록의 오류일 수 있습니다"라고 덧붙이세요.
    
    [데이터 스키마 정보]
    Nodes: Rapper, Person, Gang, Location, Event, Label
    Relationships: BEEF_WITH, ATTACKED, KILLED, LOCATED_IN, MEMBER_OF, FRIEND_WITH
    
    질문: {question}
    
    Cypher 쿼리 생성 결과와 DB 검색 결과를 종합하여 답변하세요.
    """
    
    PROMPT = PromptTemplate(input_variables=["question"], template=template)
    
    # 체인 생성 (Natural Language -> Cypher -> Result -> Answer)
    chain = GraphCypherQAChain.from_llm(
        llm, 
        graph=graph, 
        verbose=True, # 터미널에 에이전트의 생각(쿼리)을 보여줍니다
        qa_prompt=PROMPT,
        allow_dangerous_requests=True # Cypher 실행 허용
    )
    return chain

chain = get_chain()

# 5. 채팅 인터페이스 구현
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "어떤 사건이 궁금한가? 투팍? 비기? 아니면 라스베가스의 그날 밤?"}
    ]

# 이전 대화 출력
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력 처리
if prompt := st.chat_input("수사관님, 질문을 입력하세요..."):
    # 사용자 질문 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # 에이전트 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("사건 기록 뒤지는 중... 🔍"):
            try:
                # 여기서 LLM이 그래프를 탐색합니다
                response = chain.invoke(prompt)
                msg = response['result']
                
                st.write(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
                
            except Exception as e:
                st.error(f"수사 도중 오류 발생: {e}")
                st.caption("Tip: 질문이 너무 복잡하면 단계를 나누어 질문해보세요.")
