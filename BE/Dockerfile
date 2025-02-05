#############
# 1.  빌드   #
#############

# 베이스 이미지 설정
FROM gradle:8.12.0-jdk17-alpine AS build

# 컨테이너 안 경로 설정
WORKDIR /home/gradle/BE

# 종속성 관련 파일만 먼저 복사
COPY build.gradle settings.gradle ./

#  소스 코드 복사
COPY src ./src/


# Gradle 캐시를 활용하여 종속성 다운로드 및 빌드
RUN gradle build -x test


################
# 2. 이미지 생성  #
################

FROM openjdk:17-jdk-alpine

WORKDIR /BE

# 빌드된 JAR 파일 복사
COPY --from=build /home/gradle/BE/build/libs/*.jar app.jar

# 애플리케이션 실행
ENTRYPOINT ["java", "-jar", "app.jar"]

# 포트 노출 (Spring Boot 기본 포트)
EXPOSE 8080

#