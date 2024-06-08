package com.outlandinsights.app.modules.platform.models.http.organizations;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Builder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class UpdateOrganizationRequest {
    private String name;
    private String description;
    private String imageUrl;
}
