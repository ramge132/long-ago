package com.example.b101.domain;


import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Room implements Serializable {

    @Id
    private String id;

    private String name;

//    private List<User> users;

    private int maxCapacity;

    private String password;

    private String link;


}
