package com.example.b101.repository;

import com.example.b101.domain.StoryCardVariants;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface StoryCardVariantsRepository extends JpaRepository<StoryCardVariants, Integer> {
}
