// File: routes/auth_routes.js
import express from 'express';
import { AuthController } from '../controllers/auth_controller.js';
import { validateUserRegistration, validateUserLogin } from '../middleware/validation_middleware.js';

const router = express.Router();
const authController = new AuthController();

// POST /api/auth/register - Register new user
router.post('/register', validateUserRegistration, (req, res) => {
    authController.registerUser(req, res);
});

// POST /api/auth/login - User login
router.post('/login', validateUserLogin, (req, res) => {
    authController.loginUser(req, res);
});

// POST /api/auth/logout - User logout
router.post('/logout', (req, res) => {
    authController.logoutUser(req, res);
});

// POST /api/auth/refresh - Refresh token
router.post('/refresh', (req, res) => {
    authController.refreshToken(req, res);
});

export default router;