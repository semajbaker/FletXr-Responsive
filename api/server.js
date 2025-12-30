// File: server.js
// Main server application with authentication and business endpoints

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';

// Route imports
import authRoutes from './src/routes/auth_routes.js';
import borrowerCategoriesRoutes from './src/routes/borrower_categories_routes.js';
import loanProductsRoutes from './src/routes/loan_products_routes.js';
import borrowersRoutes from './src/routes/borrowers_routes.js';
// Core imports
import { DatabaseConnection } from './src/config/database_connection.js';
import { ResponseHelper } from './src/utils/response_helper.js';

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 8000;
const app = express();

/**
 * Security Middleware Configuration
 */

// Security headers
app.use(helmet({
    crossOriginResourcePolicy: { policy: "cross-origin" }
}));

// CORS configuration
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:8080'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
    message: {
        success: false,
        error: {
            type: 'RATE_LIMIT_EXCEEDED',
            message: 'Too many requests from this IP, please try again later.',
            timestamp: new Date().toISOString()
        }
    },
    standardHeaders: true,
    legacyHeaders: false
});

app.use(limiter);

// Stricter rate limiting for auth endpoints
const authLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10, // Limit each IP to 10 auth requests per windowMs
    message: {
        success: false,
        error: {
            type: 'AUTH_RATE_LIMIT_EXCEEDED',
            message: 'Too many authentication attempts, please try again later.',
            timestamp: new Date().toISOString()
        }
    }
});

/**
 * Application Middleware
 */

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] ${req.method} ${req.path} - IP: ${req.ip}`);
    next();
});

/**
 * Database Connection Initialization
 */
async function initializeDatabase() {
    try {
        console.log('Initializing database connection...');
        const db = DatabaseConnection.getInstance();

        // Test database connection
        const isConnected = await db.testConnection();
        if (!isConnected) {
            throw new Error('Database connection test failed');
        }

        console.log('Database connection established successfully');
        return true;
    } catch (error) {
        console.error('Failed to initialize database:', error.message);
        return false;
    }
}

/**
 * Routes Configuration
 */

// Health check endpoint
app.get("/", (request, response) => {
    ResponseHelper.success(response, "Loan Management System API is running", {
        server: "Express.js",
        environment: process.env.NODE_ENV || 'development',
        timestamp: new Date().toISOString(),
        version: "1.0.0"
    });
});

// Health check endpoint with database status
app.get("/health", async (request, response) => {
    try {
        const db = DatabaseConnection.getInstance();
        const poolStatus = db.getPoolStatus();
        const isDbConnected = await db.testConnection();

        const healthData = {
            status: "healthy",
            database: {
                connected: isDbConnected,
                pool_status: poolStatus
            },
            server: {
                uptime: process.uptime(),
                memory: process.memoryUsage(),
                node_version: process.version
            },
            timestamp: new Date().toISOString()
        };

        ResponseHelper.success(response, "Service is healthy", healthData);
    } catch (error) {
        console.error('Health check failed:', error);
        ResponseHelper.internalError(response, "Health check failed");
    }
});

// API routes
app.use('/api/auth', authLimiter, authRoutes);
app.use('/api/borrower-categories', borrowerCategoriesRoutes);
app.use('/api/loan-products', loanProductsRoutes);
app.use('/api/borrowers', borrowersRoutes);

// API version information
app.get('/api', (req, res) => {
    ResponseHelper.success(res, 'Loan Management System API', {
        version: '1.0.0',
        available_endpoints: {
            authentication: '/api/auth',
            borrower_categories: '/api/borrower-categories',
            loan_products: '/api/loan-products',
            borrowers: '/api/borrowers'
        },
        documentation: 'See individual endpoint documentation'
    });
});

/**
 * Error Handling Middleware
 */

// Handle 404 errors
app.use((req, res) => {
    ResponseHelper.notFound(res, `Route ${req.originalUrl} not found`);
});

// Global error handler
app.use((error, req, res, next) => {
    console.error('Global error handler:', {
        error: error.message,
        stack: error.stack,
        path: req.path,
        method: req.method,
        ip: req.ip,
        timestamp: new Date().toISOString()
    });

    // Handle specific error types
    if (error.name === 'ValidationError') {
        return ResponseHelper.validationError(res, error.message);
    }

    if (error.name === 'JsonWebTokenError') {
        return ResponseHelper.unauthorized(res, 'Invalid token');
    }

    if (error.name === 'TokenExpiredError') {
        return ResponseHelper.unauthorized(res, 'Token expired');
    }

    if (error.code === '23505') { // PostgreSQL unique violation
        return ResponseHelper.conflict(res, 'Resource already exists');
    }

    if (error.code === '23503') { // PostgreSQL foreign key violation
        return ResponseHelper.badRequest(res, 'Invalid reference');
    }

    if (error.code === '23514') { // PostgreSQL check constraint violation
        return ResponseHelper.badRequest(res, 'Invalid data: constraint violation');
    }

    // Default to internal server error
    ResponseHelper.internalError(res, 'An unexpected error occurred');
});

// Global server instance for graceful shutdown
let serverInstance = null;

/**
 * Graceful Shutdown Handling
 */
const gracefulShutdown = async (signal) => {
    console.log(`\nReceived ${signal}. Starting graceful shutdown...`);

    try {
        // Close database connections
        const db = DatabaseConnection.getInstance();
        await db.closePool();
        console.log('Database connections closed');

        // Close server if it exists
        if (serverInstance) {
            serverInstance.close(() => {
                console.log('Server closed successfully');
                process.exit(0);
            });
        } else {
            console.log('No server instance to close');
            process.exit(0);
        }

        // Force close after timeout
        setTimeout(() => {
            console.error('Forced shutdown after timeout');
            process.exit(1);
        }, 10000);

    } catch (error) {
        console.error('Error during graceful shutdown:', error);
        process.exit(1);
    }
};

/**
 * Server Startup
 */
async function startServer() {
    try {
        // Initialize database connection
        const dbInitialized = await initializeDatabase();
        if (!dbInitialized) {
            console.error('Failed to initialize database. Server will not start.');
            process.exit(1);
        }

        // Start server
        serverInstance = app.listen(PORT, () => {
            console.log(`        
                Loan Management System API                                                                                                     
                Server running on: http://localhost:${PORT}                        
                Environment: ${(process.env.NODE_ENV || 'development').padEnd(27)} 
                Available endpoints:
                - Authentication: /api/auth
                - Borrower Categories: /api/borrower-categories  
                - Loan Products: /api/loan-products
                - Borrowers: /api/borrowers
            `);

            // Register shutdown handlers after server starts
            process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
            process.on('SIGINT', () => gracefulShutdown('SIGINT'));
        });

        return serverInstance;
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Start the server
startServer().catch(console.error);

export default app;