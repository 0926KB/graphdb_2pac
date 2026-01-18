"""
Hip-Hop Noir: Graph ETL Pipeline Visualizer
문서가 지식 그래프로 변환되는 전 과정을 실시간으로 추적하는 대시보드
"""
import streamlit as st
import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from streamlit_agraph import agraph, Node, Edge, Config

# 1. 설정 및 연결
load_dotenv()
st.set_page_config(layout="wide", page_title="Graph ETL Visualizer", page_icon="⚙️")

# 커스텀 CSS
st.markdown("""
<style>
    .stTextArea textarea {
        font-family: 'Consolas', monospace;
        font-size: 14px;
    }
    .step-header {
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .node-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ 힙합 느와르: 그래프 구축 파이프라인 (ETL)")
st.caption("Raw Text가 지식 그래프(Knowledge Graph)로 변환되는 전 과정을 추적합니다.")

# 사이드바: DB 연결 상태 및 설정
with st.sidebar:
    st.header("🔌 System Status")
    
    neo4j_uri = os.getenv("NEO4J_URI")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if neo4j_uri:
        st.success("✅ Neo4j Connected")
        st.caption(f"URI: {neo4j_uri[:30]}...")
    else:
        st.error("❌ Missing NEO4J_URI in .env")
    
    if openai_key:
        st.success("✅ OpenAI API Ready")
    else:
        st.error("❌ Missing OPENAI_API_KEY in .env")
    
    if not neo4j_uri or not openai_key:
        st.warning("⚠️ .env 파일을 확인하세요")
        st.stop()
    
    st.divider()
    
    # 모델 및 청킹 설정
    st.header("⚙️ Pipeline Settings")
    chunk_size = st.slider("Chunk Size (문자)", 100, 2000, 500, step=50)
    chunk_overlap = st.slider("Overlap (중복)", 0, 500, 50, step=10)
    
    st.divider()
    
    # 스키마 설정
    st.header("📐 Schema Definition")
    allowed_nodes = st.multiselect(
        "허용 노드 타입",
        ["Rapper", "Producer", "Gang", "Event", "Location", "Person", "Label"],
        default=["Rapper", "Gang", "Event", "Location", "Person"]
    )
    
    allowed_rels = st.multiselect(
        "허용 관계 타입",
        ["BEEF_WITH", "ATTACKED", "KILLED", "MEMBER_OF", "LOCATED_IN", "SIGNED_TO", "FOUNDED", "AFFILIATED_WITH", "FRIEND_WITH"],
        default=["BEEF_WITH", "ATTACKED", "KILLED", "MEMBER_OF", "LOCATED_IN"]
    )
    
    st.divider()
    
    # DB 관리
    st.header("🗄️ Database Management")
    if st.button("🗑️ 기존 데이터 삭제", type="secondary", use_container_width=True):
        try:
            graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI"),
                username=os.getenv("NEO4J_USERNAME"),
                password=os.getenv("NEO4J_PASSWORD")
            )
            graph.query("MATCH (n) DETACH DELETE n")
            st.success("✅ 데이터 삭제 완료!")
        except Exception as e:
            st.error(f"오류: {e}")

# ==========================================
# Step 1: 문서 입력 (Raw Data)
# ==========================================
st.header("📥 Step 1: Raw Document Input")
st.caption("분석할 원본 텍스트를 입력하세요. LLM이 이 텍스트에서 엔티티와 관계를 추출합니다.")

default_text = """1996년 9월 7일, 래퍼 투팍(Tupac Shakur)은 라스베가스에서 마이크 타이슨의 경기를 관람했다.
경기 직후, 투팍은 로비에서 올랜도 앤더슨(Orlando Anderson)이라는 'Southside Crips' 갱단원과 싸움을 벌였다.
몇 시간 뒤, 투팍은 슈그 나이트(Suge Knight)가 운전하는 차를 타고 가던 중 총격을 당해 사망했다.
많은 사람들은 이 사건이 동부의 비기(Notorious B.I.G.)와 연관되어 있다고 의심했다."""

input_text = st.text_area(
    "분석할 텍스트를 입력하세요:",
    value=default_text,
    height=180,
    key="input_text"
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    run_button = st.button("🚀 파이프라인 실행", type="primary", use_container_width=True)
with col2:
    st.metric("입력 문자 수", f"{len(input_text):,}")

if run_button:
    if not input_text.strip():
        st.error("텍스트를 입력해주세요!")
        st.stop()
    
    # Neo4j 및 LLM 연결
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )

    # ==========================================
    # Step 2: 청킹 (Chunking)
    # ==========================================
    st.divider()
    st.header("✂️ Step 2: Text Chunking")
    st.caption(f"긴 문서를 LLM이 처리하기 좋은 크기({chunk_size}자)로 분할합니다.")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    docs = [Document(page_content=input_text)]
    chunks = text_splitter.split_documents(docs)
    
    st.success(f"✅ 총 **{len(chunks)}개**의 청크로 분할되었습니다.")
    
    # 청크 시각화
    num_cols = min(len(chunks), 4)
    if num_cols > 0:
        cols = st.columns(num_cols)
        for i, chunk in enumerate(chunks):
            with cols[i % num_cols]:
                with st.container():
                    st.markdown(f"**🧩 Chunk #{i+1}**")
                    st.caption(f"({len(chunk.page_content)} chars)")
                    preview = chunk.page_content[:150] + "..." if len(chunk.page_content) > 150 else chunk.page_content
                    st.info(f'"{preview}"')

    # ==========================================
    # Step 3: LLM 파싱 & 추출 (Parsing)
    # ==========================================
    st.divider()
    st.header("🧠 Step 3: LLM Entity & Relation Extraction")
    st.caption("GPT-4o가 텍스트를 분석하여 엔티티(노드)와 관계(엣지)를 추출합니다.")
    
    with st.spinner("🤖 LLM이 텍스트를 이해하고 관계를 추출 중입니다... (약 10-30초 소요)"):
        try:
            llm_transformer = LLMGraphTransformer(
                llm=llm,
                allowed_nodes=allowed_nodes,
                allowed_relationships=allowed_rels
            )
            graph_documents = llm_transformer.convert_to_graph_documents(chunks)
            
            # 전체 통계
            total_nodes = sum(len(doc.nodes) for doc in graph_documents)
            total_rels = sum(len(doc.relationships) for doc in graph_documents)
            
            st.success(f"✅ 추출 완료! 노드: **{total_nodes}개**, 관계: **{total_rels}개**")
            
        except Exception as e:
            st.error(f"❌ LLM 추출 오류: {e}")
            st.stop()
    
    # 파싱 결과 시각화
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔵 Extracted Nodes")
        all_nodes = []
        for doc in graph_documents:
            all_nodes.extend(doc.nodes)
        
        if all_nodes:
            for node in all_nodes:
                st.code(f"(:{node.type} {{id: '{node.id}'}})", language="cypher")
        else:
            st.warning("추출된 노드가 없습니다.")
    
    with col2:
        st.subheader("🔗 Extracted Relationships")
        all_rels = []
        for doc in graph_documents:
            all_rels.extend(doc.relationships)
        
        if all_rels:
            for rel in all_rels:
                st.code(f"({rel.source.id}) -[:{rel.type}]-> ({rel.target.id})", language="cypher")
        else:
            st.warning("추출된 관계가 없습니다.")

    # ==========================================
    # Step 4: Cypher 코드 변환
    # ==========================================
    st.divider()
    st.header("📝 Step 4: Generated Cypher Query")
    st.caption("LLM이 추출한 데이터를 바탕으로 실행될 DB 쿼리입니다.")
    
    cypher_preview = "// 노드 생성 쿼리\n"
    for node in all_nodes:
        props = ", ".join([f"{k}: '{v}'" for k, v in node.properties.items()]) if node.properties else ""
        if props:
            cypher_preview += f"MERGE (n:{node.type} {{id: '{node.id}', {props}}})\n"
        else:
            cypher_preview += f"MERGE (n:{node.type} {{id: '{node.id}'}})\n"
    
    cypher_preview += "\n// 관계 생성 쿼리\n"
    for rel in all_rels:
        cypher_preview += f"MATCH (a {{id: '{rel.source.id}'}}), (b {{id: '{rel.target.id}'}})\n"
        cypher_preview += f"MERGE (a)-[:{rel.type}]->(b)\n\n"
    
    st.code(cypher_preview, language="cypher")
    
    # 복사 버튼
    st.download_button(
        label="📋 Cypher 쿼리 다운로드",
        data=cypher_preview,
        file_name="generated_cypher.cql",
        mime="text/plain"
    )

    # ==========================================
    # Step 5: DB 저장 및 시각화 (Final Output)
    # ==========================================
    st.divider()
    st.header("🎨 Step 5: Final Graph Visualization")
    st.caption("Neo4j에 저장된 그래프를 시각화합니다.")
    
    # DB 저장
    with st.spinner("💾 Neo4j 데이터베이스에 저장 중..."):
        try:
            graph.add_graph_documents(graph_documents)
            st.toast("✅ 데이터베이스 저장 완료!", icon="💾")
        except Exception as e:
            st.error(f"❌ DB 저장 오류: {e}")
            st.stop()

    # 시각화를 위해 DB에서 데이터 가져오기
    with st.spinner("🎨 그래프 렌더링 중..."):
        try:
            visual_query = """
            MATCH (n)-[r]->(m)
            RETURN n, r, m
            LIMIT 100
            """
            results = graph.query(visual_query)
            
            nodes = []
            edges = []
            node_ids = set()
            
            # 노드 타입별 색상 정의
            color_map = {
                "Rapper": "#FF6B6B",      # 빨간색
                "Producer": "#4ECDC4",    # 청록색
                "Gang": "#45B7D1",         # 파란색
                "Event": "#96CEB4",        # 연두색
                "Location": "#FFEAA7",     # 노란색
                "Person": "#DDA0DD",       # 보라색
                "Label": "#F39C12"         # 주황색
            }

            for record in results:
                source = record['n']
                target = record['m']
                rel = record['r']
                
                # 소스 노드
                src_id = source.get('id', source.get('name', str(id(source))))
                src_labels = list(source.labels) if hasattr(source, 'labels') else []
                src_label = src_labels[0] if src_labels else "Node"
                src_color = color_map.get(src_label, "#999999")
                
                if src_id not in node_ids:
                    nodes.append(Node(
                        id=src_id,
                        label=src_id,
                        size=25,
                        color=src_color,
                        title=f"{src_label}: {src_id}"
                    ))
                    node_ids.add(src_id)
                
                # 타겟 노드
                tgt_id = target.get('id', target.get('name', str(id(target))))
                tgt_labels = list(target.labels) if hasattr(target, 'labels') else []
                tgt_label = tgt_labels[0] if tgt_labels else "Node"
                tgt_color = color_map.get(tgt_label, "#999999")

                if tgt_id not in node_ids:
                    nodes.append(Node(
                        id=tgt_id,
                        label=tgt_id,
                        size=25,
                        color=tgt_color,
                        title=f"{tgt_label}: {tgt_id}"
                    ))
                    node_ids.add(tgt_id)
                
                # 엣지 (관계)
                rel_type = rel[1] if isinstance(rel, tuple) else type(rel).__name__
                edges.append(Edge(
                    source=src_id,
                    target=tgt_id,
                    label=rel_type,
                    color="#888888"
                ))

            if nodes:
                st.success(f"✅ 그래프 로드 완료! 노드: {len(nodes)}개, 엣지: {len(edges)}개")
                
                # 범례 표시
                st.markdown("**🎨 Color Legend:**")
                legend_cols = st.columns(len(color_map))
                for i, (node_type, color) in enumerate(color_map.items()):
                    with legend_cols[i]:
                        st.markdown(f'<span style="color:{color}">●</span> {node_type}', unsafe_allow_html=True)
                
                # 그래프 설정
                config = Config(
                    width=900,
                    height=600,
                    directed=True,
                    physics=True,
                    hierarchical=False,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6",
                    collapsible=False,
                )
                
                # 그래프 렌더링
                return_value = agraph(nodes=nodes, edges=edges, config=config)
                
            else:
                st.warning("⚠️ 시각화할 그래프 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"❌ 그래프 시각화 오류: {e}")
            st.info("Neo4j에 데이터는 저장되었습니다. Neo4j Browser에서 직접 확인해보세요.")

    # 최종 요약
    st.divider()
    st.header("📊 Pipeline Summary")
    
    summary_cols = st.columns(5)
    with summary_cols[0]:
        st.metric("📄 입력 문자", f"{len(input_text):,}")
    with summary_cols[1]:
        st.metric("✂️ 청크 수", len(chunks))
    with summary_cols[2]:
        st.metric("🔵 노드 수", total_nodes)
    with summary_cols[3]:
        st.metric("🔗 관계 수", total_rels)
    with summary_cols[4]:
        st.metric("✅ 상태", "완료")
    
    st.success("🎉 파이프라인 실행 완료! 이제 `app.py`를 실행하여 질문해보세요.")

