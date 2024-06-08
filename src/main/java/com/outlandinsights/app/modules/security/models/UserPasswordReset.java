package com.outlandinsights.app.modules.security.models;

import lombok.Builder;
import lombok.Data;

import java.io.Serializable;
import java.sql.Timestamp;

@Builder
@Data
public class UserPasswordReset implements Serializable {
    private String userId;
    private String token;
    private Timestamp expiryTime;
}

