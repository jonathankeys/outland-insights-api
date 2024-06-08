package com.outlandinsights.app.modules.security.models.http;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Builder
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ChangePasswordWithTokenRequest {
    private String email;
    private String newPassword;
    private String newPasswordConfirmation;
}
