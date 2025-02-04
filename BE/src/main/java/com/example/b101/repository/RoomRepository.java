package com.example.b101.repository;

import com.example.b101.cache.Room;

import java.util.List;

public interface RoomRepository {

    void create(Room room); //방 생성

    Room findById(String id); //방 아이디로 조회

    List<Room> findAll(); //모든 방 정보 조회

    void delete(String id); //방 삭제

    void put(Room room); //방 정보 수정
}
