// File: src/middleware/auth_middleware.js
// Authentication middleware for JWT token verification

import jwt from 'jsonwebtoken';
import { SessionService } from '../services/session_service.js';
import { ResponseHelper } from '../utils/response_helper.js';

const sessionService = new SessionService();

/**
 * Middleware to authenticate JWT tokens and validate sessions
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authenticateToken = async (req, res, next) => {
    try {
        // Extract token from Authorization header
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return ResponseHelper.unauthorized(res, 'Access token required');
        }

        const token = authHeader.substring(7); // Remove 'Bearer ' prefix

        // Verify JWT token
        let decodedToken;
        try {
            decodedToken = jwt.verify(token, process.env.JWT_SECRET);
        } catch (jwtError) {
            if (jwtError.name === 'TokenExpiredError') {
                return ResponseHelper.unauthorized(res, 'Access token expired');
            }
            if (jwtError.name === 'JsonWebTokenError') {
                return ResponseHelper.unauthorized(res, 'Invalid access token');
            }
            throw jwtError;
        }

        // Validate session in database
        const sessionData = await sessionService.validateSessionAndGetUser(token);
        if (!sessionData) {
            return ResponseHelper.unauthorized(res, 'Invalid or expired session');
        }

        // Check if user is still active
        if (!sessionData.user_active) {
            return ResponseHelper.forbidden(res, 'User account is deactivated');
        }

        // Attach user information to request object
        req.user = {
            userId: sessionData.user_id,
            username: sessionData.username,
            email: sessionData.email,
            role: sessionData.role,
            isEmailVerified: sessionData.is_email_verified,
            sessionId: sessionData.session_id
        };

        // Attach token for potential logout operations
        req.token = token;

        next();

    } catch (error) {
        console.error('Authentication middleware error:', error);
        ResponseHelper.internalError(res, 'Authentication failed');
    }
};

/**
 * Optional authentication middleware - allows both authenticated and unauthenticated requests
 * Sets req.user if token is valid, but doesn't block request if invalid/missing
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const optionalAuthentication = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        
        // If no auth header, continue without authentication
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return next();
        }

        const token = authHeader.substring(7);

        // Try to verify token and validate session
        try {
            const decodedToken = jwt.verify(token, process.env.JWT_SECRET);
            const sessionData = await sessionService.validateSessionAndGetUser(token);
            
            if (sessionData && sessionData.user_active) {
                req.user = {
                    userId: sessionData.user_id,
                    username: sessionData.username,
                    email: sessionData.email,
                    role: sessionData.role,
                    isEmailVerified: sessionData.is_email_verified,
                    sessionId: sessionData.session_id
                };
                req.token = token;
            }
        } catch (error) {
            // Silently ignore authentication errors in optional mode
            console.log('Optional authentication failed:', error.message);
        }

        next();

    } catch (error) {
        console.error('Optional authentication middleware error:', error);
        // Don't block the request, just log the error
        next();
    }
};

/**
 * Middleware to check if user's email is verified
 * Should be used after authenticateToken middleware
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const requireEmailVerification = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    if (!req.user.isEmailVerified) {
        return ResponseHelper.forbidden(res, 'Email verification required');
    }

    next();
};

/**
 * Middleware to extract user info from valid JWT without database validation
 * Useful for endpoints that need user info but don't require active session validation
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const extractUserFromToken = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return ResponseHelper.unauthorized(res, 'Access token required');
        }

        const token = authHeader.substring(7);

        // Verify JWT token only (no database validation)
        const decodedToken = jwt.verify(token, process.env.JWT_SECRET);

        req.user = {
            userId: decodedToken.userId,
            username: decodedToken.username,
            email: decodedToken.email,
            role: decodedToken.role
        };
        req.token = token;

        next();

    } catch (error) {
        if (error.name === 'TokenExpiredError') {
            return ResponseHelper.unauthorized(res, 'Access token expired');
        }
        if (error.name === 'JsonWebTokenError') {
            return ResponseHelper.unauthorized(res, 'Invalid access token');
        }
        console.error('Extract user from token error:', error);
        ResponseHelper.internalError(res, 'Token validation failed');
    }
};