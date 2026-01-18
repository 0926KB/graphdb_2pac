# -*- coding: utf-8 -*-
"""
완벽한 수사 보고서 버전 - 진실 주입 스크립트
명확한 인과관계가 담긴 텍스트를 그래프로 변환
"""
import os
import sys
import re
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. 설정 로드
load_dotenv()

# 2. Neo4j 연결
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# 3. [핵심] 탐정을 위한 '완벽한 정답' 텍스트
# 인과관계가 모호하지 않도록 주어와 목적어를 명확히 서술했습니다.
truth_text = """
[사건 개요: 투팍 샤커 살인 사건의 진실]

1996년 9월 7일 라스베가스에서 발생한 투팍 샤커(Tupac Shakur) 살인 사건은 단순한 갱단 전쟁이 아닌, 치밀하게 계획된 청부 살인이었다.

1. 배후와 청부 (The Mastermind)
배드 보이 레코즈(Bad Boy Records)의 설립자인 '퍼프 대디(Puff Daddy)'는 동부와 서부 힙합 전쟁의 승리자가 되길 원했다.
퍼프 대디는 1995년, 크립스(Southside Crips) 갱단의 간부인 '키피 D(Keffe D)'에게 은밀한 제안을 했다.
퍼프 대디는 키피 D에게 "투팍 샤커와 슈그 나잇을 죽여주면 그 대가로 100만 달러(1 Million USD)를 주겠다"고 약속하며 살인을 청부했다.
이로써 퍼프 대디는 이 사건의 실질적인 배후(Mastermind)가 되었다.

2. 실행 계획 (The Setup)
키피 D는 이 제안을 수락했다. 1996년 9월 7일, 마이크 타이슨 경기 후 MGM 호텔 로비에서 투팍이 올랜도 앤더슨(Orlando Anderson)을 폭행하는 사건이 발생했다.
올랜도 앤더슨은 키피 D의 조카였으며, 이 폭행 사건은 살인 계획을 실행에 옮기는 결정적인 명분(Trigger)이 되었다.

3. 범행 도구와 실행 (The Execution)
사건 당일 밤, 키피 D는 흰색 캐딜락 조수석에 탑승했다. 뒷좌석에는 그의 조카 올랜도 앤더슨이 타고 있었다.
키피 D는 미리 준비한 40구경 '글록 22(Glock 22)' 권총을 뒷좌석에 있는 올랜도 앤더슨에게 건네주며 투팍을 쏘라고 지시했다.
흰색 캐딜락이 투팍의 BMW 옆에 멈춰 섰을 때, 올랜도 앤더슨은 건네받은 글록 22로 투팍을 향해 4발의 총탄을 발사했다.
투팍은 치명상을 입고 6일 뒤 사망했다.

4. 결론 (Conclusion)
경찰 수사 결과, 직접 방아쇠를 당긴 실행범은 '올랜도 앤더슨'으로 밝혀졌다.
현장에서 범행을 지휘하고 무기를 제공한 사람은 '키피 D'였다.
그리고 이 모든 것을 돈으로 사주한 최종 배후는 '퍼프 대디'임이 드러났다.
"""

def inject_truth():
    print("=" * 60)
    print("Truth Injection Script - Perfect Investigation Report")
    print("=" * 60)
    
    print("\n[INIT] Preparing to inject the truth...")
    # 기존 그래프를 날리고 새로 쓰고 싶다면 아래 주석을 해제하세요.
    # graph.query("MATCH (n) DETACH DELETE n") 

    # 텍스트 전처리 및 청킹
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [Document(page_content=truth_text)]
    chunks = text_splitter.split_documents(docs)
    print(f"\n[CHUNK] Text split into {len(chunks)} pieces.")

    # LLM 설정 (똑똑한 GPT-4o 사용 권장)
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # [핵심] 추출할 노드와 관계를 명확히 지정해줍니다.
    # LLM에게 "이런 관계를 중점적으로 찾아봐"라고 힌트를 주는 겁니다.
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=[
            "Person", "Rapper", "Producer", "Gang", "Weapon", "Event", "Label", "Location"
        ],
        allowed_relationships=[
            "HIRED_HITMAN",    # 청부하다
            "OFFERED_BOUNTY",  # 현상금을 걸다
            "ORDERED_HIT",     # 살인을 지시하다
            "GAVE_WEAPON",     # 무기를 건네다
            "SHOT_AT",         # 총을 쏘다
            "KILLED",          # 죽이다
            "UNCLE_OF",        # 삼촌 관계
            "MEMBER_OF",       # 조직원
            "BEEF_WITH",       # 적대 관계
            "FOUNDED",         # 설립하다
            "ATTACKED"         # 공격하다
        ]
    )

    print("\n[EXTRACT] AI is extracting the truth from text...")
    print("  (This may take 30-60 seconds...)")
    graph_documents = transformer.convert_to_graph_documents(chunks)
    
    total_nodes = sum(len(d.nodes) for d in graph_documents)
    total_rels = sum(len(d.relationships) for d in graph_documents)
    
    print(f"\n[RESULT] Extracted nodes: {total_nodes}")
    print(f"[RESULT] Extracted relationships: {total_rels}")
    
    # 미리보기
    if graph_documents:
        print("\n[PREVIEW] Sample nodes:")
        for node in graph_documents[0].nodes[:5]:
            print(f"  - ({node.type}: {node.id})")
        
        print("\n[PREVIEW] Sample relationships:")
        for rel in graph_documents[0].relationships[:5]:
            print(f"  - ({rel.source.id}) -[:{rel.type}]-> ({rel.target.id})")

    print("\n[SAVE] Saving to Neo4j database...")
    graph.add_graph_documents(graph_documents)
    
    # 검증
    print("\n" + "=" * 60)
    print("[VERIFY] Key relationships in database:")
    print("=" * 60)
    
    verify = graph.query("""
        MATCH (p)-[r]->(t)
        WHERE p.id CONTAINS 'Puff' OR p.id CONTAINS 'Keffe' OR p.id CONTAINS 'Orlando'
        RETURN p.id as from, type(r) as rel, t.id as to
        LIMIT 10
    """)
    for rec in verify:
        print(f"  {rec['from']} -[:{rec['rel']}]-> {rec['to']}")
    
    print("\n" + "=" * 60)
    print("[DONE] Truth has been recorded!")
    print("Now ask the detective (app.py) about the truth.")
    print("=" * 60)

if __name__ == "__main__":
    inject_truth()

