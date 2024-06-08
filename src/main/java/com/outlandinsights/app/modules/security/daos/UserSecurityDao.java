package com.outlandinsights.app.modules.security.daos;

import com.outlandinsights.app.database.Database;
import com.outlandinsights.app.modules.security.models.UserPasswordReset;
import com.outlandinsights.app.modules.security.models.UserSecurity;
import lombok.extern.log4j.Log4j2;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;

@Log4j2
public class UserSecurityDao {

    private static final String INSERT_USER_SECURITY = "INSERT INTO user_passwords (user_id, \"password\") VALUES(?, ?)";
    private static final String USER_RESET_PASSWORD_INSERT = "INSERT INTO user_password_reset (user_id, token, expiry_time) VALUES(?, ?, ?)";
    private static final String GET_USER_BY_RESET_TOKEN = "SELECT * FROM user_password_reset WHERE \"token\" = ?";
    private static final String USER_RESET_PASSWORD_DELETE_BY_USER_ID = "DELETE FROM user_password_reset WHERE user_id = ?";
    private static final String USER_RESET_PASSWORD_DELETE_BY_TOKEN = "DELETE FROM user_password_reset WHERE token = ?";
    private static final String USER_PASSWORD_UPDATE = "UPDATE user_passwords SET password = ? WHERE user_id = ?";
    private static final String GET_USER_SECURITY_BY_ID = "SELECT * FROM user_passwords where user_id = ?";

    public static void insertUserPassword(final String userId, final String password) throws SQLException {
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(INSERT_USER_SECURITY);
            statement.setString(1, userId);
            statement.setString(2, password);
            statement.executeUpdate();
        }
    }

    public static void updateUserPassword(final String userId, final String newPassword) throws SQLException {
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(USER_PASSWORD_UPDATE);
            statement.setString(1, newPassword);
            statement.setString(2, userId);
            statement.executeUpdate();
        }
    }

    public static void setResetPasswordRecord(final String userId, final String token) throws SQLException {
        // Set date for when token expires at
        final Timestamp timestamp = new Timestamp(Instant.now().plus(Duration.ofHours(1)).toEpochMilli());

        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(USER_RESET_PASSWORD_INSERT);
            statement.setString(1, userId);
            statement.setString(2, token);
            statement.setTimestamp(3, timestamp);
            statement.executeUpdate();
        }
    }

    public static UserPasswordReset getPasswordResetByToken(final String token) throws SQLException{
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_USER_BY_RESET_TOKEN);
            statement.setString(1, token);
            final ResultSet r = statement.executeQuery();
            if (r.next()) {
                return UserPasswordReset.builder()
                        .userId(r.getString("user_id"))
                        .token(r.getString("token"))
                        .expiryTime(r.getTimestamp("expiry_time"))
                        .build();
            }
        }
        return null;
    }

    public static void deletePasswordResetsForUser(final String userId) throws SQLException {
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(USER_RESET_PASSWORD_DELETE_BY_USER_ID);
            statement.setString(1, userId);
            statement.executeUpdate();
        }
    }

    public static void deletePasswordResetByToken(final String token) throws SQLException {
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(USER_RESET_PASSWORD_DELETE_BY_TOKEN);
            statement.setString(1, token);
            statement.executeUpdate();
        }
    }

    public static UserSecurity getUserSecurityById(final String id) throws SQLException {
        try(final Connection c = Database.getSecurityConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_USER_SECURITY_BY_ID);
            statement.setString(1, id);
            final ResultSet r = statement.executeQuery();
            if (r.next()) {
                return UserSecurity.builder()
                        .userId(r.getString("user_id"))
                        .password(r.getString("password"))
                        .build();
            }
        }
        return null;
    }
}
