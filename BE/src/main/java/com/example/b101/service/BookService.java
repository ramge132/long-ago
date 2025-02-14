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
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class BookService {

    private final BookRepository bookRepository;


    public ResponseEntity<?> saveBook(BookRequest bookRequest, HttpServletRequest request) {
        Book book = Book.builder()
                .id(UUID.randomUUID().toString())
                .title(bookRequest.getTitle())
                .imageUrl(bookRequest.getImageUrl())
                .build();

        bookRepository.save(book);

        return ApiResponseUtil.success(book,
                "저장 성공",
                HttpStatus.CREATED,
                request.getRequestURI());
    }

    //1,2,3위 책 데이터
    public ResponseEntity<?> findBook1to3 (HttpServletRequest request) {
        //1,2,3위의 책 데이터
        Page<Book> books1to3 = bookRepository.findAll(PageRequest.of(0,3,Sort.by(Sort.Direction.DESC,"viewCnt")));


        return ApiResponseUtil.success(books1to3.getContent(),
                "1~3위 책 데이터 반환",
                HttpStatus.OK,
                request.getRequestURI());
    }

    //조회수 순 페이지네이션
    public ResponseEntity<?> getBooksByPageSort(int page, int mode, HttpServletRequest request) {

        Page<Book> books;

        if(mode==0){
            //해당하는 페이지의 12개의 책 데이터를 가져옴 (조회수 순)
            books = bookRepository.findAll(PageRequest.of(page-1, 13, Sort.by(Sort.Direction.DESC,"viewCnt")));

            if(books.getContent().size()<9){
                return ApiResponseUtil.success(books.getContent(),"book 데이터 조회수순으로 불러왔습니다. (pageSize보다 작음)",
                        HttpStatus.NOT_FOUND,
                        request.getRequestURI());
            }

            return ApiResponseUtil.success(books.getContent().subList(3,13),
                    "book 데이터를 조회수순으로 불러왔습니다.",
                    HttpStatus.OK,
                    request.getRequestURI());
        }

        //해당하는 페이지의 12개의 책 데이터를 가져옴 (최신순)
        books = bookRepository.findAll(PageRequest.of(page-1, 13, Sort.by(Sort.Direction.DESC,"createdAt")));


        //1,2,3위의 책 데이터
        Page<Book> books1to3 = bookRepository.findAll(PageRequest.of(0,3,Sort.by(Sort.Direction.DESC,"viewCnt")));

        List<Book> books1to3Content = books1to3.getContent();

        List<Book> bookList = books.getContent().stream().filter(book -> !books1to3Content.contains(book)).toList();

        if(bookList.size()<9){
            return ApiResponseUtil.success(bookList,
                    "book 데이터 최신순으로 불러왔습니다. (pageSize보다 작음)",
                    HttpStatus.OK,
                    request.getRequestURI());
        }

        return ApiResponseUtil.success(bookList.subList(0,9),
                "book 데이터 최신순으로 불러왔습니다.",
                HttpStatus.OK,
                request.getRequestURI());

    }


    //book 정보 가져오기
    public ResponseEntity<?> getBookById(String id,HttpServletRequest request) {
        Book book = bookRepository.findBookById(id).stream().findFirst().orElse(null);

        if(book == null) {
            return ApiResponseUtil.failure("해당 Id의 book이 없습니다.",
                    HttpStatus.NOT_FOUND,request.getRequestURI());
        }

        book.setViewCnt(book.getViewCnt()+1);
        bookRepository.save(book);

        BookResponse bookResponse = BookResponse.builder()
                .bookCover(book.getImageUrl())
                .title(book.getTitle())
                .sceneResponseList(book.getScenes().stream().map(scene -> new SceneResponse(scene.getSceneOrder(), scene.getImageUrl(), scene.getUserPrompt())).toList())
                .build();

        return ApiResponseUtil.success(bookResponse,"book 데이터 반환 성공",HttpStatus.OK,request.getRequestURI());
    }
}
