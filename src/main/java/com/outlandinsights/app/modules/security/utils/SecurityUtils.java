package com.outlandinsights.app.modules.security.utils;

import com.outlandinsights.app.modules.security.daos.UserSecurityDao;
import com.outlandinsights.app.modules.security.models.UserSecurity;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.KeySpec;
import java.sql.SQLException;
import java.util.Base64;
import java.util.Objects;

public class SecurityUtils {
    // Private constructor, class should not be instantiated
    private SecurityUtils() {}

    public static String hashPassword(final String clearTextPassword) {
        final SecureRandom random = new SecureRandom();
        final byte[] salt = new byte[16];
        random.nextBytes(salt);

        return hashPassword(clearTextPassword, salt);
    }

    public static boolean verifyPassword(final String userId, final String password) throws SQLException {
        final UserSecurity userSecurity = UserSecurityDao.getUserSecurityById(userId);
        if (userSecurity != null) {
            return SecurityUtils.passwordAreEqual(password, userSecurity.getPassword());
        }
        return false;
    }

    private static boolean passwordAreEqual(final String clearTextPassword, final String storedPassword) {
        final byte[] salt = Base64.getDecoder().decode(storedPassword.split(":")[0]);
        final String hashedPassword = hashPassword(clearTextPassword, salt);
        return Objects.equals(hashedPassword, storedPassword);
    }

    /**
     * Ensure this method is always private to this class, we should not be allowing methods outside of this class to
     * pass in a salt on their own as we cannot trust it will be in the expected format.
     * @param clearTextPassword the password to hash
     * @param salt a custom salt to enhance the security of the hashed password
     * @return the hashed password
     */
    private static String hashPassword(final String clearTextPassword, final byte[] salt) {
        final KeySpec spec = new PBEKeySpec(clearTextPassword.toCharArray(), salt, 65536, 128);
        try {
            final SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
            final String encodedSalt = Base64.getEncoder().encodeToString(salt);
            final String encodedPassword = Base64.getEncoder().encodeToString(factory.generateSecret(spec).getEncoded());
            return String.format("%s:%s", encodedSalt, encodedPassword);
        } catch (InvalidKeySpecException | NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}
