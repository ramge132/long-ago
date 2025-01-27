package com.example.b101.domain;


import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Room implements Serializable {

    @Id
    private String id;

    private String name;

    private List<String> users; //참가자들 sessionID

    private String owner; //방장 sessionID

    private int maxCapacity;

    private String password;

    private String link;


}
