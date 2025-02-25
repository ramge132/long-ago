package com.example.b101.config;

import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;

@Configuration
@EnableConfigurationProperties(WebClientProperties.class)
public class WebClientConfig {

    @Bean
    public WebClient webClient(WebClient.Builder builder) {


        //WebClient 객체를 빌드하는데 요청 하나의 버퍼 크기를 최대 2MB로 지정.
        //WebClient의 응답 제한 시간을 5분으로 지정 (기본 값은 30초)
        return builder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(2 * 1024 * 1024))
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create().responseTimeout(Duration.ofMinutes(5))))
                .build();
    }
}
