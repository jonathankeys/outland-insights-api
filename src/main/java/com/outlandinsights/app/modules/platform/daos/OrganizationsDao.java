package com.outlandinsights.app.modules.platform.daos;

import com.outlandinsights.app.database.Database;
import com.outlandinsights.app.modules.platform.models.Organization;
import com.outlandinsights.app.modules.platform.models.http.organizations.UpdateOrganizationRequest;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class OrganizationsDao {
    private static final String GET_ORGANIZATION_BY_ID = "select * from organizations where id = ?";

    public static Organization getById(final String id) throws SQLException {
        try(final Connection c = Database.getPlatformConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_ORGANIZATION_BY_ID);
            statement.setString(1, id);
            final ResultSet r = statement.executeQuery();
            if (r.next()) {
                return Organization.builder()
                        .id(r.getString("id"))
                        .name(r.getString("name"))
                        .description(r.getString("description"))
                        .imageUrl(r.getString("image_url"))
                        .createdAt(r.getString("created_at"))
                        .updatedAt(r.getString("updated_at"))
                        .build();
            }
        }
        return null;
    }

    public static void updateById(final String id, final UpdateOrganizationRequest request) throws SQLException {
        try(final Connection c = Database.getPlatformConnection()) {
            final PreparedStatement statement = c.prepareStatement(GET_ORGANIZATION_BY_ID);
            statement.setString(1, id);
            statement.executeUpdate();
        }
    }

    public static void deleteById(final String id) throws SQLException {

    }
}
