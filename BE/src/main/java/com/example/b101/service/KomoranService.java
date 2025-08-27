package com.example.b101.service;

import kr.co.shineware.nlp.komoran.constant.DEFAULT_MODEL;
import kr.co.shineware.nlp.komoran.core.Komoran;
import kr.co.shineware.nlp.komoran.model.KomoranResult;
import kr.co.shineware.nlp.komoran.model.Token;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.List;

/**
 * KOMORAN 형태소 분석기 서비스
 * 싱글턴 패턴으로 성능 최적화
 */
@Slf4j
@Service
public class KomoranService {
    
    private Komoran komoran;
    
    @PostConstruct
    public void init() {
        log.info("KOMORAN 형태소 분석기 초기화 시작");
        long startTime = System.currentTimeMillis();
        
        this.komoran = new Komoran(DEFAULT_MODEL.LIGHT);
        
        long endTime = System.currentTimeMillis();
        log.info("KOMORAN 형태소 분석기 초기화 완료 - 소요시간: {}ms", endTime - startTime);
    }
    
    /**
     * 텍스트를 형태소 분석하여 토큰 리스트 반환
     */
    public List<Token> analyze(String text) {
        if (text == null || text.trim().isEmpty()) {
            return List.of();
        }
        
        try {
            KomoranResult result = komoran.analyze(text);
            return result.getTokenList();
        } catch (Exception e) {
            log.error("형태소 분석 중 오류 발생: {}", e.getMessage(), e);
            return List.of();
        }
    }
    
    /**
     * 텍스트에서 명사, 형용사, 동사만 추출
     */
    public List<String> extractKeywords(String text) {
        List<Token> tokens = analyze(text);
        return tokens.stream()
                .filter(token -> {
                    String pos = token.getPos();
                    // 명사(NN), 형용사(VA), 동사(VV) 등 의미있는 품사만 추출
                    return pos.startsWith("NN") || pos.startsWith("VA") || pos.startsWith("VV");
                })
                .map(Token::getMorph)
                .distinct()
                .toList();
    }
}