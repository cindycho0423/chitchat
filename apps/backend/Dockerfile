FROM python:3.11-slim

WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# 포트 오픈
EXPOSE 8000

# 실행 명령 (docker-compose.yml의 command와 일치시키기)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]