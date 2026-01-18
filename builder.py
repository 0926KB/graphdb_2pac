# -*- coding: utf-8 -*-
"""
Hip-Hop Noir - 투팍 사건 그래프 구축 스크립트
"""
import os
import re
import sys
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document

# Windows 콘솔 UTF-8 설정
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

# 3. 긴 텍스트 입력 (투팍 사건 상세 내용)
raw_text = """
1996년 9월 7일 밤 투팍은 마이크 타이슨의 경기를 보러 가기 위해 라스베가스에 있었다.
올랜도 앤더슨은 이전 레이크우드 쇼핑몰에서 데스 로우와 연관되어 있는 파이리츠 갱단과 싸움을 벌인 전적이 있었다.
올랜도 앤더슨은 사우스사이드 크립스(Southside Crips) 갱단의 멤버였다.
MGM 호텔 로비에서 트레이 디와 같이 동행하고 있던 투팍은 올랜도 앤더슨을 발견하자 바로 달려들어 그를 공격했다.
슈그 나이트도 이 폭행에 가담했다.
오후 11시 15분, 투팍과 슈그 나이트가 탄 차량 우측으로 흰색 캐딜락이 조용히 다가왔다.
캐딜락에서 누군가 글록 22를 꺼내들고 이들을 향해 집중사격을 가했다.
투팍은 네 발의 총탄을 맞았고, 결국 향년 25세라는 너무나도 젊은 나이에 세상을 떠나고 말았다.
투팍은 Death Row Records 소속이었으며, 슈그 나이트가 이 레이블의 CEO였다.
투팍은 Mob Piru Bloods 갱단과 연관이 있었다.

당시 컴튼 지역에서 마약 거래로 유명했던 갱단 멤버이자 올랜도 앤더슨의 삼촌인 두에인 "키피 D" 데이비스는 모든 것을 전부 알고 있는 사람이었다.
키피 D는 사우스사이드 크립스의 멤버였다.
키피 D는 2024년에 투팍 살해 혐의로 체포되었다.

퍼프 대디(P. Diddy)는 Bad Boy Records의 CEO였다.
노토리어스 비아이지(Notorious B.I.G., 비기)는 Bad Boy Records 소속이었다.
투팍과 비기는 원래 친구였으나, 1994년 투팍이 뉴욕 쿼드 스튜디오에서 총격을 당한 후 사이가 틀어졌다.
투팍은 비기가 1994년 총격 사건의 배후라고 의심했다.
투팍은 1996년 'Hit Em Up'이라는 디스곡으로 비기를 맹비난했다.

퍼프 대디는 그들이 투팍과 슈그 나이트를 죽이면 백만 불을 넘기겠다고 제안했다고 한다.
2024년 7월 25일, 법원 문서를 통해 퍼프 대디가 암살자에게 백만 달러를 지급해 투팍 샤커 암살을 의뢰했다고 밝혀졌다.
비기는 1997년 3월 9일 로스앤젤레스에서 총격을 받고 사망했다. 이 사건도 미해결 상태다.
"""

# 4. 전처리 (위키 주석 [1], [편집] 같은 노이즈 제거)
cleaned_text = re.sub(r"\[\d+\]|\[편집\]", "", raw_text)

def process_graph():
    print("=" * 60)
    print("Hip-Hop Noir - Graph Builder")
    print("=" * 60)
    
    # 기존 데이터 삭제 (선택적)
    # print("\n[CLEAN] Deleting existing data...")
    # graph.query("MATCH (n) DETACH DELETE n")

    print("\n[CHUNK] Text chunking...")
    # 텍스트가 기니까 1000자 단위로 자르고, 문맥 유지를 위해 200자씩 겹치게 함
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = [Document(page_content=cleaned_text)]
    chunks = text_splitter.split_documents(docs)
    print(f"  -> {len(chunks)} chunks created.")

    print("\n[EXTRACT] LLM extracting entities and relationships... (GPT-4o)")
    print("  This may take 30-60 seconds...")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    llm_transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=["Rapper", "Producer", "Gang", "Person", "Event", "Location", "Label"],
        allowed_relationships=[
            "BEEF_WITH", "ATTACKED", "KILLED", "HIRED", "UNCLE_OF", 
            "MEMBER_OF", "SIGNED_TO", "LOCATED_IN", "ORDERED_HIT",
            "FRIEND_WITH", "CEO_OF", "SHOT", "SUSPECTED"
        ]
    )

    # 변환 실행
    graph_documents = llm_transformer.convert_to_graph_documents(chunks)
    
    total_nodes = sum(len(d.nodes) for d in graph_documents)
    total_rels = sum(len(d.relationships) for d in graph_documents)
    
    print(f"\n[RESULT] Extracted: {total_nodes} nodes, {total_rels} relationships")
    
    # 추출된 내용 미리보기
    if graph_documents:
        print("\n[PREVIEW] Sample nodes:")
        for node in graph_documents[0].nodes[:5]:
            print(f"  - ({node.type}: {node.id})")
        
        print("\n[PREVIEW] Sample relationships:")
        for rel in graph_documents[0].relationships[:5]:
            print(f"  - ({rel.source.id}) -[:{rel.type}]-> ({rel.target.id})")

    # DB 저장
    print("\n[SAVE] Saving to Neo4j...")
    graph.add_graph_documents(graph_documents)
    
    # 저장 후 통계
    print("\n[STATS] Database statistics:")
    node_stats = graph.query("""
        MATCH (n)
        RETURN labels(n)[0] as label, count(*) as count
        ORDER BY count DESC
    """)
    for record in node_stats:
        print(f"  - {record['label']}: {record['count']}")
    
    print("\n" + "=" * 60)
    print("[DONE] Graph built successfully!")
    print("Now run: streamlit run app.py")
    print("Ask about 'P. Diddy' or 'Keefe D'!")
    print("=" * 60)

if __name__ == "__main__":
    process_graph()
