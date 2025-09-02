# Long Ago Infrastructure

## 🏗️ 프로덕션 서버 설정 백업

이 디렉토리는 EC2 프로덕션 서버의 인프라 설정 파일들을 백업하고 관리합니다.

## 📁 디렉토리 구조

```
infra/
├── docker-compose.prod.yml  # 프로덕션용 Docker Compose 설정
├── nginx/
│   └── default.conf         # Nginx 웹서버 설정
├── turnserver.conf          # WebRTC TURN 서버 설정
├── init_db.sql             # 데이터베이스 초기화 스크립트
├── backup-scripts/
│   ├── sync-from-server.sh  # EC2에서 설정 다운로드
│   └── deploy-to-server.sh  # 설정을 EC2로 업로드
└── README.md               # 이 파일
```

## 🔧 사용 방법

### 서버에서 설정 파일 백업하기:
```bash
cd infra/backup-scripts
chmod +x sync-from-server.sh
./sync-from-server.sh
```

### 로컬 설정을 서버로 배포하기:
```bash
cd infra/backup-scripts  
chmod +x deploy-to-server.sh
./deploy-to-server.sh
```

## 🚀 새 서버 배포 절차

1. **EC2 인스턴스 생성**
2. **Docker 설치**
3. **설정 파일 업로드**:
   ```bash
   ./deploy-to-server.sh
   ```
4. **환경변수 설정** (GitHub Actions 또는 수동)
5. **서비스 시작**:
   ```bash
   ssh -i "./long-ago-main-key.pem" ubuntu@16.176.206.134
   docker-compose up -d
   ```

## 📋 주요 서비스

### Web Server (Nginx)
- 포트: 80, 443
- SSL/TLS 인증서 관리
- 정적 파일 서빙
- 리버스 프록시

### Application Server (Spring Boot)
- 포트: 8080  
- API 서버
- 데이터베이스 연결

### AI Service (Python)
- 포트: 8190
- 이미지 생성 서비스
- OpenAI + Gemini API 통합

### Cache Server (Redis)
- 포트: 6379
- 세션 관리
- 캐시 저장소

### TURN Server (Coturn)
- 포트: 3478, 5349
- WebRTC P2P 연결 지원

## 🛡️ 보안 고려사항

- `.env` 파일은 절대 Git에 커밋하지 마세요
- SSL 인증서는 별도로 백업하세요
- API 키는 GitHub Secrets에서 관리하세요

## 🔄 업데이트 주기

정기적으로 서버 설정을 백업하세요:
- 설정 변경 후 즉시
- 주요 배포 전후
- 월 1회 정기 백업

## 📞 문제 해결

### 연결 문제:
- SSH 키 경로 확인: `./long-ago-main-key.pem`
- 서버 IP 확인: `16.176.206.134`
- 보안 그룹 설정 확인

### 서비스 재시작:
```bash
ssh -i "./long-ago-main-key.pem" ubuntu@16.176.206.134
docker-compose logs -f  # 로그 확인
docker-compose restart  # 재시작
```