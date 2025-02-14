package com.example.b101.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SignUpRequest {

    private String email;
    private String password;
}
