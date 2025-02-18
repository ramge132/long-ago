package com.example.b101.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class FinishGameResponse {

    String bookId;

    String title;

    String bookCover;
}
