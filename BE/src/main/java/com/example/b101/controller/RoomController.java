package com.example.b101.controller;

import com.example.b101.domain.Room;
import com.example.b101.dto.CreateRoomDto;
import com.example.b101.service.RoomService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/rooms")
public class RoomController {

    private final RoomService roomService;

    public RoomController(RoomService roomService) {
        this.roomService = roomService;
    }

    @PostMapping
    public ResponseEntity<?> createRoom(@RequestBody CreateRoomDto createRoomDto, HttpServletRequest request) {
        return roomService.createRoom(createRoomDto,request);
    }

    @GetMapping("/{id}")
    public Room getRoom(@PathVariable String id) {
        return roomService.getRoomById(id);
    }

    @GetMapping
    public List<Room> getAllRooms() {
        return roomService.getAllRooms();
    }

    @DeleteMapping
    public void deleteRoom(@RequestParam String id) {
        roomService.deleteRoom(id);
    }

    @PostMapping("/{roomId}")
    public ResponseEntity<?> enterRoom(@PathVariable String roomId, @RequestParam String userid,HttpServletRequest request) {
        return roomService.addUserToRoom(userid, roomId,request);
    }
}
