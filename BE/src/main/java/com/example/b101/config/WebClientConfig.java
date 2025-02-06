package com.example.b101.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Configuration
public class WebClientConfig {

    @Bean
    public WebClient webClient(WebClient.Builder builder) {

        //WebClient 객체를 빌드하는데 요청 하나의 버퍼 크기를 최대 2MB로 지정.
        return builder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(2 * 1024 * 1024))
                .baseUrl("http://{SERVER_HOST}:{PORT}")
                .build();
    }
}
