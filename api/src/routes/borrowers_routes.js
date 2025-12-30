// File: src/routes/borrowers_routes.js
import express from 'express';
import { BorrowersController } from '../controllers/borrowers_controller.js';
import { authenticateToken } from '../middleware/auth_middleware.js';
import { authorizeRoles, authorizeBorrowerAccess } from '../middleware/authorization_middleware.js';
import { 
    validateCreateBorrower, 
    validateUpdateBorrower,
    validateUpdateKycStatus,
    validateBlacklistBorrower,
    validateUUIDParam,
    validatePagination,
    validateBorrowerSearch
} from '../middleware/business_validation_middleware.js';

const router = express.Router();
const borrowersController = new BorrowersController();

/**
 * Static routes first to avoid conflicts
 */

// GET /api/borrowers/statistics - Get borrower statistics (Admin/Superuser only)
router.get('/statistics', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    (req, res) => {
        borrowersController.getBorrowerStatistics(req, res);
    }
);

// GET /api/borrowers/search - Search borrowers (Staff only)
router.get('/search', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'collection_officer', 'admin', 'superuser']),
    validateBorrowerSearch,
    (req, res) => {
        borrowersController.searchBorrowers(req, res);
    }
);

// GET /api/borrowers/by-category/:categoryId - Get borrowers by category (Staff only)
router.get('/by-category/:categoryId', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'collection_officer', 'admin', 'superuser']),
    validateUUIDParam('categoryId'),
    (req, res) => {
        borrowersController.getBorrowersByCategory(req, res);
    }
);

/**
 * Main CRUD routes
 */

// POST /api/borrowers - Create new borrower (Loan Officer and above)
router.post('/', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'admin', 'superuser']),
    validateCreateBorrower,
    (req, res) => {
        borrowersController.createBorrower(req, res);
    }
);

// GET /api/borrowers - Get all borrowers with pagination (Staff only)
router.get('/', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser']),
    validatePagination,
    (req, res) => {
        borrowersController.getAllBorrowers(req, res);
    }
);

/**
 * Parameterized routes last
 */

// GET /api/borrowers/:id/credit-history - Get borrower credit history (Staff only)
router.get('/:id/credit-history', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        borrowersController.getBorrowerCreditHistory(req, res);
    }
);

// PATCH /api/borrowers/:id/kyc-status - Update KYC status (Loan Officer and above)
router.patch('/:id/kyc-status', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'admin', 'superuser']),
    validateUUIDParam('id'),
    validateUpdateKycStatus,
    (req, res) => {
        borrowersController.updateKycStatus(req, res);
    }
);

// PATCH /api/borrowers/:id/blacklist - Blacklist borrower (Admin/Superuser only)
router.patch('/:id/blacklist', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    validateBlacklistBorrower,
    (req, res) => {
        borrowersController.blacklistBorrower(req, res);
    }
);

// PATCH /api/borrowers/:id/reactivate - Reactivate borrower (Admin/Superuser only)
router.patch('/:id/reactivate', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        borrowersController.reactivateBorrower(req, res);
    }
);

// GET /api/borrowers/:id - Get borrower by ID (Staff only)
router.get('/:id', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'collection_officer', 'auditor', 'admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        borrowersController.getBorrowerById(req, res);
    }
);

// PUT /api/borrowers/:id - Update borrower (Loan Officer and above)
router.put('/:id', 
    authenticateToken,
    authorizeRoles(['loan_officer', 'admin', 'superuser']),
    validateUUIDParam('id'),
    validateUpdateBorrower,
    (req, res) => {
        borrowersController.updateBorrower(req, res);
    }
);

// DELETE /api/borrowers/:id - Hard delete borrower (Admin/Superuser only)
router.delete('/:id', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        borrowersController.deleteBorrower(req, res);
    }
);

export default router;