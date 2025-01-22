# 1. 빌드
FROM gradle:8.12.0-jdk17-alpine AS build

# 컨테이너 안 경로 설정
WORKDIR /home/gradle/project

# 종속성 관련 파일만 먼저 복사
COPY build.gradle settings.gradle ./


# Gradle 캐시를 활용하여 종속성 다운로드 및 빌드
RUN gradle build -x test --no-daemon

# 소스 코드 복사
COPY ./src ./src/

# 2. 실행 가능한 JAR 파일을 포함한 이미지 생성
FROM openjdk:17-jdk-alpine

WORKDIR /app

# 빌드된 JAR 파일 복사
COPY --from=build /home/gradle/project/src/build/libs/*.jar app.jar

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]

# 포트 노출 (Spring Boot 기본 포트)
EXPOSE 8080

