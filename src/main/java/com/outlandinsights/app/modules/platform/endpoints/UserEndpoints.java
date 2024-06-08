package com.outlandinsights.app.modules.platform.endpoints;

import com.outlandinsights.app.modules.platform.daos.UsersDao;
import com.outlandinsights.app.modules.platform.models.User;
import io.javalin.apibuilder.EndpointGroup;
import io.javalin.http.Context;
import io.javalin.http.InternalServerErrorResponse;
import io.javalin.http.UnauthorizedResponse;
import lombok.extern.log4j.Log4j2;
import org.eclipse.jetty.http.HttpStatus;

import java.sql.SQLException;

import static io.javalin.apibuilder.ApiBuilder.get;

@Log4j2
public class UserEndpoints implements EndpointGroup {

    public void getUser(final Context ctx) {
        final String userId = (String) ctx.req().getSession().getAttribute("user_id");
        try {
            final User user = UsersDao.getUserById(userId);
            if (user != null) {
                ctx.json(user);
                ctx.status(HttpStatus.Code.OK.getCode());
                return;
            }
            throw new UnauthorizedResponse();
        } catch (SQLException e) {
            throw new InternalServerErrorResponse();
        }
    }

    @Override
    public void addEndpoints() {
        get(this::getUser);
    }
}
