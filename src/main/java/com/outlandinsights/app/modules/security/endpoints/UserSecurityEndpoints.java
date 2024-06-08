package com.outlandinsights.app.modules.security.endpoints;

import com.outlandinsights.app.modules.platform.daos.UsersDao;
import com.outlandinsights.app.modules.security.daos.UserSecurityDao;
import com.outlandinsights.app.modules.security.models.http.ChangePasswordRequest;
import com.outlandinsights.app.modules.security.models.http.ChangePasswordWithTokenRequest;
import com.outlandinsights.app.modules.security.models.http.LoginRequest;
import com.outlandinsights.app.modules.security.models.http.SignUpRequest;
import com.outlandinsights.app.modules.platform.models.User;
import com.outlandinsights.app.modules.security.models.http.ResetPasswordRequest;
import com.outlandinsights.app.modules.security.models.UserPasswordReset;
import com.outlandinsights.app.modules.security.utils.SecurityUtils;
import io.javalin.apibuilder.EndpointGroup;
import io.javalin.http.BadRequestResponse;
import io.javalin.http.Context;
import io.javalin.http.InternalServerErrorResponse;
import io.javalin.http.UnauthorizedResponse;
import lombok.extern.log4j.Log4j2;
import org.apache.logging.log4j.ThreadContext;
import org.eclipse.jetty.http.HttpStatus;

import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.UUID;

import static io.javalin.apibuilder.ApiBuilder.post;

@Log4j2
public class UserSecurityEndpoints implements EndpointGroup {
    public void login(final Context ctx) {
        final LoginRequest request = ctx.bodyAsClass(LoginRequest.class);
        if (ctx.req().getSession().getAttribute("user_id") != null) {
            final String userId = (String) ctx.req().getSession().getAttribute("user_id");
            try {
                // Should not be using UserDao, in future if this is broken out into a microservice this should be
                // moved in to a service call.
                final User user = UsersDao.getUserById(userId);
                if (user.getEmail().equals(request.getEmail())) {
                    log.info("Session already exists, changing session id");
                    ctx.status(201);
                    ctx.req().changeSessionId();
                    return;
                }
                log.error("Currently cached user is not the same as the one logging in, invalidate the current " +
                        "session and continue with login process.");
                ctx.req().getSession().invalidate();
            } catch (SQLException e) {
                log.error("Exception getting current user in login flow", e);
                throw new InternalServerErrorResponse();
            }
        }

        try {
            final User user = UsersDao.getUserByEmail(request.getEmail());
            final boolean isVerified = SecurityUtils.verifyPassword(user.getId(), request.getPassword());
            if (isVerified) {
                ctx.req().getSession().setAttribute("user_id", user.getId());
                ctx.req().getSession().setAttribute("session_id", ctx.req().getSession().getId());
                ThreadContext.put("session_id", ctx.req().getSession().getId());
                ctx.status(200);
                return;
            }
        } catch (SQLException e) {
            log.error("Exception logging in user", e);
            throw new InternalServerErrorResponse();
        }
        throw new BadRequestResponse("Invalid email or password");
    }

    // May need to send response to delete cookie on client side
    public void logout(final Context ctx) {
        ctx.req().getSession().invalidate();
        ctx.removeCookie("JSESSIONID");
        ctx.status(200);
    }

    public void signUp(final Context ctx) {
        final SignUpRequest request = ctx.bodyAsClass(SignUpRequest.class);
        try {
            final String id = UUID.randomUUID().toString();
            final User user = UsersDao.createUser(request.getEmail(), request.getFirstName(), request.getLastName(), id);
            final String hashedPassword = SecurityUtils.hashPassword(request.getPassword());
            UserSecurityDao.insertUserPassword(user.getId(), hashedPassword);
            ctx.status(201);
        } catch (SQLException e) {
            log.error("Error signing up user", e);
            throw new InternalServerErrorResponse();
        }
    }

    public void changePassword(final Context ctx) {
        final ChangePasswordRequest request = ctx.bodyAsClass(ChangePasswordRequest.class);


        final String userId = (String) ctx.req().getSession().getAttribute("user_id");
        if (userId == null) {
            throw new UnauthorizedResponse();
        }

        if (!request.getNewPassword().equals(request.getNewPasswordConfirmation())) {
            log.error("Provided passwords do not match for password change");
            throw new BadRequestResponse("New password and new password confirmation must match");
        }

        try {
            final boolean isVerified = SecurityUtils.verifyPassword(userId, request.getOldPassword());
            if (!isVerified) {
                throw new BadRequestResponse("Invalid user or password");
            }

            UserSecurityDao.updateUserPassword(userId, SecurityUtils.hashPassword(request.getNewPassword()));
            ctx.status(HttpStatus.Code.OK.getCode());
        } catch (SQLException e) {
            log.error("Provided old password is not correct for user");
            throw new InternalServerErrorResponse();
        }
    }

    public void changePasswordWithToken(final Context ctx) {
        final ChangePasswordWithTokenRequest request = ctx.bodyAsClass(ChangePasswordWithTokenRequest.class);
        final String token = ctx.queryParam("token");

        if (!request.getNewPassword().equals(request.getNewPasswordConfirmation())) {
            log.error("Provided passwords do not match for password change");
            throw new BadRequestResponse("new password and new password confirmation must match");
        }

        try {
            final UserPasswordReset userPasswordReset = UserSecurityDao.getPasswordResetByToken(token);
            if (userPasswordReset == null) {
                log.warn("User attempted to reset password for token={} which no longer exists", token);
                throw new BadRequestResponse();
            }

            if (userPasswordReset.getExpiryTime().before(Timestamp.from(Instant.now()))) {
                UserSecurityDao.deletePasswordResetByToken(token);
                log.error("Password reset expiry is outdated");
                throw new BadRequestResponse("Token is outdated");
            }

            UserSecurityDao.updateUserPassword(userPasswordReset.getUserId(), SecurityUtils.hashPassword(request.getNewPassword()));
            UserSecurityDao.deletePasswordResetsForUser(userPasswordReset.getUserId());

            ctx.status(HttpStatus.Code.OK.getCode());
        } catch (SQLException e) {
            log.error("Error attempting to change users password with a token");
            throw new InternalServerErrorResponse();
        }
    }

    public void resetPassword(final Context ctx) {
        final ResetPasswordRequest request = ctx.bodyAsClass(ResetPasswordRequest.class);
        final String resetToken = UUID.randomUUID().toString();
        try {
            final User user = UsersDao.getUserByEmail(request.getEmail());
            UserSecurityDao.setResetPasswordRecord(user.getId(), resetToken);
            ctx.status(HttpStatus.Code.OK.getCode());
        } catch (SQLException e) {
            log.error("Error setting reset password", e);
            throw new InternalServerErrorResponse();
        }
    }

    @Override
    public void addEndpoints() {
        post("/sign-up", this::signUp);
        post("/login", this::login);
        post("/logout", this::logout);
        post("/change-password", this::changePassword);
        post("/change-password/token", this::changePasswordWithToken);
        post("/reset-password", this::resetPassword);
    }
}
