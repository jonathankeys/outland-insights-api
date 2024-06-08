package com.outlandinsights.app.modules.platform.endpoints;

import io.javalin.apibuilder.EndpointGroup;
import io.javalin.http.Context;
import lombok.extern.log4j.Log4j2;

import static io.javalin.apibuilder.ApiBuilder.get;

@Log4j2
public class HealthEndpoints implements EndpointGroup {
    public void healthCheck(final Context ctx) {
        log.info("Running health check...");
        ctx.status(200);
        ctx.json("ok");
    }

    public void deepHealthCheck(final Context ctx) throws InterruptedException {
        log.info("Running deep health check...");
        Thread.sleep(1000);
        ctx.status(200);
        ctx.json("ok");
    }

    @Override
    public void addEndpoints() {
        get("shallow", this::healthCheck);
        get("deep", this::deepHealthCheck);
    }
}
