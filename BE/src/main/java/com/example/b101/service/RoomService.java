package com.example.b101.service;

import com.example.b101.cache.Room;
import com.example.b101.dto.RoomRequest;
import com.example.b101.repository.RoomRepository;
import com.example.b101.common.ApiResponseUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class RoomService {

    private final RoomRepository roomRepository;

    public RoomService(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    public ResponseEntity<?> createRoom(RoomRequest roomRequest, HttpServletRequest request) {
        List<String> users = new ArrayList<>();
        users.add(roomRequest.getOwnerId());


        Room room = new Room(
                UUID.randomUUID().toString(),
                roomRequest.getName(),
                users,
                roomRequest.getOwnerId(),
                roomRequest.getMaxCapacity(),
                roomRequest.getPassword(),
                roomRequest.getLink());


        roomRepository.create(room);


        return ApiResponseUtil.success(room,
                "방이 생성 되었습니다.",
                HttpStatus.CREATED,
                request.getRequestURI());
    }

    public ResponseEntity<?> getAllRooms(HttpServletRequest request) {
        if (roomRepository.findAll().isEmpty()) {
            return ApiResponseUtil.failure("생성되어 있는 방이 없습니다.",
                    HttpStatus.NOT_FOUND,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(roomRepository.findAll(),
                "전체 방 정보 가져오기 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }


    public ResponseEntity<?> deleteRoom(String id, HttpServletRequest request) {
        if (roomRepository.findById(id) == null) {
            return ApiResponseUtil.failure("해당 roomId를 가진 방이 없습니다.",
                    HttpStatus.NOT_FOUND,
                    request.getRequestURI());
        }
        roomRepository.delete(id);
        return ApiResponseUtil.success(null,
                "방 삭제 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }

    // 방 입장하기
    public ResponseEntity<?> addUserToRoom(String userId, String roomId, HttpServletRequest request) {
        Room room = roomRepository.findById(roomId);
        if (room == null) {
            return ApiResponseUtil.failure("잘못된 방 ID입니다.",
                    HttpStatus.NOT_FOUND,
                    request.getRequestURI());
        }

        List<String> users = room.getUsers();
        if (users.contains(userId)) {
            return ApiResponseUtil.failure("이미 입장 되어있는 방입니다.",
                    HttpStatus.CONFLICT,
                    request.getRequestURI());
        }
        if (users.size() >= room.getMaxCapacity()) {
            return ApiResponseUtil.failure("방 정원이 다 찼습니다.",
                    HttpStatus.BAD_REQUEST,
                    request.getRequestURI());
        }

        users.add(userId);
        room.setUsers(users);

        roomRepository.put(room);

        return ApiResponseUtil.success(null,
                "방 입장 성공",
                HttpStatus.OK,
                request.getRequestURI());
    }


    //방 나가기
    public ResponseEntity<?> removeUserFromRoom(String sessionId, String roomId, HttpServletRequest request) {
        Room room = roomRepository.findById(roomId);

        // roomId와 일치하는 방이 없을 때
        if (room == null) {
            return ApiResponseUtil.failure("해당 roomId를 가진 방을 찾을 수 없습니다.",
                    HttpStatus.NOT_FOUND,
                    request.getRequestURI());
        }

        // sessionId가 방에 없는 경우
        if (!room.getUsers().contains(sessionId)) {
            return ApiResponseUtil.failure("해당 사용자가 방에 존재하지 않습니다.",
                    HttpStatus.NOT_FOUND,
                    request.getRequestURI());
        }

        // 방장이 나가려고 할 때
        if (room.getOwner().equals(sessionId)) {
            room.getUsers().remove(sessionId);

            // 방에 사용자가 남아있을 경우 새로운 방장 지정
            if (!room.getUsers().isEmpty()) {
                String newOwnerSessionId = room.getUsers().get(0); // 다음 사용자를 방장으로
                room.setOwner(newOwnerSessionId);
                room.setId(newOwnerSessionId); // roomId 업데이트
                roomRepository.put(room);

                return ApiResponseUtil.success(newOwnerSessionId,
                        "방장이 나갔습니다. 새로운 방장은 " + newOwnerSessionId + "입니다.",
                        HttpStatus.OK,
                        request.getRequestURI());
            } else {
                // 방에 사용자가 없으면 방 삭제
                roomRepository.delete(roomId);
                return ApiResponseUtil.success(null,
                        "방장이 방을 나가고 방이 삭제되었습니다.",
                        HttpStatus.OK,
                        request.getRequestURI());
            }
        }

        // 일반 사용자가 나가는 경우
        room.getUsers().remove(sessionId);
        roomRepository.put(room);

        return ApiResponseUtil.success(sessionId,
                sessionId + "님이 방을 나갔습니다.",
                HttpStatus.OK,
                request.getRequestURI());
    }


}
