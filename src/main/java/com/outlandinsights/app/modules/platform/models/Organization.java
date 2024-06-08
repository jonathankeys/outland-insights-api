package com.outlandinsights.app.modules.platform.models;

import lombok.Builder;
import lombok.Data;

import java.io.Serializable;

@Builder
@Data
public class Organization implements Serializable {
    private String id;
    private String name;
    private String description;
    private String imageUrl;
    private String createdAt;
    private String updatedAt;
}
