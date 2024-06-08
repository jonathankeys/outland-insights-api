package com.outlandinsights.app.database;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import lombok.Getter;

import java.sql.Connection;
import java.sql.SQLException;

public class Database {
    private static final HikariConfig platformConfig = new HikariConfig();
    @Getter private static final HikariDataSource platformDataSource;

    private static final HikariConfig securityConfig = new HikariConfig();
    @Getter private static final HikariDataSource securityDataSource;

    static {
        platformConfig.setJdbcUrl(String.format("jdbc:postgresql://%s:5432/postgres", System.getenv("PG_HOST")));
        platformConfig.setUsername("postgres");
        platformConfig.setPassword("mysecretpassword");
        platformConfig.setSchema("platform");
        platformConfig.addDataSourceProperty("cachePrepStmts", "true");
        platformConfig.addDataSourceProperty("prepStmtCacheSize", "250");
        platformConfig.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        platformDataSource = new HikariDataSource(platformConfig);

        securityConfig.setJdbcUrl(String.format("jdbc:postgresql://%s:5432/postgres", System.getenv("PG_HOST")));
        securityConfig.setUsername("postgres");
        securityConfig.setPassword("mysecretpassword");
        securityConfig.setSchema("security");
        securityConfig.addDataSourceProperty("cachePrepStmts", "true");
        securityConfig.addDataSourceProperty("prepStmtCacheSize", "250");
        securityConfig.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        securityDataSource = new HikariDataSource(securityConfig);
    }

    private Database() {}

    public static Connection getPlatformConnection() throws SQLException {
        return platformDataSource.getConnection();
    }

    public static Connection getSecurityConnection() throws SQLException {
        return securityDataSource.getConnection();
    }
}
