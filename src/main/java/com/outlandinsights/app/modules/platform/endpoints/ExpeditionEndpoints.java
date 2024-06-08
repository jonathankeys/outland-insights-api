package com.outlandinsights.app.modules.platform.endpoints;

import com.outlandinsights.app.modules.platform.daos.OrganizationsDao;
import com.outlandinsights.app.modules.platform.models.Organization;
import com.outlandinsights.app.modules.platform.models.http.organizations.UpdateOrganizationRequest;
import io.javalin.apibuilder.CrudHandler;
import io.javalin.http.Context;
import io.javalin.http.InternalServerErrorResponse;
import io.javalin.http.NotFoundResponse;
import org.eclipse.jetty.http.HttpStatus;
import org.jetbrains.annotations.NotNull;

import java.sql.SQLException;

public class ExpeditionEndpoints implements CrudHandler {
    @Override
    public void create(@NotNull final Context cxt) {

    }

    @Override
    public void getAll(@NotNull final Context cxt) {
//        final List<Organization> organizations = OrganizationsDao.queryAllOrganizations();
//        cxt.json(organizations);
        cxt.status(HttpStatus.Code.OK.getCode());
    }

    @Override
    public void getOne(@NotNull final Context cxt, @NotNull final String id) {
        try {
            final Organization organization = OrganizationsDao.getById(id);

            if (organization != null) {
                cxt.json(organization);
                cxt.status(HttpStatus.Code.OK.getCode());
                return;
            }

        } catch (SQLException e) {
            throw new InternalServerErrorResponse();
        }
        throw new NotFoundResponse();
    }

    @Override
    public void update(@NotNull final Context cxt, @NotNull final String id) {
        final UpdateOrganizationRequest request = cxt.bodyAsClass(UpdateOrganizationRequest.class);
        try {
            OrganizationsDao.updateById(id, request);
            cxt.status(HttpStatus.Code.OK.getCode());
        } catch (SQLException e) {
            throw new InternalServerErrorResponse();
        }
    }

    @Override
    public void delete(@NotNull final Context cxt, @NotNull final String id) {
        try {
            OrganizationsDao.deleteById(id);
            cxt.status(HttpStatus.Code.OK.getCode());
        } catch (SQLException e) {
            throw new InternalServerErrorResponse();
        }
    }
}
