package com.example.b101;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;


@SpringBootApplication
@EnableJpaAuditing // JPA Auditing 활성화
@EnableCaching //레디스 캐싱 기능 활성화
public class EreGgApplication {

    public static void main(String[] args) {

        SpringApplication.run(EreGgApplication.class, args);
    }

}
