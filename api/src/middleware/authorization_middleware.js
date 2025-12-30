// File: src/middleware/authorization_middleware.js
// Authorization middleware for role-based access control

import { ResponseHelper } from '../utils/response_helper.js';

/**
 * Role hierarchy definition
 * Higher number = more permissions
 */
const ROLE_HIERARCHY = {
    'customer': 1,
    'collection_officer': 2,
    'loan_officer': 3,
    'auditor': 4,
    'admin': 5,
    'superuser': 6
};

/**
 * Middleware to authorize users based on required roles
 * @param {Array<string>} allowedRoles - Array of role names that are allowed access
 * @returns {Function} Express middleware function
 */
export const authorizeRoles = (allowedRoles = []) => {
    return (req, res, next) => {
        // Check if user is authenticated
        if (!req.user) {
            return ResponseHelper.unauthorized(res, 'Authentication required for authorization');
        }

        const userRole = req.user.role;

        // Check if user's role is in the allowed roles list
        if (allowedRoles.includes(userRole)) {
            return next();
        }

        // Check role hierarchy - higher roles can access lower role permissions
        const userRoleLevel = ROLE_HIERARCHY[userRole] || 0;
        const hasHierarchyAccess = allowedRoles.some(allowedRole => {
            const allowedRoleLevel = ROLE_HIERARCHY[allowedRole] || 0;
            return userRoleLevel >= allowedRoleLevel;
        });

        if (hasHierarchyAccess) {
            return next();
        }

        // Access denied
        return ResponseHelper.forbidden(res,
            `Access denied. Required roles: ${allowedRoles.join(', ')}. Your role: ${userRole}`
        );
    };
};

/**
 * Middleware to authorize superuser only
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeSuperuser = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    if (req.user.role !== 'superuser') {
        return ResponseHelper.forbidden(res, 'Superuser access required');
    }

    next();
};

/**
 * Middleware to authorize admin and superuser roles
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeAdminOrSuperuser = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const allowedRoles = ['admin', 'superuser'];
    if (!allowedRoles.includes(req.user.role)) {
        return ResponseHelper.forbidden(res, 'Admin or Superuser access required');
    }

    next();
};

/**
 * Middleware to authorize loan officers, admins, and superusers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeLoanOfficerOrAbove = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const allowedRoles = ['loan_officer', 'admin', 'superuser'];
    const userRoleLevel = ROLE_HIERARCHY[req.user.role] || 0;
    const minRequiredLevel = ROLE_HIERARCHY['loan_officer'];

    if (userRoleLevel < minRequiredLevel) {
        return ResponseHelper.forbidden(res, 'Loan Officer level access or higher required');
    }

    next();
};

/**
 * Middleware to check if user can access their own resources or has elevated permissions
 * @param {string} userIdParam - Parameter name containing user ID (default: 'userId')
 * @returns {Function} Express middleware function
 */
export const authorizeOwnResourceOrElevated = (userIdParam = 'userId') => {
    return (req, res, next) => {
        if (!req.user) {
            return ResponseHelper.unauthorized(res, 'Authentication required');
        }

        const targetUserId = req.params[userIdParam];
        const currentUserId = req.user.userId;
        const userRole = req.user.role;

        // Allow access if user is accessing their own resource
        if (targetUserId === currentUserId) {
            return next();
        }

        // Allow access if user has elevated permissions
        const elevatedRoles = ['loan_officer', 'admin', 'superuser'];
        if (elevatedRoles.includes(userRole)) {
            return next();
        }

        return ResponseHelper.forbidden(res, 'Access denied. Can only access your own resources');
    };
};


/**
 * Middleware to check specific permissions from user's custom permissions
 * @param {Array<string>} requiredPermissions - Array of permission strings
 * @returns {Function} Express middleware function
 */
export const authorizePermissions = (requiredPermissions = []) => {
    return (req, res, next) => {
        if (!req.user) {
            return ResponseHelper.unauthorized(res, 'Authentication required');
        }

        // If no specific permissions required, just check authentication
        if (requiredPermissions.length === 0) {
            return next();
        }

        // Superusers have all permissions
        if (req.user.role === 'superuser') {
            return next();
        }

        // Check if user has custom permissions (would need to be added to auth flow)
        const userPermissions = req.user.permissions || {};

        const hasRequiredPermissions = requiredPermissions.every(permission => {
            return userPermissions[permission] === true;
        });

        if (!hasRequiredPermissions) {
            return ResponseHelper.forbidden(res,
                `Missing required permissions: ${requiredPermissions.join(', ')}`
            );
        }

        next();
    };
};

/**
 * Middleware to authorize based on borrower ownership
 * Customers can only access their own borrower records
 * @param {string} borrowerIdParam - Parameter name containing borrower ID
 * @returns {Function} Express middleware function
 */
export const authorizeBorrowerAccess = (borrowerIdParam = 'borrowerId') => {
    return async (req, res, next) => {
        if (!req.user) {
            return ResponseHelper.unauthorized(res, 'Authentication required');
        }

        const userRole = req.user.role;

        // Staff roles can access all borrower records
        const staffRoles = ['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser'];
        if (staffRoles.includes(userRole)) {
            return next();
        }

        // For customers, they should only access their own borrower record
        // This would require additional logic to map user to borrower
        // For now, customers are denied access to borrower management endpoints
        if (userRole === 'customer') {
            return ResponseHelper.forbidden(res, 'Customers cannot access borrower management endpoints');
        }

        return ResponseHelper.forbidden(res, 'Access denied');
    };
};
/**
 * Middleware to authorize borrower updates
 * Only loan officers and above can update borrowers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeBorrowerUpdate = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const authorizedRoles = ['loan_officer', 'admin', 'superuser'];
    const userRoleLevel = ROLE_HIERARCHY[req.user.role] || 0;
    const minRequiredLevel = ROLE_HIERARCHY['loan_officer'];

    if (userRoleLevel < minRequiredLevel) {
        return ResponseHelper.forbidden(res, 'Loan Officer level access or higher required to update borrowers');
    }

    next();
};
/**
 * Middleware to authorize KYC status updates
 * Only loan officers and above can update KYC status
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeKycStatusUpdate = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const authorizedRoles = ['loan_officer', 'admin', 'superuser'];
    const userRoleLevel = ROLE_HIERARCHY[req.user.role] || 0;
    const minRequiredLevel = ROLE_HIERARCHY['loan_officer'];

    if (userRoleLevel < minRequiredLevel) {
        return ResponseHelper.forbidden(res, 'Loan Officer level access or higher required to update KYC status');
    }

    next();
};
/**
 * Middleware to authorize borrower blacklisting
 * Only admins and superusers can blacklist borrowers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeBorrowerBlacklist = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const authorizedRoles = ['admin', 'superuser'];
    if (!authorizedRoles.includes(req.user.role)) {
        return ResponseHelper.forbidden(res, 'Admin or Superuser access required to blacklist borrowers');
    }

    next();
};
/**
 * Middleware to authorize borrower deletion
 * Only admins and superusers can delete borrowers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeBorrowerDeletion = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const authorizedRoles = ['admin', 'superuser'];
    if (!authorizedRoles.includes(req.user.role)) {
        return ResponseHelper.forbidden(res, 'Admin or Superuser access required to delete borrowers');
    }

    next();
};

/**
 * Middleware to authorize borrower creation
 * Only loan officers and above can create borrowers
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
export const authorizeBorrowerCreation = (req, res, next) => {
    if (!req.user) {
        return ResponseHelper.unauthorized(res, 'Authentication required');
    }

    const authorizedRoles = ['loan_officer', 'admin', 'superuser'];
    const userRoleLevel = ROLE_HIERARCHY[req.user.role] || 0;
    const minRequiredLevel = ROLE_HIERARCHY['loan_officer'];

    if (userRoleLevel < minRequiredLevel) {
        return ResponseHelper.forbidden(res, 'Loan Officer level access or higher required to create borrowers');
    }

    next();
};


/**
 * Get user's effective permissions based on role
 * @param {string} role - User role
 * @returns {Object} Object containing permission flags
 */
export const getEffectivePermissions = (role) => {
    const basePermissions = {
        can_view_own_data: true,
        can_update_own_profile: true
    };

    const rolePermissions = {
        'customer': {
            ...basePermissions,
            can_apply_for_loan: true,
            can_view_own_loans: true,
            can_make_payments: true
        },
        'collection_officer': {
            ...basePermissions,
            can_view_loans: true,
            can_update_collection_activities: true,
            can_send_reminders: true,
            can_view_borrowers: true
        },
        'loan_officer': {
            ...basePermissions,
            can_view_loans: true,
            can_create_loans: true,
            can_approve_loans: true,
            can_disburse_loans: true,
            can_view_borrowers: true,
            can_create_borrowers: true,
            can_update_borrowers: true
        },
        'auditor': {
            ...basePermissions,
            can_view_all_data: true,
            can_view_audit_logs: true,
            can_generate_reports: true
        },
        'admin': {
            ...basePermissions,
            can_view_all_data: true,
            can_create_users: true,
            can_update_users: true,
            can_manage_loan_products: true,
            can_manage_categories: true,
            can_view_audit_logs: true,
            can_manage_vault: true
        },
        'superuser': {
            ...basePermissions,
            can_do_everything: true,
            can_manage_system_settings: true,
            can_delete_data: true,
            can_manage_users: true
        }
    };

    return rolePermissions[role] || basePermissions;
};