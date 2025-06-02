package com.auth.backend.security;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Produces;
import jakarta.security.enterprise.identitystore.Pbkdf2PasswordHash;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.Map;

/**
 * A CDI producer for creating a Pbkdf2PasswordHash implementation.
 */
@ApplicationScoped
public class PasswordHashProducer {
    
    /**
     * Produces a Pbkdf2PasswordHash implementation.
     * 
     * @return A Pbkdf2PasswordHash implementation
     */
    @Produces
    @ApplicationScoped
    public Pbkdf2PasswordHash createPasswordHash() {
        // Anonymous inner class implementation to avoid CDI ambiguity
        return new Pbkdf2PasswordHash() {
            private static final int SALT_SIZE = 16;
            
            @Override
            public void initialize(Map<String, String> parameters) {
                // No initialization needed for our simple implementation
            }
            
            @Override
            public String generate(char[] password) {
                try {
                    // Generate a random salt
                    SecureRandom random = new SecureRandom();
                    byte[] salt = new byte[SALT_SIZE];
                    random.nextBytes(salt);
                    
                    // Hash the password with the salt
                    MessageDigest md = MessageDigest.getInstance("SHA-256");
                    md.update(salt);
                    byte[] hashedPassword = md.digest(new String(password).getBytes(StandardCharsets.UTF_8));
                    
                    // Encode the salt and hashed password in Base64
                    String encodedSalt = Base64.getEncoder().encodeToString(salt);
                    String encodedPassword = Base64.getEncoder().encodeToString(hashedPassword);
                    
                    // Return the salt and hashed password separated by a colon
                    return encodedSalt + ":" + encodedPassword;
                } catch (NoSuchAlgorithmException e) {
                    throw new RuntimeException("Error hashing password", e);
                }
            }
            
            @Override
            public boolean verify(char[] password, String hashedPassword) {
                try {
                    // Split the stored hash into salt and password parts
                    String[] parts = hashedPassword.split(":");
                    if (parts.length != 2) {
                        return false;
                    }
                    
                    byte[] salt = Base64.getDecoder().decode(parts[0]);
                    byte[] storedHash = Base64.getDecoder().decode(parts[1]);
                    
                    // Hash the input password with the stored salt
                    MessageDigest md = MessageDigest.getInstance("SHA-256");
                    md.update(salt);
                    byte[] newHash = md.digest(new String(password).getBytes(StandardCharsets.UTF_8));
                    
                    // Compare the new hash with the stored hash
                    if (storedHash.length != newHash.length) {
                        return false;
                    }
                    
                    for (int i = 0; i < storedHash.length; i++) {
                        if (storedHash[i] != newHash[i]) {
                            return false;
                        }
                    }
                    
                    return true;
                } catch (Exception e) {
                    return false;
                }
            }
        };
    }
} 