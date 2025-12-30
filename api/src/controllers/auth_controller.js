// File: controllers/auth_controller.js
// Authentication controller for user registration and management

import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { UserService } from '../services/user_service.js';
import { SessionService } from '../services/session_service.js';
import { ResponseHelper } from '../utils/response_helper.js';
import { AuthConstants } from '../constants/auth_constants.js';

export class AuthController {
    constructor() {
        this.userService = new UserService();
        this.sessionService = new SessionService();
    }

    /**
     * Register new user
     * POST /api/auth/register
     */
    registerUser = async (req, res) => {
        try {
            const { username, email, phone_number, password } = req.body;

            // Check if user already exists
            const existingUser = await this.userService.findByEmailOrUsername(email, username);
            if (existingUser) {
                return ResponseHelper.conflict(res, 'User already exists with this email or username');
            }

            // Hash password
            const saltRounds = AuthConstants.BCRYPT_SALT_ROUNDS;
            const passwordHash = await bcrypt.hash(password, saltRounds);

            // Create user data
            const userData = {
                username: username.toLowerCase().trim(),
                email: email.toLowerCase().trim(),
                phone_number: phone_number?.trim() || null,
                password_hash: passwordHash,
                role: 'customer', // Default role as requested
                is_active: true,
                is_email_verified: false
            };

            // Create user
            const newUser = await this.userService.createUser(userData);

            // Generate tokens
            const accessToken = this._generateAccessToken(newUser);
            const refreshToken = this._generateRefreshToken();

            // Create session
            const sessionData = {
                user_id: newUser.id,
                session_token: accessToken,
                refresh_token: refreshToken,
                expires_at: new Date(Date.now() + AuthConstants.SESSION_DURATION),
                ip_address: req.ip,
                user_agent: req.get('User-Agent')
            };

            await this.sessionService.createSession(sessionData);

            // Prepare response (exclude sensitive data)
            const userResponse = {
                id: newUser.id,
                username: newUser.username,
                email: newUser.email,
                phone_number: newUser.phone_number,
                role: newUser.role,
                is_active: newUser.is_active,
                is_email_verified: newUser.is_email_verified,
                created_at: newUser.created_at
            };

            ResponseHelper.created(res, 'User registered successfully', {
                user: userResponse,
                access_token: accessToken,
                refresh_token: refreshToken,
                expires_in: AuthConstants.ACCESS_TOKEN_DURATION / 1000
            });

        } catch (error) {
            console.error('Registration error:', error);
            ResponseHelper.internalError(res, 'Failed to register user');
        }
    };

    /**
     * User login
     * POST /api/auth/login
     */
    loginUser = async (req, res) => {
        try {
            const { email, password } = req.body;

            // Find user by email
            const user = await this.userService.findByEmail(email.toLowerCase().trim());
            if (!user) {
                return ResponseHelper.unauthorized(res, 'Invalid credentials');
            }

            // Check if user is active
            if (!user.is_active) {
                return ResponseHelper.forbidden(res, 'Account is deactivated');
            }

            // Verify password
            const isPasswordValid = await bcrypt.compare(password, user.password_hash);
            if (!isPasswordValid) {
                return ResponseHelper.unauthorized(res, 'Invalid credentials');
            }

            // Generate tokens
            const accessToken = this._generateAccessToken(user);
            const refreshToken = this._generateRefreshToken();

            // Create session
            const sessionData = {
                user_id: user.id,
                session_token: accessToken,
                refresh_token: refreshToken,
                expires_at: new Date(Date.now() + AuthConstants.SESSION_DURATION),
                ip_address: req.ip,
                user_agent: req.get('User-Agent')
            };

            await this.sessionService.createSession(sessionData);

            // Update last login
            await this.userService.updateLastLogin(user.id);

            // Prepare response
            const userResponse = {
                id: user.id,
                username: user.username,
                email: user.email,
                phone_number: user.phone_number,
                role: user.role,
                is_active: user.is_active,
                is_email_verified: user.is_email_verified
            };

            ResponseHelper.success(res, 'Login successful', {
                user: userResponse,
                access_token: accessToken,
                refresh_token: refreshToken,
                expires_in: AuthConstants.ACCESS_TOKEN_DURATION / 1000
            });

        } catch (error) {
            console.error('Login error:', error);
            ResponseHelper.internalError(res, 'Login failed');
        }
    };

    /**
     * User logout
     * POST /api/auth/logout
     */
    logoutUser = async (req, res) => {
        try {
            const authHeader = req.headers.authorization;
            if (!authHeader || !authHeader.startsWith('Bearer ')) {
                return ResponseHelper.unauthorized(res, 'No token provided');
            }

            const token = authHeader.substring(7);
            
            // Deactivate session
            await this.sessionService.deactivateSessionByToken(token);

            ResponseHelper.success(res, 'Logout successful');

        } catch (error) {
            console.error('Logout error:', error);
            ResponseHelper.internalError(res, 'Logout failed');
        }
    };

    /**
     * Refresh access token
     * POST /api/auth/refresh
     */
    refreshToken = async (req, res) => {
        try {
            const { refresh_token } = req.body;

            if (!refresh_token) {
                return ResponseHelper.badRequest(res, 'Refresh token required');
            }

            // Find active session by refresh token
            const session = await this.sessionService.findActiveSessionByRefreshToken(refresh_token);
            if (!session) {
                return ResponseHelper.unauthorized(res, 'Invalid refresh token');
            }

            // Get user data
            const user = await this.userService.findById(session.user_id);
            if (!user || !user.is_active) {
                return ResponseHelper.unauthorized(res, 'User not found or inactive');
            }

            // Generate new tokens
            const newAccessToken = this._generateAccessToken(user);
            const newRefreshToken = this._generateRefreshToken();

            // Update session
            await this.sessionService.updateSession(session.id, {
                session_token: newAccessToken,
                refresh_token: newRefreshToken,
                expires_at: new Date(Date.now() + AuthConstants.SESSION_DURATION)
            });

            ResponseHelper.success(res, 'Token refreshed successfully', {
                access_token: newAccessToken,
                refresh_token: newRefreshToken,
                expires_in: AuthConstants.ACCESS_TOKEN_DURATION / 1000
            });

        } catch (error) {
            console.error('Token refresh error:', error);
            ResponseHelper.internalError(res, 'Token refresh failed');
        }
    };

    /**
     * Generate JWT access token
     * @private
     */
    _generateAccessToken(user) {
        const payload = {
            userId: user.id,
            username: user.username,
            email: user.email,
            role: user.role
        };

        return jwt.sign(payload, process.env.JWT_SECRET, {
            expiresIn: AuthConstants.ACCESS_TOKEN_DURATION / 1000 + 's',
            issuer: 'flutter-auth-app'
        });
    }

    /**
     * Generate refresh token
     * @private
     */
    _generateRefreshToken() {
        return uuidv4() + uuidv4().replace(/-/g, '');
    }
}