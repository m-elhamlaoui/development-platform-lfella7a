package com.auth.backend.filter;

import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.ext.Provider;
import java.io.IOException;

/**
 * Filter to handle Cross-Origin Resource Sharing (CORS).
 * This is essential to allow the frontend running on a different origin to access the backend API.
 */
@Provider
public class CORSFilter implements ContainerResponseFilter {

    @Override
    public void filter(ContainerRequestContext requestContext, ContainerResponseContext responseContext) throws IOException {
        // Allow requests from the frontend origin
        responseContext.getHeaders().add("Access-Control-Allow-Origin", "http://localhost:3000");
        
        // Allow specific HTTP methods
        responseContext.getHeaders().add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
        
        // Allow specific headers
        responseContext.getHeaders().add("Access-Control-Allow-Headers", "Content-Type, Authorization");
        
        // Allow credentials
        responseContext.getHeaders().add("Access-Control-Allow-Credentials", "true");
        
        // Set max age for preflight requests
        responseContext.getHeaders().add("Access-Control-Max-Age", "3600");
    }
} 