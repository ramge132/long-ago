package com.example.b101.controller;

import com.example.b101.dto.CreateRoomDto;
import com.example.b101.service.RoomService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


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


    @GetMapping
    public ResponseEntity<?> getAllRooms(HttpServletRequest request) {
        return roomService.getAllRooms(request);
    }

    @DeleteMapping
    public ResponseEntity<?> deleteRoom(@RequestParam String roomId,HttpServletRequest request) {
        return roomService.deleteRoom(roomId,request);
    }

    @PostMapping("/{roomId}")
    public ResponseEntity<?> enterRoom(@PathVariable String roomId, @RequestParam String userid,HttpServletRequest request) {
        return roomService.addUserToRoom(userid, roomId,request);
    }
}
