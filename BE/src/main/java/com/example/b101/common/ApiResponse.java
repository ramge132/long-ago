package com.example.b101.common;

import lombok.Builder;
import lombok.Data;

/**
 * API 응답을 일관적인 형태로 제공하기 위한 클래스입니다.
 *
 * @param <T> 응답 데이터의 타입 (예: String, User, List<User> 등)
 *
 * 빌더 패턴(@Builder)을 사용하여 객체 생성 시 필요한 필드값만 설정할 수 있도록 하며,
 * 생성된 객체는 불변 상태를 유지합니다. 이는 응답 객체가 외부에서 변조될 가능성을 방지합니다.
 */
@Data
@Builder
public class ApiResponse<T> {

    private boolean success;         // 성공 여부
    private int status;              // HTTP 상태 코드
    private String message;          // 메시지
    private T data;                  // 실제 데이터
    private String timestamp;        // 응답 시간
    private String path;             // 요청 경로

}
