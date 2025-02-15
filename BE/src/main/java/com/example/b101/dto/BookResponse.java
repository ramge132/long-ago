package com.example.b101.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class BookResponse {

    String title;

    List<SceneResponse> sceneResponseList;

    String bookCover;
}
