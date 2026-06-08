package com.trackit.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Entity
@Table(name = "patients")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Patient {

    @Id
    private String id; // TRK-001 format

    @Column(nullable = false, length = 11)
    private String nationalId;

    @Column(nullable = false)
    private String firstName;

    @Column(nullable = false)
    private String lastName;

    private String gender;
    private Integer age;
    private String dob;
    private String mobile;
    private String telephone;
    private String email;
    private String bloodType;
    private String genotype;
    private String department;
    private String maritalStatus;
    private String doctor;
    private String country;
    private String state;
    private String city;
    private String street;
    private String zip;

    // JSON array stored as text: [{type, detail}, ...]
    @Column(columnDefinition = "TEXT")
    private String contacts;

    private String status = "Active";
    private String registeredDate;

    @Column(columnDefinition = "TEXT")
    private String photo; // base64 or null
}
