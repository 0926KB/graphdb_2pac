"""
Hip-Hop Noir 추론 엔진
LangChain을 사용하여 자연어 질문을 Cypher 쿼리로 변환하고,
그래프 데이터베이스에서 정보를 추출하여 추론합니다.
"""
import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate

load_dotenv()

# LLM 설정
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Neo4j 그래프 연결
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)


# 🔥 핵심: 탐정 프롬프트 (Detective Prompt)
# LLM에게 단순 검색이 아니라 '추론'을 하도록 강제합니다.
detective_template = """당신은 90년대 힙합 범죄 전문 프로파일러입니다.
Neo4j 그래프 데이터베이스의 정보를 바탕으로 질문에 답하세요.

**중요한 규칙:**
1. 데이터베이스에 정답이 명시적으로 없으면, '관계(Relationships)'를 통해 추론하세요.
2. '살해 동기(Motive)', '갱단 연결(Gang Affiliation)', '과거의 충돌(Past Conflicts)'을 연결하여 유력한 용의자를 지목하세요.
3. 답변은 수사 보고서 형식으로 작성하세요:
   - 증거 1, 증거 2, 증거 3...
   - 관계 분석
   - 동기 분석
   - 결론 및 유력한 용의자

**스키마 정보:**
{schema}

**데이터베이스 쿼리 결과:**
{context}

**질문:** {question}

**답변 (한국어로 작성):**"""

PROMPT = PromptTemplate(
    input_variables=["schema", "context", "question"],
    template=detective_template
)


# GraphCypherQAChain 생성
# 최신 버전에서는 allow_dangerous_requests 파라미터 확인 필요
try:
    # LangChain 최신 버전
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        verbose=True,  # 생각하는 과정 출력
        qa_prompt=PROMPT,
        return_intermediate_steps=True,  # 중간 단계 반환
    )
except TypeError:
    # 일부 버전에서는 allow_dangerous_requests 필요
    try:
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            qa_prompt=PROMPT,
            return_intermediate_steps=True,
            allow_dangerous_requests=True,
        )
    except TypeError:
        # 최신 버전에서는 allow_dangerous_requests 제거됨
        chain = GraphCypherQAChain.from_llm(
            llm=llm,
            graph=graph,
            verbose=True,
            qa_prompt=PROMPT,
            return_intermediate_steps=True,
        )


def ask_detective(question: str) -> dict:
    """
    탐정에게 질문하고 추론 결과를 받습니다.
    
    Args:
        question: 사용자의 질문 (자연어)
        
    Returns:
        dict: {'result': 답변, 'intermediate_steps': 중간 단계 (선택적)}
    """
    try:
        print(f"\n🔍 질문 분석 중: {question}\n")
        result = chain.invoke({"query": question})
        return result
    except Exception as e:
        error_msg = f"수사 도중 오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "result": error_msg,
            "intermediate_steps": []
        }


def get_graph_schema() -> str:
    """그래프 데이터베이스의 스키마 정보를 반환합니다."""
    try:
        return graph.get_schema
    except:
        # 대체 방법
        node_info = graph.query("""
            CALL db.schema.nodeTypeProperties()
            YIELD nodeType, propertyName, propertyTypes
            RETURN nodeType, collect(propertyName) as properties
        """)
        
        rel_info = graph.query("""
            CALL db.schema.relTypeProperties()
            YIELD relType, propertyName, propertyTypes
            RETURN relType, collect(propertyName) as properties
        """)
        
        schema_str = "Nodes: " + str(node_info) + "\nRelationships: " + str(rel_info)
        return schema_str


if __name__ == "__main__":
    # 테스트
    test_questions = [
        "투팍과 사이가 안 좋았던 사람은 누구야?",
        "Death Row Records와 대립했던 갱단은 어디야?",
        "투팍을 쏜 범인이 데이터에 명시돼 있어? 없다면, 폭행 사건과 갱단 관계를 근거로 가장 유력한 용의자를 추론해줘."
    ]
    
    print("🕵️‍♂️ Hip-Hop Noir 추론 엔진 테스트\n")
    print(f"연결된 데이터베이스: {os.getenv('NEO4J_URI', 'Not set')}\n")
    
    for i, q in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"테스트 질문 {i}: {q}")
        print('='*60)
        result = ask_detective(q)
        print(f"\n📋 답변: {result.get('result', 'No result')}\n")

