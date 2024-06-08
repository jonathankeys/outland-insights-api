package com.outlandinsights.app.modules.platform.models;

import lombok.Builder;
import lombok.Data;

import java.io.Serializable;

@Builder
@Data
public class User implements Serializable {
    private String id;
    private String firstName;
    private String lastName;
    private String email;
    private String createdAt;
    private String updatedAt;
}

