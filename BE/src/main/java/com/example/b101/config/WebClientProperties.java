package com.example.b101.config;

import jakarta.annotation.PostConstruct;
import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import java.util.List;

@Getter
@Setter
@Component
@ConfigurationProperties(prefix = "webclient.base")
public class WebClientProperties {
    private List<String> url;

    @PostConstruct
    public void init() {
        System.out.println("📌 WebClient Base URLs: " + url);
    }
}
