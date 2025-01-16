package com.example.b101.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class LoginController {

    @GetMapping("/login")
    public String loginPage() {
        return "login"; // templates/login.mustache 렌더링
    }


    @GetMapping("/index")
    public String indexPage() {
        return "index";
    }

    @GetMapping("/login-fail")
    public String loginFailPage() {
        return "loginFail";
    }
}
