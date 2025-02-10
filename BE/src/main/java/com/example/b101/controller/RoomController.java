package com.example.b101.controller;

import com.example.b101.dto.RoomRequest;
import com.example.b101.service.RoomService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController
@RequestMapping("/rooms")
@AllArgsConstructor
public class RoomController {

    private final RoomService roomService;


    @PostMapping
    public ResponseEntity<?> createRoom(@RequestBody RoomRequest roomRequest, HttpServletRequest request) {
        return roomService.createRoom(roomRequest, request);
    }


    @GetMapping
    public ResponseEntity<?> getAllRooms(HttpServletRequest request) {
        return roomService.getAllRooms(request);
    }


    @DeleteMapping
    public ResponseEntity<?> deleteRoom(@RequestParam String roomId, HttpServletRequest request) {
        return roomService.deleteRoom(roomId, request);
    }

    @PostMapping("/{roomId}")
    public ResponseEntity<?> enterRoom(@PathVariable String roomId, @RequestParam String userId, HttpServletRequest request) {
        return roomService.addUserToRoom(userId, roomId, request);
    }


    @PatchMapping("/{roomId}")
    public ResponseEntity<?> leaveRoom(@PathVariable String roomId, @RequestParam String userId, HttpServletRequest request) {
        return roomService.removeUserFromRoom(userId, roomId, request);
    }

}
