package com.example.b101.controller;
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
        return bookService.getBooksByPageSort(page, mode, request);
    }


    @GetMapping
    public ResponseEntity<?> findById(@RequestParam String id, HttpServletRequest request) {
        return bookService.getBookById(id, request);
    }


    @GetMapping("/top3")
    public ResponseEntity<?> findBook1to3(HttpServletRequest request) {
        return bookService.findBook1to3(request);
    }
}
