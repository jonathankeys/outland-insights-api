package com.outlandinsights.app.modules.platform.daos;

import com.outlandinsights.app.database.Database;
import com.outlandinsights.app.modules.platform.models.User;
import lombok.extern.log4j.Log4j2;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

@Log4j2
public class UsersDao {
    private static final String GET_USER_BY_ID = "select * from users where id = ?";
    private static final String GET_USER_BY_EMAIL = "select * from users where email = ?";
    private static final String INSERT_USER = "INSERT INTO users (id, first_name, last_name, email) VALUES (?, ?, ?, ?)";

    public static User getUserById(final String id) throws SQLException {
        try(final Connection c = Database.getPlatformConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_USER_BY_ID);
            statement.setString(1, id);
            final ResultSet r = statement.executeQuery();
            if (r.next()) {
                return User.builder()
                        .id(r.getString("id"))
                        .firstName(r.getString("first_name"))
                        .lastName(r.getString("last_name"))
                        .email(r.getString("email"))
                        .createdAt(r.getString("created_at"))
                        .updatedAt(r.getString("updated_at"))
                        .build();
            }
        }
        return null;
    }

    public static User getUserByEmail(final String email) throws SQLException {
        try(final Connection c = Database.getPlatformConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_USER_BY_EMAIL);
            statement.setString(1, email);
            final ResultSet r = statement.executeQuery();
            if (r.next()) {
                return User.builder()
                        .id(r.getString("id"))
                        .firstName(r.getString("first_name"))
                        .lastName(r.getString("last_name"))
                        .email(r.getString("email"))
                        .createdAt(r.getString("created_at"))
                        .updatedAt(r.getString("updated_at"))
                        .build();
            }
        }
        return null;
    }

    public static User createUser(final String email, final String firstName, final String lastName, final String id) throws SQLException {
        try(final Connection c = Database.getPlatformConnection()) {
            final PreparedStatement statement = c.prepareStatement(INSERT_USER);
            statement.setString(1, id);
            statement.setString(2, firstName);
            statement.setString(3, lastName);
            statement.setString(4, email);
            statement.executeUpdate();

            return getUserById(id);
        }
    }
}
