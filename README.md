# ChitChatChot

## 챗봇 애플리케이션

ChitChatChot은 사용자 친화적인 인터페이스를 통해 대화형 AI 챗봇과 상호작용할 수 있는 풀스택 웹 애플리케이션입니다. 백엔드는 Python FastAPI로 구축되었으며, 프론트엔드는 React(Remix 프레임워크 사용)로 개발되었습니다. Docker를 사용하여 쉽게 배포하고 실행할 수 있습니다.

## 주요 기능

- **대화형 챗봇:** AI 기반 챗봇과의 실시간 대화.
- **웹소켓 통신:** 백엔드와 프론트엔드 간의 효율적인 실시간 통신.
- **모듈화된 백엔드:** FastAPI를 사용한 깔끔하고 확장 가능한 API 구조.
- **현대적인 프론트엔드:** React 및 Remix를 활용한 반응형 사용자 인터페이스.
- **Docker 지원:** 컨테이너화를 통한 간편한 설정 및 배포.

## 기술 스택

### 백엔드
- **Python:** 핵심 로직 및 API 개발.
- **FastAPI:** 빠르고 효율적인 API 구축을 위한 웹 프레임워크.
- **SQLite:** 경량 데이터베이스 (개발용).
- **WebSockets:** 실시간 통신 구현.

### 프론트엔드
- **React:** 사용자 인터페이스 구축을 위한 JavaScript 라이브러리.
- **Remix:** React 기반의 풀스택 웹 ���레임워크.
- **TypeScript:** 타입 안정성을 위한 JavaScript 상위 집합.
- **Tailwind CSS:** 유틸리티 우선 CSS 프레임워크.
- **Vite:** 빠른 개발 서버 및 번들러.

### 배포
- **Docker:** 애플리케이션 컨테이너화.
- **Docker Compose:** 다중 컨테이너 Docker 애플리케이션 정의 및 실행.

## 설치 및 실행 방법

이 프로젝트는 Docker 및 Docker Compose를 사용하여 쉽게 설정하고 실행할 수 있습니다.

### 전제 조건
- Docker Desktop (Docker Engine 및 Docker Compose 포함)이 설치되어 있어야 합니다.

### 단계

1.  **리포지토리 클론:**
    ```bash
    git clone <your-repository-url>
    cd chitchatchot
    ```

2.  **환경 변수 설정:**
    `apps/backend/.env` 및 `apps/frontend/.env` 파일에 필요한 환경 변수를 설정합니다. 예시:
    
    **`apps/backend/.env`**
    ```
    DATABASE_URL=sqlite:///./chatbot.db
    ```

    **`apps/frontend/.env`**
    ```
    VITE_API_BASE_URL=http://localhost:8000
    VITE_WS_BASE_URL=ws://localhost:8000
    ```

3.  **Docker Compose로 빌드 및 실행:**
    프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다.
    ```bash
    docker-compose up --build
    ```
    이 명령어는 백엔드 및 프론트엔드 서비스를 빌드하고 ���작합니다.

4.  **애플리케이션 접근:**
    - **프론트엔드:** `http://localhost:3000` (또는 `docker-compose.yml`에 설정된 포트)
    - **백엔드 API 문서 (Swagger UI):** `http://localhost:8000/docs` (또는 `docker-compose.yml`에 설정된 포트)

## 프로젝트 구조

```
chitchatchot/
├── docker-compose.yml
├── apps/
│   ├── backend/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── ai/             # AI 모델 및 로직
│   │   ├── config/         # 설정 파일
│   │   ├── db/             # 데이터베이스 관련 파일
│   │   ├── manager/        # 웹소켓 연결 관리
│   │   ├── routers/        # FastAPI 라우터 정의
│   │   └── schema/         # Pydantic 모델 정의
│   └── frontend/
│       ├── package.json
│       ├── app/            # Remix 애플리케이션 소스 코드
│       ├── public/         # 정적 파일
│       └── ...
└── ...
```
