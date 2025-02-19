package com.example.b101.service;

import com.example.b101.cache.SceneRedis;
import com.example.b101.common.ApiResponseUtil;
import com.example.b101.config.AwsConfig;
import com.example.b101.repository.RedisSceneRepository;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.core.exception.SdkClientException;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.S3Exception;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;
import software.amazon.awssdk.services.s3.presigner.model.PresignedGetObjectRequest;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class S3service {

    private static final Logger log = LoggerFactory.getLogger(S3service.class);
    private final S3Presigner s3Presigner;
    private final S3Client s3Client;
    private final AwsConfig awsConfig;
    private final ExecutorService executorService = Executors.newFixedThreadPool(2); // 병렬 처리 스레드 풀
    private final RedisSceneRepository redisSceneRepository;

    ////////////////////////////////////
    // #1. presignedURL 생성 + 예외 처리 //
    ///////////////////////////////////
    public ResponseEntity<?> generatePresignedUrl(String bookNum, String fileName, HttpServletRequest request) {
        try {
            if (bookNum == null || fileName == null) {
                return ApiResponseUtil.failure("bookNum 또는 fileName이 비어 있습니다.", HttpStatus.BAD_REQUEST, request.getRequestURI());
            }

            // 해당 키 값으로 특정 S3파일에 접근
            String objectKey = bookNum + "/" + fileName;

            // 1) objectRequest 객체 생성 (버킷 이름과 키 설정)
            GetObjectRequest getObjectRequest =
                    GetObjectRequest.builder()
                            .bucket(awsConfig.getBucketName())
                            .key(objectKey)
                            .build();

            // 2) presignRequest 객체 생성 (1분 시간 설정)
            GetObjectPresignRequest getObjectPresignRequest =
                    GetObjectPresignRequest.builder()
                            .signatureDuration(Duration.ofMinutes(1))
                            .getObjectRequest(getObjectRequest)
                            .build();

            // 3) presigned request 보내기
            PresignedGetObjectRequest presignedGetObjectRequest =
                    s3Presigner.presignGetObject(getObjectPresignRequest);

            // 로그
            System.out.println("Presigned URL: " + presignedGetObjectRequest.url());

            return ApiResponseUtil.success(presignedGetObjectRequest.url().toString(),
                    "URL 생성", HttpStatus.CREATED, request.getRequestURI());

        } catch (NoSuchKeyException e) {
            return ApiResponseUtil.failure("파일을 찾을 수 없습니다: " + fileName, HttpStatus.NOT_FOUND, request.getRequestURI());
        } catch (S3Exception e) {
            return ApiResponseUtil.failure("S3 접근 중 오류 발생: " + e.awsErrorDetails().errorMessage(), HttpStatus.FORBIDDEN, request.getRequestURI());
        } catch (SdkClientException e) {
            return ApiResponseUtil.failure("AWS 네트워크 오류 발생", HttpStatus.SERVICE_UNAVAILABLE, request.getRequestURI());
        }
    }

    ////////////////////////////
    // #2. 파일 업로드 + 예외 처리 //
    ////////////////////////////
    public boolean uploadToS3(String gameId,String bookId) {

        log.info("s3에 이미지 저장 로직 실행");
        // 1) Redis에서 gameId와 같은 Scene 다 가져오기
        List<SceneRedis> sceneRedisList = redisSceneRepository.findAllByGameId(gameId);

        log.info("Redis에 저장된 scene 데이터들 : {}", sceneRedisList.size());

        for (int i = 0; i < sceneRedisList.size(); i++) {
            SceneRedis scene = sceneRedisList.get(i);
            byte[] image = scene.getImage();  // 이미지 데이터
            int imageSize = image != null ? image.length : 0;  // 이미지 크기 계산 (이미지가 null일 경우 0으로 설정)

            // 로그 출력
            log.info("Index: {}, SceneOrder: {}, Image Size: {} bytes", i, scene.getSceneOrder(), imageSize);
        }

        // 책이 비어 있으면 예외처리 (사용자들이 게임을 안 했을 때)
        if (sceneRedisList.isEmpty()) {
            log.info("해당 gameId에 대한 데이터가 레디스에 없음.");
            return false;
        }
        // 업로드 성공 여부 플래그 ( 동시성 문제로 사용)
        AtomicBoolean isUploaded = new AtomicBoolean(false);

        // 2) 병렬로 S3 업로드
        List<CompletableFuture<Void>> uploadFutures = sceneRedisList.stream()
                .map(scene -> CompletableFuture.runAsync(() -> {
                    try {
                        uploadFileToS3(scene,bookId);
                        log.info( "파일 업로드 성공 - SceneOrder: {}, Image Size: {} bytes", scene.getSceneOrder(), scene.getImage().length);
                        isUploaded.set(true);
                    } catch (Exception e) {
                        log.error( "파일 업로드 실패 - SceneOrder: {} 에러: {}", scene.getSceneOrder(), e.getMessage());
                    }
                }, executorService))
                .toList();

        // 3) 모든 업로드 끝날 까지 대기 (각각의 병렬 처리 예외 처리)
        CompletableFuture.allOf(uploadFutures.toArray(new CompletableFuture[0])).join();

        if (!isUploaded.get()) {
            log.info("사진 하나도 저장 안 됨");
            return false;
        }
        log.info("아무튼 업로드 됨");
        return true;
    }

    // S3 업로드 메서드 (바이너리 데이터를 바로 업로드)
    private void uploadFileToS3(SceneRedis scene,String bookId) {
        log.info("image 데이터가 있나요? : {} bytes", scene.getImage() != null ? scene.getImage().length : 0);

        // 해당 이름의 객체로 S3에 저장
        String objectKey = bookId + "/" + scene.getSceneOrder() + ".png";

        // S3 업로드 객체 빌드
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(awsConfig.getBucketName())
                .key(objectKey)
                .build();

        // S3에 파일 업로드 (바이너리 데이터(scene.getImage()를 업로드)
        s3Client.putObject(putObjectRequest, RequestBody.fromBytes(scene.getImage()));
    }

    ///////////////////////////////////////
    // #3.  파일 다운로드 + 예외 처리(정상 작동)  //
    ///////////////////////////////////////
    public ResponseEntity<?> downloadFromS3(String objectKey, HttpServletRequest request) {
        try {

            log.info("현재 위치 S3service.downloadFromS3");

            // S3 업로드 객체 생성
            GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                    .bucket(awsConfig.getBucketName())
                    .key(objectKey)
                    .build();

            byte[] fileBytes = s3Client.getObject(getObjectRequest).readAllBytes();

            // 파일 확장자에 따라 Content-Type 자동 설정
            MediaType contentType = getContentType(objectKey);

            return ResponseEntity.ok()
                    .contentType(contentType)
                    .body(fileBytes);

        } catch (NoSuchKeyException e) {
            return ApiResponseUtil.failure("파일을 찾을 수 없습니다: " + objectKey, HttpStatus.NOT_FOUND, request.getRequestURI());
        } catch (S3Exception e) {
            return ApiResponseUtil.failure("S3 접근 중 오류 발생: " + e.awsErrorDetails().errorMessage(), HttpStatus.FORBIDDEN, request.getRequestURI());
        } catch (SdkClientException e) {
            return ApiResponseUtil.failure("AWS 네트워크 오류 발생", HttpStatus.SERVICE_UNAVAILABLE, request.getRequestURI());
        } catch (Exception e) {
            return ApiResponseUtil.failure("파일 다운로드 중 오류 발생", HttpStatus.INTERNAL_SERVER_ERROR, request.getRequestURI());
        }
    }

    // 파일 확장자에 따른 Content-Type 반환 ( 다운로드에서 사용 )
    private MediaType getContentType(String objectKey) {
        if (objectKey.endsWith(".png")) {
            return MediaType.IMAGE_PNG;
        } else if (objectKey.endsWith(".jpg") || objectKey.endsWith(".jpeg")) {
            return MediaType.IMAGE_JPEG;
        } else if (objectKey.endsWith(".gif")) {
            return MediaType.IMAGE_GIF;
        }
        return MediaType.APPLICATION_OCTET_STREAM; // 기본값 (이미지 아닌 경우)
    }
}


