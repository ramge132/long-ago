package com.example.b101.config;

import com.example.b101.domain.Room;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {

    @Value("${spring.data.redis.port}")
    private int port;

    @Value("${spring.data.redis.host}")
    private String host;


    @Bean
    public LettuceConnectionFactory redisConnectionFactory() {
        // Lettuce라는 라이브러리를 활용해 Redis 연결을 관리하는 객체를 생성하고
        // Redis 서버에 대한 정보(host, port)를 설정한다.
        return new LettuceConnectionFactory(new RedisStandaloneConfiguration(host, port));
    }


    @Bean
    public RedisTemplate<String, Room> redisTemplate(LettuceConnectionFactory redisConnectionFactory) {
        RedisTemplate<String, Room> template = new RedisTemplate<>();
        template.setConnectionFactory(redisConnectionFactory);

        // JSON 직렬화 설정
        GenericJackson2JsonRedisSerializer serializer = new GenericJackson2JsonRedisSerializer();
        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        template.setKeySerializer(stringSerializer);  // Key는 문자열로 직렬화
        template.setValueSerializer(serializer);      // Value는 JSON 직렬화
        template.setHashKeySerializer(stringSerializer); //해시 key눈 문자열로 직렬화
        template.setHashValueSerializer(serializer); //해시 value는 JSON 직렬화

        return template;
    }

}
