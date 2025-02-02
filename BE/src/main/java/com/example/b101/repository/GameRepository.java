package com.example.b101.repository;

import com.example.b101.domain.Game;

import java.util.List;

public interface GameRepository {

    void save(Game game);

    void delete(Game game);

    void update(Game game);

    Game findById(int id);

//    List<Game> findAll();
}
