// File: src/middleware/business_validation_middleware.js
// Validation middleware for business entities (borrower categories and loan products)

import { body, param, query, validationResult } from 'express-validator';
import { ResponseHelper } from '../utils/response_helper.js';

// Handle validation errors
const handleValidationErrors = (req, res, next) => {
    const errors = validationResult(req);
    
    if (!errors.isEmpty()) {
        const errorMessages = errors.array().map(error => ({
            field: error.path,
            message: error.msg,
            value: error.value
        }));
        
        return ResponseHelper.validationError(res, 'Validation failed', errorMessages);
    }
    
    next();
};

// UUID validation for parameters
export const validateUUIDParam = (paramName = 'id') => [
    param(paramName)
        .isUUID(4)
        .withMessage(`${paramName} must be a valid UUID`),
    handleValidationErrors
];

// Pagination validation
export const validatePagination = [
    query('page')
        .optional({ checkFalsy: true })
        .isInt({ min: 1 })
        .withMessage('Page must be a positive integer')
        .toInt(),
    
    query('limit')
        .optional({ checkFalsy: true })
        .isInt({ min: 1, max: 100 })
        .withMessage('Limit must be between 1 and 100')
        .toInt(),
    
    query('active_only')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('active_only must be a boolean')
        .toBoolean(),
    
    handleValidationErrors
];

// ============================================
// BORROWER CATEGORIES VALIDATION
// ============================================

// Create borrower category validation
export const validateCreateBorrowerCategory = [
    body('name')
        .trim()
        .isLength({ min: 2, max: 100 })
        .withMessage('Category name must be between 2 and 100 characters')
        .matches(/^[a-zA-Z0-9\s\-_&]+$/)
        .withMessage('Category name can only contain letters, numbers, spaces, hyphens, underscores, and ampersands'),
    
    body('description')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 500 })
        .withMessage('Description must be less than 500 characters'),
    
    body('is_active')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('is_active must be a boolean'),
    
    handleValidationErrors
];

// Update borrower category validation
export const validateUpdateBorrowerCategory = [
    body('name')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 100 })
        .withMessage('Category name must be between 2 and 100 characters')
        .matches(/^[a-zA-Z0-9\s\-_&]+$/)
        .withMessage('Category name can only contain letters, numbers, spaces, hyphens, underscores, and ampersands'),
    
    body('description')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 500 })
        .withMessage('Description must be less than 500 characters'),
    
    body('is_active')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('is_active must be a boolean'),
    
    // Ensure at least one field is provided
    body()
        .custom((value, { req }) => {
            const allowedFields = ['name', 'description', 'is_active'];
            const providedFields = Object.keys(req.body).filter(key => allowedFields.includes(key));
            
            if (providedFields.length === 0) {
                throw new Error('At least one field must be provided for update');
            }
            return true;
        }),
    
    handleValidationErrors
];

// ============================================
// LOAN PRODUCTS VALIDATION
// ============================================

// Create loan product validation
export const validateCreateLoanProduct = [
    body('name')
        .trim()
        .isLength({ min: 3, max: 255 })
        .withMessage('Product name must be between 3 and 255 characters')
        .matches(/^[a-zA-Z0-9\s\-_&()]+$/)
        .withMessage('Product name can only contain letters, numbers, spaces, hyphens, underscores, ampersands, and parentheses'),
    
    body('description')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 1000 })
        .withMessage('Description must be less than 1000 characters'),
    
    body('interest_type')
        .optional({ checkFalsy: true })
        .isIn(['flat_monthly', 'reducing_balance'])
        .withMessage('Interest type must be either flat_monthly or reducing_balance'),
    
    body('interest_rate')
        .isFloat({ min: 0.0001, max: 5.0000 })
        .withMessage('Interest rate must be between 0.0001 and 5.0000 (0.01% to 500%)')
        .custom((value) => {
            // Ensure maximum 4 decimal places
            const decimalPlaces = (value.toString().split('.')[1] || '').length;
            if (decimalPlaces > 4) {
                throw new Error('Interest rate can have maximum 4 decimal places');
            }
            return true;
        }),
    
    body('max_amount')
        .isFloat({ min: 1.00, max: 999999999.99 })
        .withMessage('Maximum amount must be between 1.00 and 999,999,999.99')
        .custom((value) => {
            // Ensure maximum 2 decimal places for currency
            const decimalPlaces = (value.toString().split('.')[1] || '').length;
            if (decimalPlaces > 2) {
                throw new Error('Maximum amount can have maximum 2 decimal places');
            }
            return true;
        }),
    
    body('default_term_days')
        .isInt({ min: 1, max: 3650 })
        .withMessage('Default term days must be between 1 and 3650 days (10 years)'),
    
    body('grace_days')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 30 })
        .withMessage('Grace days must be between 0 and 30'),
    
    body('penalty_type')
        .optional({ checkFalsy: true })
        .isIn(['fixed', 'percentage'])
        .withMessage('Penalty type must be either fixed or percentage'),
    
    body('penalty_value')
        .isFloat({ min: 0.01, max: 999999.99 })
        .withMessage('Penalty value must be between 0.01 and 999,999.99')
        .custom((value, { req }) => {
            const penaltyType = req.body.penalty_type || 'fixed';
            
            if (penaltyType === 'percentage' && value > 1.0000) {
                throw new Error('Percentage penalty value must be between 0.01 and 1.0000 (1% to 100%)');
            }
            
            // Ensure maximum 2 decimal places for fixed, 4 for percentage
            const maxDecimals = penaltyType === 'percentage' ? 4 : 2;
            const decimalPlaces = (value.toString().split('.')[1] || '').length;
            if (decimalPlaces > maxDecimals) {
                throw new Error(`Penalty value can have maximum ${maxDecimals} decimal places for ${penaltyType} type`);
            }
            
            return true;
        }),
    
    body('min_credit_score')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 100 })
        .withMessage('Minimum credit score must be between 0 and 100'),
    
    body('is_active')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('is_active must be a boolean'),
    
    handleValidationErrors
];
// ============================================
// BORROWERS VALIDATION
// ============================================

// Create borrower validation
export const validateCreateBorrower = [
    body('full_name')
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Full name must be between 2 and 255 characters')
        .matches(/^[a-zA-Z\s\-'\.]+$/)
        .withMessage('Full name can only contain letters, spaces, hyphens, apostrophes, and periods'),
    
    body('phone_primary')
        .trim()
        .isMobilePhone('any', { strictMode: false })
        .withMessage('Primary phone number must be a valid phone number')
        .isLength({ min: 8, max: 20 })
        .withMessage('Primary phone number must be between 8 and 20 characters'),
    
    body('phone_whatsapp')
        .optional({ checkFalsy: true })
        .trim()
        .isMobilePhone('any', { strictMode: false })
        .withMessage('WhatsApp phone number must be a valid phone number')
        .isLength({ min: 8, max: 20 })
        .withMessage('WhatsApp phone number must be between 8 and 20 characters'),
    
    body('email')
        .optional({ checkFalsy: true })
        .trim()
        .isEmail()
        .withMessage('Email must be a valid email address')
        .normalizeEmail(),
    
    body('id_number')
        .trim()
        .isLength({ min: 5, max: 50 })
        .withMessage('ID number must be between 5 and 50 characters')
        .matches(/^[a-zA-Z0-9\-\/]+$/)
        .withMessage('ID number can only contain letters, numbers, hyphens, and forward slashes'),
    
    body('date_of_birth')
        .isISO8601({ strict: true })
        .withMessage('Date of birth must be a valid date in YYYY-MM-DD format')
        .custom((value) => {
            const birthDate = new Date(value);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            
            if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                age--;
            }
            
            if (age < 18) {
                throw new Error('Borrower must be at least 18 years old');
            }
            
            if (age > 100) {
                throw new Error('Invalid date of birth - age cannot exceed 100 years');
            }
            
            if (birthDate > today) {
                throw new Error('Date of birth cannot be in the future');
            }
            
            return true;
        }),
    
    body('address')
        .trim()
        .isLength({ min: 10, max: 500 })
        .withMessage('Address must be between 10 and 500 characters'),
    
    body('category_id')
        .isUUID(4)
        .withMessage('Category ID must be a valid UUID'),
    
    body('employer_or_school')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Employer or school must be between 2 and 255 characters'),
    
    body('referrer')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Referrer must be between 2 and 255 characters'),
    
    body('credit_score')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 100 })
        .withMessage('Credit score must be between 0 and 100'),
    
    body('risk_tier')
        .optional({ checkFalsy: true })
        .isIn(['low', 'standard', 'high'])
        .withMessage('Risk tier must be either low, standard, or high'),
    
    body('notes')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 1000 })
        .withMessage('Notes must be less than 1000 characters'),
    
    handleValidationErrors
];

// Update borrower validation
export const validateUpdateBorrower = [
    body('full_name')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Full name must be between 2 and 255 characters')
        .matches(/^[a-zA-Z\s\-'\.]+$/)
        .withMessage('Full name can only contain letters, spaces, hyphens, apostrophes, and periods'),
    
    body('phone_primary')
        .optional({ checkFalsy: true })
        .trim()
        .isMobilePhone('any', { strictMode: false })
        .withMessage('Primary phone number must be a valid phone number')
        .isLength({ min: 8, max: 20 })
        .withMessage('Primary phone number must be between 8 and 20 characters'),
    
    body('phone_whatsapp')
        .optional({ checkFalsy: true })
        .trim()
        .isMobilePhone('any', { strictMode: false })
        .withMessage('WhatsApp phone number must be a valid phone number')
        .isLength({ min: 8, max: 20 })
        .withMessage('WhatsApp phone number must be between 8 and 20 characters'),
    
    body('email')
        .optional({ checkFalsy: true })
        .trim()
        .isEmail()
        .withMessage('Email must be a valid email address')
        .normalizeEmail(),
    
    body('id_number')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 5, max: 50 })
        .withMessage('ID number must be between 5 and 50 characters')
        .matches(/^[a-zA-Z0-9\-\/]+$/)
        .withMessage('ID number can only contain letters, numbers, hyphens, and forward slashes'),
    
    body('date_of_birth')
        .optional({ checkFalsy: true })
        .isISO8601({ strict: true })
        .withMessage('Date of birth must be a valid date in YYYY-MM-DD format')
        .custom((value) => {
            if (value !== undefined) {
                const birthDate = new Date(value);
                const today = new Date();
                const age = today.getFullYear() - birthDate.getFullYear();
                const monthDiff = today.getMonth() - birthDate.getMonth();
                
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
                    age--;
                }
                
                if (age < 18) {
                    throw new Error('Borrower must be at least 18 years old');
                }
                
                if (age > 100) {
                    throw new Error('Invalid date of birth - age cannot exceed 100 years');
                }
                
                if (birthDate > today) {
                    throw new Error('Date of birth cannot be in the future');
                }
            }
            return true;
        }),
    
    body('address')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 10, max: 500 })
        .withMessage('Address must be between 10 and 500 characters'),
    
    body('category_id')
        .optional({ checkFalsy: true })
        .isUUID(4)
        .withMessage('Category ID must be a valid UUID'),
    
    body('employer_or_school')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Employer or school must be between 2 and 255 characters'),
    
    body('referrer')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 255 })
        .withMessage('Referrer must be between 2 and 255 characters'),
    
    body('status')
        .optional({ checkFalsy: true })
        .isIn(['active', 'inactive', 'blacklisted'])
        .withMessage('Status must be either active, inactive, or blacklisted'),
    
    body('credit_score')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 100 })
        .withMessage('Credit score must be between 0 and 100'),
    
    body('risk_tier')
        .optional({ checkFalsy: true })
        .isIn(['low', 'standard', 'high'])
        .withMessage('Risk tier must be either low, standard, or high'),
    
    body('kyc_status')
        .optional({ checkFalsy: true })
        .isIn(['incomplete', 'pending', 'approved', 'rejected'])
        .withMessage('KYC status must be either incomplete, pending, approved, or rejected'),
    
    body('notes')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 1000 })
        .withMessage('Notes must be less than 1000 characters'),
    
    // Ensure at least one field is provided
    body()
        .custom((value, { req }) => {
            const allowedFields = [
                'full_name', 'phone_primary', 'phone_whatsapp', 'email', 'id_number',
                'date_of_birth', 'address', 'category_id', 'employer_or_school',
                'referrer', 'status', 'credit_score', 'risk_tier', 'kyc_status', 'notes'
            ];
            const providedFields = Object.keys(req.body).filter(key => allowedFields.includes(key));
            
            if (providedFields.length === 0) {
                throw new Error('At least one field must be provided for update');
            }
            return true;
        }),
    
    handleValidationErrors
];

// Update KYC status validation
export const validateUpdateKycStatus = [
    body('kyc_status')
        .isIn(['incomplete', 'pending', 'approved', 'rejected'])
        .withMessage('KYC status must be either incomplete, pending, approved, or rejected'),
    
    body('notes')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 1000 })
        .withMessage('Notes must be less than 1000 characters'),
    
    handleValidationErrors
];

// Blacklist borrower validation
export const validateBlacklistBorrower = [
    body('reason')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 5, max: 500 })
        .withMessage('Blacklist reason must be between 5 and 500 characters if provided'),
    
    handleValidationErrors
];

// Borrower search validation
export const validateBorrowerSearch = [
    query('q')
        .trim()
        .isLength({ min: 2, max: 100 })
        .withMessage('Search query must be between 2 and 100 characters'),
    
    query('limit')
        .optional({ checkFalsy: true })
        .isInt({ min: 1, max: 50 })
        .withMessage('Limit must be between 1 and 50')
        .toInt(),
    
    handleValidationErrors
];

// Category ID parameter validation for borrowers
export const validateCategoryIdParam = [
    param('categoryId')
        .isUUID(4)
        .withMessage('Category ID must be a valid UUID'),
    handleValidationErrors
];

// Borrower pagination with additional filters validation
export const validateBorrowerPagination = [
    query('page')
        .optional({ checkFalsy: true })
        .isInt({ min: 1 })
        .withMessage('Page must be a positive integer')
        .toInt(),
    
    query('limit')
        .optional({ checkFalsy: true })
        .isInt({ min: 1, max: 100 })
        .withMessage('Limit must be between 1 and 100')
        .toInt(),
    
    query('status')
        .optional({ checkFalsy: true })
        .isIn(['active', 'inactive', 'blacklisted'])
        .withMessage('Status must be either active, inactive, or blacklisted'),
    
    query('kyc_status')
        .optional({ checkFalsy: true })
        .isIn(['incomplete', 'pending', 'approved', 'rejected'])
        .withMessage('KYC status must be either incomplete, pending, approved, or rejected'),
    
    query('category_id')
        .optional({ checkFalsy: true })
        .isUUID(4)
        .withMessage('Category ID must be a valid UUID'),
    
    query('search')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 2, max: 100 })
        .withMessage('Search query must be between 2 and 100 characters'),
    
    query('active_only')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('active_only must be a boolean')
        .toBoolean(),
    
    handleValidationErrors
];

// Update loan product validation
export const validateUpdateLoanProduct = [
    body('name')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ min: 3, max: 255 })
        .withMessage('Product name must be between 3 and 255 characters')
        .matches(/^[a-zA-Z0-9\s\-_&()]+$/)
        .withMessage('Product name can only contain letters, numbers, spaces, hyphens, underscores, ampersands, and parentheses'),
    
    body('description')
        .optional({ checkFalsy: true })
        .trim()
        .isLength({ max: 1000 })
        .withMessage('Description must be less than 1000 characters'),
    
    body('interest_type')
        .optional({ checkFalsy: true })
        .isIn(['flat_monthly', 'reducing_balance'])
        .withMessage('Interest type must be either flat_monthly or reducing_balance'),
    
    body('interest_rate')
        .optional({ checkFalsy: true })
        .isFloat({ min: 0.0001, max: 5.0000 })
        .withMessage('Interest rate must be between 0.0001 and 5.0000 (0.01% to 500%)')
        .custom((value) => {
            if (value !== undefined) {
                const decimalPlaces = (value.toString().split('.')[1] || '').length;
                if (decimalPlaces > 4) {
                    throw new Error('Interest rate can have maximum 4 decimal places');
                }
            }
            return true;
        }),
    
    body('max_amount')
        .optional({ checkFalsy: true })
        .isFloat({ min: 1.00, max: 999999999.99 })
        .withMessage('Maximum amount must be between 1.00 and 999,999,999.99')
        .custom((value) => {
            if (value !== undefined) {
                const decimalPlaces = (value.toString().split('.')[1] || '').length;
                if (decimalPlaces > 2) {
                    throw new Error('Maximum amount can have maximum 2 decimal places');
                }
            }
            return true;
        }),
    
    body('default_term_days')
        .optional({ checkFalsy: true })
        .isInt({ min: 1, max: 3650 })
        .withMessage('Default term days must be between 1 and 3650 days (10 years)'),
    
    body('grace_days')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 30 })
        .withMessage('Grace days must be between 0 and 30'),
    
    body('penalty_type')
        .optional({ checkFalsy: true })
        .isIn(['fixed', 'percentage'])
        .withMessage('Penalty type must be either fixed or percentage'),
    
    body('penalty_value')
        .optional({ checkFalsy: true })
        .isFloat({ min: 0.01, max: 999999.99 })
        .withMessage('Penalty value must be between 0.01 and 999,999.99')
        .custom((value, { req }) => {
            if (value !== undefined) {
                const penaltyType = req.body.penalty_type || 'fixed';
                
                if (penaltyType === 'percentage' && value > 1.0000) {
                    throw new Error('Percentage penalty value must be between 0.01 and 1.0000 (1% to 100%)');
                }
                
                const maxDecimals = penaltyType === 'percentage' ? 4 : 2;
                const decimalPlaces = (value.toString().split('.')[1] || '').length;
                if (decimalPlaces > maxDecimals) {
                    throw new Error(`Penalty value can have maximum ${maxDecimals} decimal places for ${penaltyType} type`);
                }
            }
            return true;
        }),
    
    body('min_credit_score')
        .optional({ checkFalsy: true })
        .isInt({ min: 0, max: 100 })
        .withMessage('Minimum credit score must be between 0 and 100'),
    
    body('is_active')
        .optional({ checkFalsy: true })
        .isBoolean()
        .withMessage('is_active must be a boolean'),
    
    // Ensure at least one field is provided
    body()
        .custom((value, { req }) => {
            const allowedFields = [
                'name', 'description', 'interest_type', 'interest_rate', 
                'max_amount', 'default_term_days', 'grace_days', 'penalty_type', 
                'penalty_value', 'min_credit_score', 'is_active'
            ];
            const providedFields = Object.keys(req.body).filter(key => allowedFields.includes(key));
            
            if (providedFields.length === 0) {
                throw new Error('At least one field must be provided for update');
            }
            return true;
        }),
    
    handleValidationErrors
];

// Loan calculation validation
export const validateLoanCalculation = [
    body('principal_amount')
        .isFloat({ min: 1.00, max: 999999999.99 })
        .withMessage('Principal amount must be between 1.00 and 999,999,999.99')
        .custom((value) => {
            const decimalPlaces = (value.toString().split('.')[1] || '').length;
            if (decimalPlaces > 2) {
                throw new Error('Principal amount can have maximum 2 decimal places');
            }
            return true;
        }),
    
    body('term_days')
        .optional({ checkFalsy: true })
        .isInt({ min: 1, max: 3650 })
        .withMessage('Term days must be between 1 and 3650 days (10 years)'),
    
    handleValidationErrors
];

// Interest type parameter validation
export const validateInterestTypeParam = [
    param('interestType')
        .isIn(['flat_monthly', 'reducing_balance'])
        .withMessage('Interest type must be either flat_monthly or reducing_balance'),
    handleValidationErrors
];

// Import validation for loan products routes
export const validateImportInterestType = [
    param('interestType')
        .isIn(['flat_monthly', 'reducing_balance'])
        .withMessage('Interest type must be either flat_monthly or reducing_balance'),
    handleValidationErrors
];