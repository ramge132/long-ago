package com.example.b101.handler;
// 필요한 라이브러리 임포트

import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

import java.util.concurrent.ConcurrentHashMap;

// WebSocket 핸들러 클래스 정의. 클라이언트와의 메시지 교환 및 연결 관리 역할을 담당.
public class SignalingHandler extends TextWebSocketHandler {

    // 클라이언트 세션을 저장하는 ConcurrentHashMap
    // Key: 클라이언트의 세션 ID, Value: WebSocketSession 객체
    private static final ConcurrentHashMap<String, WebSocketSession> sessions = new ConcurrentHashMap<>();

    // 클라이언트가 WebSocket 연결을 성공적으로 설정한 경우 호출되는 메서드
    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        // 새로 연결된 클라이언트를 sessions 맵에 추가
        sessions.put(session.getId(), session);
        System.out.println("Client connected: " + session.getId()); // 연결된 클라이언트의 세션 ID 출력
    }

    // 클라이언트가 서버로 텍스트 메시지를 보낼 때 호출되는 메서드
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        // 클라이언트가 보낸 메시지 내용 추출
        String payload = message.getPayload();
        System.out.println("Received message: " + payload); // 받은 메시지 출력

        // 모든 클라이언트에게 메시지를 브로드캐스트 (자신 포함)
        for (WebSocketSession s : sessions.values()) {
            if (s.isOpen()) { // 세션이 열려 있는 경우에만 메시지를 보냄
                s.sendMessage(new TextMessage(payload)); // 메시지 전송
            }
        }
    }

    // 클라이언트가 WebSocket 연결을 종료한 경우 호출되는 메서드
    @Override
    public void afterConnectionClosed(WebSocketSession session, org.springframework.web.socket.CloseStatus status) throws Exception {
        // 종료된 클라이언트의 세션을 sessions 맵에서 제거
        sessions.remove(session.getId());
        System.out.println("Client disconnected: " + session.getId()); // 연결 종료된 클라이언트의 세션 ID 출력
    }
}
