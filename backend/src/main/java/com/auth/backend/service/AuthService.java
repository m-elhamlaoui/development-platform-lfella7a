package com.auth.backend.service;

import com.auth.backend.dto.AuthResponse;
import com.auth.backend.dto.SigninRequest;
import com.auth.backend.dto.SignupRequest;
import com.auth.backend.entity.User;
import com.auth.backend.repository.UserRepository;
import com.auth.backend.security.JwtUtils;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.security.enterprise.identitystore.Pbkdf2PasswordHash;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.logging.Level;
import java.util.logging.Logger;

@ApplicationScoped
public class AuthService {
    
    private static final Logger logger = Logger.getLogger(AuthService.class.getName());
    
    @Inject
    private UserRepository userRepository;
    
    @Inject
    private JwtUtils jwtUtils;
    
    @Inject
    private Pbkdf2PasswordHash passwordHash;
    
    public Response signup(SignupRequest signupRequest) {
        try {
            // Check if username is already taken
            if (userRepository.existsByUsername(signupRequest.getUsername())) {
                return Response
                        .status(Response.Status.BAD_REQUEST)
                        .entity("Error: Username is already taken!")
                        .build();
            }
            
            // Check if email is already in use
            if (userRepository.existsByEmail(signupRequest.getEmail())) {
                return Response
                        .status(Response.Status.BAD_REQUEST)
                        .entity("Error: Email is already in use!")
                        .build();
            }
            
            // Generate password hash
            String hashedPassword = null;
            if (signupRequest.getPassword() != null) {
                hashedPassword = passwordHash.generate(signupRequest.getPassword().toCharArray());
                logger.log(Level.INFO, "Hashed password generated: {0}", hashedPassword != null);
            } else {
                logger.log(Level.SEVERE, "Password is null");
                return Response
                        .status(Response.Status.BAD_REQUEST)
                        .entity("Error: Password cannot be null!")
                        .build();
            }
            
            // Create new user
            User user = new User(
                    signupRequest.getUsername(),
                    signupRequest.getEmail(),
                    hashedPassword
            );
            
            user.setUpdatedAt(LocalDateTime.now());
            
            userRepository.save(user);
            
            // Return a JSON response instead of plain text
            return Response.ok("{\"message\": \"User registered successfully!\"}").type(MediaType.APPLICATION_JSON).build();
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error during signup", e);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("{\"error\": \"Registration failed due to server error\"}")
                    .type(MediaType.APPLICATION_JSON)
                    .build();
        }
    }
    
    public Response signin(SigninRequest signinRequest) {
        try {
            Optional<User> userOptional = userRepository.findByUsername(signinRequest.getUsername());
            
            if (userOptional.isEmpty() || !passwordHash.verify(
                    signinRequest.getPassword().toCharArray(), 
                    userOptional.get().getPasswordHash())) {
                return Response
                        .status(Response.Status.UNAUTHORIZED)
                        .entity("{\"error\": \"Invalid username or password!\"}")
                        .type(MediaType.APPLICATION_JSON)
                        .build();
            }
            
            User user = userOptional.get();
            
            String jwt = jwtUtils.generateJwtToken(user);
            
            AuthResponse authResponse = new AuthResponse(
                    jwt,
                    user.getId(),
                    user.getUsername(),
                    user.getEmail()
            );
            
            return Response.ok(authResponse).type(MediaType.APPLICATION_JSON).build();
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error during signin", e);
            return Response
                    .status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity("{\"error\": \"" + e.getMessage() + "\"}")
                    .type(MediaType.APPLICATION_JSON)
                    .build();
        }
    }
} 