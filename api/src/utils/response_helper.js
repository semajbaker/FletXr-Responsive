// File: utils/response_helper.js
// Standardized API response helper utility

export class ResponseHelper {
    /**
     * Send success response (200)
     * @param {Object} res - Express response object
     * @param {string} message - Success message
     * @param {Object} data - Response data
     */
    static success(res, message = 'Success', data = null) {
        const response = {
            success: true,
            message,
            timestamp: new Date().toISOString(),
            ...(data && { data })
        };
        
        return res.status(200).json(response);
    }

    /**
     * Send created response (201)
     * @param {Object} res - Express response object
     * @param {string} message - Success message
     * @param {Object} data - Response data
     */
    static created(res, message = 'Resource created successfully', data = null) {
        const response = {
            success: true,
            message,
            timestamp: new Date().toISOString(),
            ...(data && { data })
        };
        
        return res.status(201).json(response);
    }

    /**
     * Send no content response (204)
     * @param {Object} res - Express response object
     */
    static noContent(res) {
        return res.status(204).send();
    }

    /**
     * Send bad request response (400)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     * @param {Object} errors - Validation errors
     */
    static badRequest(res, message = 'Bad request', errors = null) {
        const response = {
            success: false,
            error: {
                type: 'BAD_REQUEST',
                message,
                timestamp: new Date().toISOString(),
                ...(errors && { details: errors })
            }
        };
        
        return res.status(400).json(response);
    }

    /**
     * Send validation error response (422)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     * @param {Array} validationErrors - Validation error details
     */
    static validationError(res, message = 'Validation failed', validationErrors = []) {
        const response = {
            success: false,
            error: {
                type: 'VALIDATION_ERROR',
                message,
                timestamp: new Date().toISOString(),
                validation_errors: validationErrors
            }
        };
        
        return res.status(422).json(response);
    }

    /**
     * Send unauthorized response (401)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     */
    static unauthorized(res, message = 'Unauthorized access') {
        const response = {
            success: false,
            error: {
                type: 'UNAUTHORIZED',
                message,
                timestamp: new Date().toISOString()
            }
        };
        
        return res.status(401).json(response);
    }

    /**
     * Send forbidden response (403)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     */
    static forbidden(res, message = 'Access forbidden') {
        const response = {
            success: false,
            error: {
                type: 'FORBIDDEN',
                message,
                timestamp: new Date().toISOString()
            }
        };
        
        return res.status(403).json(response);
    }

    /**
     * Send not found response (404)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     */
    static notFound(res, message = 'Resource not found') {
        const response = {
            success: false,
            error: {
                type: 'NOT_FOUND',
                message,
                timestamp: new Date().toISOString()
            }
        };
        
        return res.status(404).json(response);
    }

    /**
     * Send conflict response (409)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     */
    static conflict(res, message = 'Resource conflict') {
        const response = {
            success: false,
            error: {
                type: 'CONFLICT',
                message,
                timestamp: new Date().toISOString()
            }
        };
        
        return res.status(409).json(response);
    }

    /**
     * Send too many requests response (429)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     * @param {number} retryAfter - Retry after seconds
     */
    static tooManyRequests(res, message = 'Too many requests', retryAfter = null) {
        const response = {
            success: false,
            error: {
                type: 'RATE_LIMIT_EXCEEDED',
                message,
                timestamp: new Date().toISOString(),
                ...(retryAfter && { retry_after: retryAfter })
            }
        };

        if (retryAfter) {
            res.set('Retry-After', retryAfter.toString());
        }
        
        return res.status(429).json(response);
    }

    /**
     * Send internal server error response (500)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     * @param {string} errorId - Error tracking ID
     */
    static internalError(res, message = 'Internal server error', errorId = null) {
        const response = {
            success: false,
            error: {
                type: 'INTERNAL_SERVER_ERROR',
                message,
                timestamp: new Date().toISOString(),
                ...(errorId && { error_id: errorId })
            }
        };
        
        return res.status(500).json(response);
    }

    /**
     * Send service unavailable response (503)
     * @param {Object} res - Express response object
     * @param {string} message - Error message
     */
    static serviceUnavailable(res, message = 'Service temporarily unavailable') {
        const response = {
            success: false,
            error: {
                type: 'SERVICE_UNAVAILABLE',
                message,
                timestamp: new Date().toISOString()
            }
        };
        
        return res.status(503).json(response);
    }

    /**
     * Send custom error response
     * @param {Object} res - Express response object
     * @param {number} statusCode - HTTP status code
     * @param {string} errorType - Error type identifier
     * @param {string} message - Error message
     * @param {Object} additionalData - Additional error data
     */
    static customError(res, statusCode, errorType, message, additionalData = null) {
        const response = {
            success: false,
            error: {
                type: errorType,
                message,
                timestamp: new Date().toISOString(),
                ...(additionalData && additionalData)
            }
        };
        
        return res.status(statusCode).json(response);
    }

    /**
     * Send paginated response
     * @param {Object} res - Express response object
     * @param {Array} data - Data array
     * @param {Object} pagination - Pagination metadata
     * @param {string} message - Success message
     */
    static paginated(res, data, pagination, message = 'Data retrieved successfully') {
        const response = {
            success: true,
            message,
            timestamp: new Date().toISOString(),
            data,
            pagination: {
                page: pagination.page || 1,
                limit: pagination.limit || 10,
                total_items: pagination.totalItems || 0,
                total_pages: pagination.totalPages || 0,
                has_next: pagination.hasNext || false,
                has_previous: pagination.hasPrevious || false
            }
        };
        
        return res.status(200).json(response);
    }

    /**
     * Handle async route errors
     * @param {Function} fn - Async route handler
     * @returns {Function} Express middleware
     */
    static asyncHandler(fn) {
        return (req, res, next) => {
            Promise.resolve(fn(req, res, next)).catch(next);
        };
    }

    /**
     * Format validation errors from express-validator
     * @param {Array} errors - Express-validator errors array
     * @returns {Array} Formatted validation errors
     */
    static formatValidationErrors(errors) {
        return errors.map(error => ({
            field: error.path || error.param,
            message: error.msg,
            value: error.value,
            location: error.location
        }));
    }
}