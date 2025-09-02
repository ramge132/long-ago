#!/bin/bash
# EC2에서 설정 파일들을 자동으로 동기화하는 스크립트

SERVER_IP="16.176.206.134"
KEY_PATH="./long-ago-main-key.pem"

echo "🔄 EC2 설정 파일 동기화 중..."

# EC2 연결 테스트
if ! ssh -i "$KEY_PATH" -o ConnectTimeout=10 ubuntu@$SERVER_IP "echo 'Connection test successful'" > /dev/null 2>&1; then
    echo "❌ EC2 서버 연결 실패! 키 경로와 서버 IP를 확인하세요."
    exit 1
fi

# 백업 디렉토리로 이동
cd "$(dirname "$0")/.." || exit 1

# docker-compose.yml 동기화
echo "📄 docker-compose.yml 동기화 중..."
scp -i "$KEY_PATH" ubuntu@$SERVER_IP:~/docker-compose.yml ./docker-compose.prod.yml

# nginx 설정 동기화
echo "🌐 nginx 설정 동기화 중..."
scp -i "$KEY_PATH" ubuntu@$SERVER_IP:~/nginx/default.conf ./nginx/default.conf

# turnserver 설정 동기화
echo "🔄 turnserver 설정 동기화 중..."
scp -i "$KEY_PATH" ubuntu@$SERVER_IP:~/turnserver.conf ./turnserver.conf

# init_db.sql 동기화 (있는 경우)
echo "🗄️ 데이터베이스 초기화 스크립트 동기화 중..."
if ssh -i "$KEY_PATH" ubuntu@$SERVER_IP "test -f ~/init_db.sql"; then
    scp -i "$KEY_PATH" ubuntu@$SERVER_IP:~/init_db.sql ./init_db.sql
    echo "✅ init_db.sql 동기화 완료"
else
    echo "ℹ️ init_db.sql 파일이 서버에 없습니다."
fi

echo ""
echo "✅ 동기화 완료!"
echo ""
echo "📝 다음 명령어로 변경사항을 확인하고 커밋하세요:"
echo "   git diff"
echo "   git add infra/"
echo "   git commit -m 'update: Sync infrastructure config from server'"
echo "   git push origin main"