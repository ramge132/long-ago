package com.example.b101.service;

import com.example.b101.domain.Room;
import com.example.b101.dto.CreateRoomDto;
import com.example.b101.repository.RoomRepository;
import com.example.b101.response.ApiResponseUtil;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class RoomService {

    private final RoomRepository roomRepository;

    public RoomService(RoomRepository roomRepository) {
        this.roomRepository = roomRepository;
    }

    public ResponseEntity<?> createRoom(CreateRoomDto createRoomDto,HttpServletRequest request) {
        Room room = new Room();
        room.setId(createRoomDto.getId());
        room.setName(createRoomDto.getName());
        room.setPassword(createRoomDto.getPassword());
        room.setLink(createRoomDto.getLink());
        room.setOwner(createRoomDto.getOwnerId());
        room.setMaxCapacity(createRoomDto.getMaxCapacity());

        List<String> users = new ArrayList<>();
        users.add(createRoomDto.getOwnerId());
        room.setUsers(users);

        roomRepository.create(room);

        return ApiResponseUtil.success(room, "방이 생성 되었습니다.", HttpStatus.CREATED,request.getRequestURI());
    }

    public Room getRoomById(String id) {
        return roomRepository.findById(id);
    }

    public List<Room> getAllRooms() {
        return roomRepository.findAll();
    }

    public void deleteRoom(String id) {
        roomRepository.delete(id);
    }

    // 사용자 추가
    public ResponseEntity<?> addUserToRoom(String userId, String roomId,HttpServletRequest request) {
        Room room = roomRepository.findById(roomId);
        if (room == null) {
            return ApiResponseUtil.failure("잘못된 방 ID입니다.", HttpStatus.NOT_FOUND,request.getRequestURI());
        }

        List<String> users = room.getUsers();
        if (users.contains(userId)) {
            return ApiResponseUtil.failure("이미 입장 되어있는 방입니다.", HttpStatus.CONFLICT,request.getRequestURI());
        }
        if (users.size() >= room.getMaxCapacity()) {
            return ApiResponseUtil.failure("방 정원이 다 찼습니다.", HttpStatus.BAD_REQUEST,request.getRequestURI());
        }

        users.add(userId);
        room.setUsers(users);

        roomRepository.put(room);

        return ApiResponseUtil.success(null,"방 입장 성공",HttpStatus.OK,request.getRequestURI());
    }

}
