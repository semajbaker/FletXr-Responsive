// File: src/constants/auth_constants.js
// Authentication-related constants

export const AuthConstants = {
    // Token durations (in milliseconds)
    ACCESS_TOKEN_DURATION: 15 * 60 * 1000, // 15 minutes
    SESSION_DURATION: 7 * 24 * 60 * 60 * 1000, // 7 days
    
    // Password hashing
    BCRYPT_SALT_ROUNDS: 12,
    
    // User roles (matching database schema)
    USER_ROLES: {
        SUPERUSER: 'superuser',
        ADMIN: 'admin',
        LOAN_OFFICER: 'loan_officer',
        COLLECTION_OFFICER: 'collection_officer',
        AUDITOR: 'auditor',
        CUSTOMER: 'customer'
    },
    
    // Role hierarchy levels (for permission checking)
    ROLE_HIERARCHY: {
        'customer': 1,
        'collection_officer': 2,
        'loan_officer': 3,
        'auditor': 4,
        'admin': 5,
        'superuser': 6
    },
    
    // Default role for new users
    DEFAULT_USER_ROLE: 'customer',
    
    // Session status
    SESSION_STATUS: {
        ACTIVE: true,
        INACTIVE: false
    },
    
    // Permission groups for easier access control
    ADMIN_ROLES: ['admin', 'superuser'],
    STAFF_ROLES: ['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser'],
    LOAN_MANAGEMENT_ROLES: ['loan_officer', 'admin', 'superuser'],
    COLLECTION_ROLES: ['collection_officer', 'admin', 'superuser'],
    REPORTING_ROLES: ['auditor', 'admin', 'superuser'],
    
    // Response messages
    MESSAGES: {
        REGISTRATION_SUCCESS: 'User registered successfully',
        LOGIN_SUCCESS: 'Login successful',
        LOGOUT_SUCCESS: 'Logout successful',
        TOKEN_REFRESH_SUCCESS: 'Token refreshed successfully',
        INVALID_CREDENTIALS: 'Invalid credentials',
        USER_EXISTS: 'User already exists with this email or username',
        ACCOUNT_DEACTIVATED: 'Account is deactivated',
        INVALID_TOKEN: 'Invalid or expired token',
        REGISTRATION_FAILED: 'Failed to register user',
        LOGIN_FAILED: 'Login failed',
        LOGOUT_FAILED: 'Logout failed',
        TOKEN_REFRESH_FAILED: 'Token refresh failed',
        ACCESS_DENIED: 'Access denied - insufficient permissions',
        EMAIL_VERIFICATION_REQUIRED: 'Email verification required'
    },
    
    // Role descriptions for UI display
    ROLE_DESCRIPTIONS: {
        'superuser': 'Full system access with all administrative privileges',
        'admin': 'Administrative access to manage users, products, and system settings',
        'loan_officer': 'Create, approve, and manage loans and borrowers',
        'collection_officer': 'Manage collections, send reminders, and track payments',
        'auditor': 'View-only access to all data for auditing and reporting',
        'customer': 'Basic customer access for loan applications and account management'
    },
    
    // Permission flags
    PERMISSIONS: {
        // User management
        CAN_CREATE_USERS: ['admin', 'superuser'],
        CAN_UPDATE_USERS: ['admin', 'superuser'],
        CAN_DELETE_USERS: ['superuser'],
        CAN_VIEW_ALL_USERS: ['admin', 'superuser'],
        
        // Borrower management
        CAN_CREATE_BORROWERS: ['loan_officer', 'admin', 'superuser'],
        CAN_UPDATE_BORROWERS: ['loan_officer', 'admin', 'superuser'],
        CAN_VIEW_BORROWERS: ['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser'],
        
        // Loan management
        CAN_CREATE_LOANS: ['loan_officer', 'admin', 'superuser'],
        CAN_APPROVE_LOANS: ['loan_officer', 'admin', 'superuser'],
        CAN_DISBURSE_LOANS: ['loan_officer', 'admin', 'superuser'],
        CAN_VIEW_LOANS: ['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser'],
        
        // Product management
        CAN_MANAGE_LOAN_PRODUCTS: ['admin', 'superuser'],
        CAN_MANAGE_BORROWER_CATEGORIES: ['admin', 'superuser'],
        
        // Collections
        CAN_MANAGE_COLLECTIONS: ['collection_officer', 'admin', 'superuser'],
        CAN_SEND_REMINDERS: ['collection_officer', 'admin', 'superuser'],
        
        // Financial management
        CAN_MANAGE_VAULT: ['admin', 'superuser'],
        CAN_VIEW_FINANCIAL_REPORTS: ['auditor', 'admin', 'superuser'],
        
        // System administration
        CAN_MANAGE_SYSTEM_SETTINGS: ['superuser'],
        CAN_VIEW_AUDIT_LOGS: ['auditor', 'admin', 'superuser'],
        CAN_BACKUP_DATA: ['superuser']
    }
};