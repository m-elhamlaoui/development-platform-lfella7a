package com.auth.backend.security;

import com.auth.backend.entity.User;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.Keys;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.annotation.PostConstruct;
import java.security.Key;
import java.util.Base64;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

@ApplicationScoped
public class JwtUtils {
    
    private static final Logger logger = Logger.getLogger(JwtUtils.class.getName());
    
    // In a real application, this key would be stored securely in a properties file or environment variable
    private static final String JWT_SECRET = "bXlTdXBlclNlY3VyZUFuZFZlcnlMb25nU2VjcmV0S2V5Rm9yU2lnbmluZ0pXVFRva2Vuc0luSmFrYXJ0YUVFQXV0aEJhY2tlbmRBcHBsaWNhdGlvbg==";
    private static final int JWT_EXPIRATION_MS = 86400000; // 24 hours
    
    private Key signingKey;
    
    @PostConstruct
    public void init() {
        byte[] keyBytes = Base64.getDecoder().decode(JWT_SECRET);
        signingKey = Keys.hmacShaKeyFor(keyBytes);
    }
    
    private Key getSigningKey() {
        return signingKey;
    }
    
    public String generateJwtToken(User user) {
        return Jwts.builder()
                .setSubject(user.getUsername())
                .claim("id", user.getId())
                .claim("email", user.getEmail())
                .claim("username", user.getUsername())
                .setIssuedAt(new Date())
                .setExpiration(new Date((new Date()).getTime() + JWT_EXPIRATION_MS))
                .signWith(getSigningKey(), SignatureAlgorithm.HS512)
                .compact();
    }
    
    public String getUserNameFromJwtToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }
    
    public boolean validateJwtToken(String authToken) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(authToken);
            return true;
        } catch (MalformedJwtException e) {
            logger.log(Level.SEVERE, "Invalid JWT token: {0}", e.getMessage());
        } catch (ExpiredJwtException e) {
            logger.log(Level.SEVERE, "JWT token is expired: {0}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            logger.log(Level.SEVERE, "JWT token is unsupported: {0}", e.getMessage());
        } catch (IllegalArgumentException e) {
            logger.log(Level.SEVERE, "JWT claims string is empty: {0}", e.getMessage());
        }
        
        return false;
    }
} 