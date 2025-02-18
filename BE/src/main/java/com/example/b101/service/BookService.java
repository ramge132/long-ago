package com.example.b101.service;

import com.example.b101.common.ApiResponseUtil;
import com.example.b101.domain.Book;
import com.example.b101.dto.BookRequest;
import com.example.b101.dto.BookResponse;
import com.example.b101.dto.SceneResponse;
import com.example.b101.repository.BookRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class BookService {

    private final BookRepository bookRepository;


    // 1~3위 책 데이터 조회
    public ResponseEntity<?> findBook1to3(HttpServletRequest request) {
        log.info("[findBook1to3] 1~3위 책 데이터 요청");

        Page<Book> books1to3 = bookRepository.findAll(PageRequest.of(0, 3, Sort.by(Sort.Direction.DESC, "viewCnt")));
        log.info("[findBook1to3] 1~3위 책 데이터 반환: {}개", books1to3.getContent().size());

        return ApiResponseUtil.success(books1to3.getContent(), "1~3위 책 데이터 반환", HttpStatus.OK, request.getRequestURI());
    }

    // 조회수 순 정렬된 페이지네이션된 책 데이터 조회
    public ResponseEntity<?> getBooksByPageSort(int page, int mode, HttpServletRequest request) {
        log.info("[getBooksByPageSort] 페이지 요청: page={}, mode={}", page, mode);

        Page<Book> books;
        if (mode == 0) {
            books = bookRepository.findAll(PageRequest.of(page - 1, 13, Sort.by(Sort.Direction.DESC, "viewCnt")));
            log.info("[getBooksByPageSort] 조회수 기준 정렬된 데이터 {}개 조회", books.getContent().size());

            if (books.getContent().size() < 9) {
                log.warn("[getBooksByPageSort] 조회된 데이터가 부족함 ({}개)", books.getContent().size());
                return ApiResponseUtil.success(books.getContent(), "book 데이터 조회수순으로 불러왔습니다. (pageSize보다 작음)",
                        HttpStatus.NOT_FOUND, request.getRequestURI());
            }

            return ApiResponseUtil.success(books.getContent().subList(3, 13),
                    "book 데이터를 조회수순으로 불러왔습니다.",
                    HttpStatus.OK,
                    request.getRequestURI());
        }

        books = bookRepository.findAll(PageRequest.of(page - 1, 13, Sort.by(Sort.Direction.DESC, "createdAt")));
        log.info("[getBooksByPageSort] 최신순 정렬된 데이터 {}개 조회", books.getContent().size());

        Page<Book> books1to3 = bookRepository.findAll(PageRequest.of(0, 3, Sort.by(Sort.Direction.DESC, "viewCnt")));
        List<Book> books1to3Content = books1to3.getContent();

        List<Book> bookList = books.getContent().stream()
                .filter(book -> !books1to3Content.contains(book))
                .toList();

        if (bookList.size() < 9) {
            log.warn("[getBooksByPageSort] 최신순 데이터가 부족함 ({}개)", bookList.size());
            return ApiResponseUtil.success(bookList,
                    "book 데이터 최신순으로 불러왔습니다. (pageSize보다 작음)",
                    HttpStatus.OK,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(bookList.subList(0, 9),
                "book 데이터 최신순으로 불러왔습니다.",
                HttpStatus.OK,
                request.getRequestURI());
    }

    // 특정 ID의 책 정보 가져오기
    public ResponseEntity<?> getBookById(String id, HttpServletRequest request) {
        log.info("[getBookById] 책 조회 요청: ID={}", id);

        Book book = bookRepository.findBookByBookId(id).stream().findFirst().orElse(null);

        if (book == null) {
            log.warn("[getBookById] 해당 ID의 책이 없음: ID={}", id);
            return ApiResponseUtil.failure("해당 Id의 book이 없습니다.",
                    HttpStatus.NOT_FOUND, request.getRequestURI());
        }

        book.setViewCnt(book.getViewCnt() + 1);
        bookRepository.saveAndFlush(book); //조회수 즉시 반영
        log.info("[getBookById] 책 조회 성공 및 조회수 증가: ID={}, 조회수={}", id, book.getViewCnt());

        BookResponse bookResponse = BookResponse.builder()
                .title(book.getTitle())
                .sceneResponseList(book.getScenes().stream()
                        .map(scene -> new SceneResponse(scene.getSceneOrder(), scene.getImageUrl(), scene.getUserPrompt()))
                        .toList())
                .bookCover(book.getImageUrl())
                .build();

        return ApiResponseUtil.success(bookResponse, "book 데이터 반환 성공", HttpStatus.OK, request.getRequestURI());
    }


    @Scheduled(cron = "0 0 12 * * *")  // 매일 정오에 실행
    public void autoDeleteBook() {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(7);
        int deletedCount = bookRepository.deleteByCreatedAtBefore(cutoffDate);

        log.info("🔍 {}개의 책이 삭제되었습니다. (기준일: {})", deletedCount, cutoffDate);
    }
}
