package com.example.b101;

import jakarta.annotation.PostConstruct;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

import java.util.TimeZone;

@SpringBootApplication
@EnableJpaAuditing // JPA Auditing 활성화
public class EreGgApplication {

    public static void main(String[] args) {
        SpringApplication.run(EreGgApplication.class, args);
    }

}
