#!/bin/bash
# 로컬의 설정 파일들을 EC2 서버로 업로드하는 스크립트

SERVER_IP="16.176.206.134"
KEY_PATH="./long-ago-main-key.pem"

echo "🚀 EC2 서버로 설정 파일 배포 중..."

# EC2 연결 테스트
if ! ssh -i "$KEY_PATH" -o ConnectTimeout=10 ubuntu@$SERVER_IP "echo 'Connection test successful'" > /dev/null 2>&1; then
    echo "❌ EC2 서버 연결 실패! 키 경로와 서버 IP를 확인하세요."
    exit 1
fi

# 백업 디렉토리로 이동
cd "$(dirname "$0")/.." || exit 1

# docker-compose.yml 업로드
if [ -f "./docker-compose.prod.yml" ]; then
    echo "📄 docker-compose.yml 업로드 중..."
    scp -i "$KEY_PATH" ./docker-compose.prod.yml ubuntu@$SERVER_IP:~/docker-compose.yml
fi

# nginx 설정 업로드
if [ -f "./nginx/default.conf" ]; then
    echo "🌐 nginx 설정 업로드 중..."
    ssh -i "$KEY_PATH" ubuntu@$SERVER_IP "mkdir -p ~/nginx"
    scp -i "$KEY_PATH" ./nginx/default.conf ubuntu@$SERVER_IP:~/nginx/default.conf
fi

# turnserver 설정 업로드
if [ -f "./turnserver.conf" ]; then
    echo "🔄 turnserver 설정 업로드 중..."
    scp -i "$KEY_PATH" ./turnserver.conf ubuntu@$SERVER_IP:~/turnserver.conf
fi

# init_db.sql 업로드 (있는 경우)
if [ -f "./init_db.sql" ]; then
    echo "🗄️ 데이터베이스 초기화 스크립트 업로드 중..."
    scp -i "$KEY_PATH" ./init_db.sql ubuntu@$SERVER_IP:~/init_db.sql
fi

echo ""
echo "✅ 업로드 완료!"
echo ""
echo "🔧 서버에서 다음 명령어로 서비스를 재시작하세요:"
echo "   ssh -i \"$KEY_PATH\" ubuntu@$SERVER_IP"
echo "   docker-compose down"
echo "   docker-compose up -d"