package com.auth.backend.controller;

import com.auth.backend.dto.SigninRequest;
import com.auth.backend.dto.SignupRequest;
import com.auth.backend.service.AuthService;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/auth")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AuthController {
    
    @Inject
    private AuthService authService;
    
    @POST
    @Path("/signup")
    public Response registerUser(@Valid SignupRequest signupRequest) {
        return authService.signup(signupRequest);
    }
    
    @POST
    @Path("/signin")
    public Response authenticateUser(@Valid SigninRequest signinRequest) {
        return authService.signin(signinRequest);
    }
} 