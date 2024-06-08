package com.outlandinsights.app;

import com.outlandinsights.app.modules.platform.endpoints.HealthEndpoints;
import com.outlandinsights.app.modules.platform.endpoints.ExpeditionEndpoints;
import com.outlandinsights.app.modules.platform.endpoints.OrganizationEndpoints;
import com.outlandinsights.app.modules.platform.endpoints.UserEndpoints;
import com.outlandinsights.app.modules.security.endpoints.UserSecurityEndpoints;
import io.javalin.apibuilder.EndpointGroup;
import lombok.extern.log4j.Log4j2;
import org.apache.logging.log4j.ThreadContext;

import java.util.UUID;

import static io.javalin.apibuilder.ApiBuilder.before;
import static io.javalin.apibuilder.ApiBuilder.crud;
import static io.javalin.apibuilder.ApiBuilder.path;

/**
 * Main endpoints file which contains a mapping to all the top level endpoints.
 * Anytime a new endpoint is added, it will need to be added through here
 */
@Log4j2
public class ApplicationRoutesRoot implements EndpointGroup {
    @Override
    public void addEndpoints() {
        // Create a request_id per each request
        before(ctx -> {
            ThreadContext.clearAll();
            ThreadContext.put("request_id", UUID.randomUUID().toString());
            if (ctx.sessionAttribute("session_id") != null) {
                ThreadContext.put("session_id", ctx.sessionAttribute("session_id"));
            }
        });
        path("/health", new HealthEndpoints());

        path("/security", new UserSecurityEndpoints());
        path("/user", new UserEndpoints());

        // Crud endpoints
        crud("/organizations/{id}", new OrganizationEndpoints());
        crud("/expeditions/{id}", new ExpeditionEndpoints());
    }
}
