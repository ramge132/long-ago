package com.example.b101.controller;

import com.example.b101.dto.BookRequest;
import com.example.b101.service.BookService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/book")
@AllArgsConstructor
public class BookController {

    private final BookService bookService;

    @GetMapping("/{page}")
    public ResponseEntity<?> findAll(@PathVariable int page,@RequestParam int mode, HttpServletRequest request) {
        return bookService.getBooksByPageSortViewCnt(page, mode, request);
    }


    @GetMapping
    public ResponseEntity<?> findById(@RequestParam String id, HttpServletRequest request) {
        return bookService.getBookById(id, request);
    }


    @PostMapping
    public ResponseEntity<?> save(@RequestBody BookRequest book, HttpServletRequest request) {
        return bookService.saveBook(book, request);
    }


    @GetMapping("/top3")
    public ResponseEntity<?> findBook1to3(HttpServletRequest request) {
        return bookService.findBook1to3(request);
    }
}
