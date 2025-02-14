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
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class S3service {

    private static final Logger log = LoggerFactory.getLogger(S3service.class);
    private final S3Presigner s3Presigner;
    private final S3Client s3Client;
    private final AwsConfig awsConfig;
    private final ExecutorService executorService = Executors.newFixedThreadPool(5); // 병렬 처리 스레드 풀
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
    public ResponseEntity<?> uploadToS3(String gameId, HttpServletRequest request) {

        // 1) Redis에서 gameId와 같은 Scene 다 가져오기
        List<SceneRedis> sceneRedisList = redisSceneRepository.findAllByGameId(gameId);
        // 예외처리
        if (sceneRedisList.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("해당 gameId에 대한 데이터가 없습니다.");
        }

        // 2) 병렬로 S3 업로드
        List<CompletableFuture<Void>> uploadFutures = sceneRedisList.stream()
                .map(scene -> CompletableFuture.runAsync(() -> uploadFileToS3(scene), executorService))
                .toList();


        // 3) 업로드 대기
        CompletableFuture.allOf(uploadFutures.toArray(new CompletableFuture[0])).join();

        return ApiResponseUtil.success(null, "저장 완료", HttpStatus.CREATED, request.getRequestURI());

    }
    // S3 업로드 메서드 (바이너리 데이터를 바로 업로드)
    private void uploadFileToS3(SceneRedis scene) {
        String objectKey = scene.getGameId() + "/" + scene.getSceneOrder() + ".png";

        // S3 업로드 객체
        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(awsConfig.getBucketName())
                .key(objectKey)
                .build();

        // S3에 파일 업로드 (바이너리 데이터를 직접 업로드)
        s3Client.putObject(putObjectRequest, RequestBody.fromBytes(scene.getImage()));
    }

    ///////////////////////
    // #3.  파일 다운로드   //
    //////////////////////
    public ResponseEntity<?> downloadFromS3(String objectKey, HttpServletRequest request) {
        try {

            log.info(awsConfig.getBucketName());
            log.info(awsConfig.getRegion());
            log.info(awsConfig.getAccessKey());
            log.info(awsConfig.getSecretKey());
            log.info(objectKey);
            log.info("내 로그 여기있어 요!!!!");
            // S3 업로드 객체 생성
            GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                    .bucket(awsConfig.getBucketName())
                    .key(objectKey)
                    .build();

            byte[] fileBytes = s3Client.getObject(getObjectRequest).readAllBytes();



            return ResponseEntity.ok()
                    .header("Content-Disposition", "attachment; filename=\"" + objectKey + "\"")
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

}


