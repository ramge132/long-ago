package com.example.b101.domain;


import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class Room implements Serializable {

    @Id
    private String id;

    private String name;

    private List<String> users; //참가자 ID

    private String owner; //방장 ID

    private int maxCapacity;

    private String password;

    private String link;


}
