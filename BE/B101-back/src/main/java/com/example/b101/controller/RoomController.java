package com.example.b101.controller;

import com.example.b101.domain.Room;
import com.example.b101.service.RoomService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/rooms")
public class RoomController {

    @Autowired
    private RoomService roomService;

    @PostMapping
    public void createRoom(@RequestBody Room room) {
        roomService.createRoom(room);
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
    public void deleteRoom(@RequestBody Room room) {
        roomService.deleteRoom(room);
    }
}
