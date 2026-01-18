# 🕵️‍♂️ Hip-Hop Noir: Data Detective

90년대 미국 힙합 씬(East vs West)의 인물, 갱단, 사건 관계도를 구축하고, 자연어 질문을 받아 그래프를 탐색하여 범인이나 배후를 동기와 관계 기반으로 추론하는 프로파일링 시스템입니다.

## 📋 프로젝트 개요

### 목표
- **Core:** 90년대 힙합 씬의 인물, 갱단, 사건 관계도 구축
- **Feature:** 자연어 질문을 받아 그래프를 탐색하고, 명시되지 않은 범인이나 배후를 추론

### 기술 스택
- **Database:** Neo4j AuraDB (그래프 데이터베이스)
- **Backend:** Python 3.10+
- **Orchestration:** LangChain (LLM과 Graph DB 연결)
- **LLM:** OpenAI GPT-4o
- **UI (Optional):** Streamlit (웹 인터페이스)

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 필수 라이브러리 설치
pip install -r requirements.txt
```

### 2. Neo4j 데이터베이스 준비

#### 옵션 A: Neo4j AuraDB (클라우드, 무료)
1. [Neo4j Console](https://console.neo4j.io/) 접속
2. `New Instance` → `Free` 선택
3. 생성된 DB의 **Connect URL**, **Username**, **Password** 복사

#### 옵션 B: Neo4j Desktop (로컬)
1. [Neo4j Desktop](https://neo4j.com/download/) 다운로드 및 설치
2. 새 프로젝트 생성 및 DB 실행
3. 기본 연결: `bolt://localhost:7687`, 사용자: `neo4j`

### 3. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하세요:

```env
# OpenAI API Key
OPENAI_API_KEY=sk-proj-...

# Neo4j Connection (AuraDB)
NEO4J_URI=neo4j+s://your-db-id.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-db-password

# 또는 로컬 Neo4j Desktop 사용 시
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USERNAME=neo4j
# NEO4J_PASSWORD=your-local-password
```

### 4. 데이터베이스 초기화

```bash
python seed.py
```

이 스크립트는 다음을 수행합니다:
- 기존 데이터 삭제
- 인물, 갱단, 레이블, 사건 노드 생성
- 관계(Beef, Affiliation, Contract 등) 생성
- 데이터베이스 통계 출력

### 5. 실행

#### 터미널 인터페이스
```bash
python app.py
```

#### Streamlit 웹 인터페이스
```bash
streamlit run app_streamlit.py
```

## 📊 데이터 모델

### Nodes (노드 타입)
- `Rapper` - 래퍼 (Tupac, Biggie 등)
- `Producer` - 제작자/경영자 (Suge Knight, P. Diddy)
- `Gang` - 갱단 (Bloods, Crips)
- `Label` - 레이블 (Death Row, Bad Boy)
- `Event` - 사건 (총격, 살해)
- `Person` - 일반 인물 (용의자 등)

### Relationships (관계 타입)
- `[:BEEF_WITH {reason, year}]` - 적대 관계
- `[:AFFILIATED_WITH]` - 갱단/세력 연루
- `[:SIGNED_TO]` - 계약 관계
- `[:ATTACKED {method, date}]` - 공격/폭행
- `[:SUSPECTED_OF_KILLING]` - 살해 용의 (추론 핵심)
- `[:PRESENT_AT]` - 현장 부재중명 (추론용)
- `[:MOTIVE {reason, strength}]` - 살해 동기 (추론용)

## 🔍 사용 예시

### 레벨 1: 단순 검색
```
Q: 투팍과 사이가 안 좋았던 사람은 누구야?
```

### 레벨 2: 관계 탐색
```
Q: Death Row Records와 대립했던 갱단은 어디야?
```

### 레벨 3: 추론 (핵심 기능)
```
Q: 투팍을 쏜 범인이 데이터에 명시돼 있어? 없다면, 폭행 사건과 갱단 관계를 근거로 가장 유력한 용의자를 추론해줘.
Q: 투팍 사망 당일 MGM Grand에서 무슨 일이 있었어?
Q: 갱단 간 전쟁과 투팍 사건의 연관성은?
```

## 📁 프로젝트 구조

```
hiphop_noir/
├── .env                    # 환경 변수 (직접 생성 필요)
├── .env.example           # 환경 변수 템플릿
├── requirements.txt       # Python 패키지 의존성
├── seed.py               # 데이터베이스 초기화 스크립트
├── detective.py          # 추론 엔진 (LangChain Agent)
├── app.py                # 터미널 인터페이스
├── app_streamlit.py      # Streamlit 웹 인터페이스
└── README.md            # 프로젝트 문서
```

## 🛠️ 개발 및 커스터마이징

### 데이터 추가
`seed.py`의 Cypher 쿼리를 수정하여 더 많은 인물, 사건, 관계를 추가할 수 있습니다.

### 추론 로직 수정
`detective.py`의 `detective_template` 프롬프트를 수정하여 추론 방식을 조정할 수 있습니다.

### 시각화 추가
Neo4j Browser (`http://localhost:7474`) 또는 pyvis, networkx 등을 사용하여 그래프 시각화를 추가할 수 있습니다.

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일을 `.gitignore`에 추가하여 Git에 커밋하지 마세요.
2. **데이터 정확성**: 이 프로젝트는 교육/데모 목적입니다. 실제 범죄 사건 데이터와 다를 수 있습니다.
3. **Neo4j AuraDB**: 무료 티어는 인스턴스가 자동으로 중지될 수 있습니다. 사용 전에 활성화되어 있는지 확인하세요.

## 🔧 문제 해결

### Neo4j 연결 오류
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` 확인
- Neo4j 서버가 실행 중인지 확인
- 방화벽 설정 확인 (특히 클라우드 DB의 경우)

### OpenAI API 오류
- `OPENAI_API_KEY` 확인
- API 키의 사용 한도 확인
- 인터넷 연결 확인

### LangChain 버전 호환성
최신 LangChain 버전에 따라 API가 변경될 수 있습니다. 오류 발생 시 `detective.py`의 체인 생성 부분을 확인하세요.

## 📚 참고 자료

- [Neo4j Documentation](https://neo4j.com/docs/)
- [LangChain Documentation](https://python.langchain.com/)
- [Cypher Query Language](https://neo4j.com/developer/cypher/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📝 라이선스

이 프로젝트는 교육/데모 목적으로 만들어졌습니다.

## 🤝 기여

버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!

---

**🕵️‍♂️ Happy Detective Work!**
