#############
# 1.  빌드   #
#############

FROM node:18-alpine AS build

# 컨테이너 안 경로 설정
WORKDIR /app

# 복사 및 종속성 설치
COPY package.json package-lock.json ./
RUN npm install

# 소스 코드 복사 및 빌드
COPY . .
RUN npm run build

################
# 2. 이미지 생성  #
################

FROM nginx:alpine

# 빌드된 파일을 Nginx의 기본 경로로 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 포트 작성
EXPOSE 80

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]

