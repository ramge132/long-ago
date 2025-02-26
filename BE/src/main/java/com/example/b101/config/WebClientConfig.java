package com.example.b101.config;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

import java.time.Duration;
import java.util.ArrayList;
import java.util.List;

@Configuration
public class WebClientConfig {


    @Value("${WEBCLIENT.BASE.URL_0}")
    private String baseUrl0;

    @Value("${WEBCLIENT.BASE.URL_1}")
    private String baseUrl1;

    @Value("${WEBCLIENT.BASE.URL_2}")
    private String baseUrl2;

    @Value("${WEBCLIENT.BASE.URL_3}")
    private String baseUrl3;

    @Value("${WEBCLIENT.BASE.URL_4}")
    private String baseUrl4;

    @Value("${WEBCLIENT.BASE.URL_5}")
    private String baseUrl5;

    @Value("${WEBCLIENT.BASE.URL_6}")
    private String baseUrl6;

    @Value("${WEBCLIENT.BASE.URL_7}")
    private String baseUrl7;

    @Value("${WEBCLIENT.BASE.URL_8}")
    private String baseUrl8;

    @Getter
    private List<String> baseUrls = new ArrayList<>();


    @Bean
    public WebClient webClient(WebClient.Builder builder) {
        baseUrls.add(baseUrl0);
        baseUrls.add(baseUrl1);
        baseUrls.add(baseUrl2);
        baseUrls.add(baseUrl3);
        baseUrls.add(baseUrl4);
        baseUrls.add(baseUrl5);
        baseUrls.add(baseUrl6);
        baseUrls.add(baseUrl7);
        baseUrls.add(baseUrl8);


        //WebClient 객체를 빌드하는데 요청 하나의 버퍼 크기를 최대 2MB로 지정.
        //WebClient의 응답 제한 시간을 5분으로 지정 (기본 값은 30초)
        return builder
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(2 * 1024 * 1024))
                .clientConnector(new ReactorClientHttpConnector(HttpClient.create().responseTimeout(Duration.ofMinutes(5))))
                .build();
    }
}
