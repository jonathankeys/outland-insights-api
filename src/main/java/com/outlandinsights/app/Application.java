package com.outlandinsights.app;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.outlandinsights.app.database.Database;
import io.javalin.Javalin;
import io.javalin.http.InternalServerErrorResponse;
import io.javalin.json.JavalinJackson;
import lombok.extern.log4j.Log4j2;
import org.eclipse.jetty.server.session.DatabaseAdaptor;
import org.eclipse.jetty.server.session.DefaultSessionCache;
import org.eclipse.jetty.server.session.JDBCSessionDataStoreFactory;
import org.eclipse.jetty.server.session.SessionCache;
import org.eclipse.jetty.server.session.SessionHandler;

import java.util.TimeZone;

/**
 * Configures the server to start running, handles add any required
 * configurations or settings.
 */
@Log4j2
public class Application {
    private static final int PORT = 7070;

    /**
     * Application entry point used to configure and start the Javalin application
     * built on top of Jetty web server.
     */
    public static void main(String... args) {
        log.info("Starting up application...");

        // Set application to run in UTC
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"));

        final Javalin app = Javalin.create(config -> {
            // Jetty Configs
            config.jetty.modifyServletContextHandler(handler -> handler.setSessionHandler(createSessionHandler()));

            // Add all endpoints
            config.router.apiBuilder(new ApplicationRoutesRoot());

            // Javalin Configs
            config.requestLogger.http((ctx, ms) -> {
                log.info("HTTP Request: [{}] {}, request ms: {}", ctx.statusCode(), ctx.path(), ms);
            });
            config.showJavalinBanner = false;

            // Object to JSON Mapper
            config.jsonMapper(new JavalinJackson().updateMapper(mapper -> {
                mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
            }));
        });

        app.exception(Exception.class, (e, ctx) -> {
            log.error("Unhandled exception in route={}", ctx.path(), e);
            throw new InternalServerErrorResponse();
        });

        app.start(PORT);
    }

    /**
     * Persist sessions within postgres using Jetty framework
     * 
     * @return A Jetty SessionHandler used to store sessions
     */
    private static SessionHandler createSessionHandler() {
        final SessionHandler handler = new SessionHandler();
        final SessionCache cache = new DefaultSessionCache(handler);
        cache.setSessionDataStore(createSessionDataStore().getSessionDataStore(handler));
        handler.setSessionCache(cache);
        handler.setHttpOnly(true);
        return handler;
    }

    /**
     * Create a Jetty Session Store which uses a database under the hood.
     * 
     * @return JDBCSessionDataStoreFactory which can instantiate a session data
     *         store for a handler
     */
    private static JDBCSessionDataStoreFactory createSessionDataStore() {
        final DatabaseAdaptor adaptor = new DatabaseAdaptor();
        adaptor.setDatasource(Database.getPlatformDataSource());

        final JDBCSessionDataStoreFactory dataStore = new JDBCSessionDataStoreFactory();
        dataStore.setDatabaseAdaptor(adaptor);
        return dataStore;
    }
}
