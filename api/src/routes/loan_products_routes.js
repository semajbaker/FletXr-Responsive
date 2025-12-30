// File: src/routes/loan_products_routes.js
import express from 'express';
import { LoanProductsController } from '../controllers/loan_products_controller.js';
import { authenticateToken } from '../middleware/auth_middleware.js';
import { authorizeRoles } from '../middleware/authorization_middleware.js';
import { 
    validateCreateLoanProduct, 
    validateUpdateLoanProduct,
    validateLoanCalculation,
    validateUUIDParam,
    validatePagination,
    validateInterestTypeParam
} from '../middleware/business_validation_middleware.js';

const router = express.Router();
const productsController = new LoanProductsController();

/**
 * Static routes first to avoid conflicts
 */

// GET /api/loan-products/statistics - Get statistics (Admin/Superuser only)
router.get('/statistics', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    (req, res) => {
        productsController.getProductStatistics(req, res);
    }
);

// GET /api/loan-products/active - Get active products (All authenticated users)
router.get('/active', 
    authenticateToken,
    (req, res) => {
        productsController.getActiveProductsForSelection(req, res);
    }
);

// GET /api/loan-products/by-interest-type/:interestType - Get by interest type (All authenticated users)
router.get('/by-interest-type/:interestType', 
    authenticateToken,
    validateInterestTypeParam,
    (req, res) => {
        productsController.getProductsByInterestType(req, res);
    }
);

/**
 * Main CRUD routes
 */

// POST /api/loan-products - Create new product (Admin/Superuser only)
router.post('/', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateCreateLoanProduct,
    (req, res) => {
        productsController.createProduct(req, res);
    }
);

// GET /api/loan-products - Get all products with pagination (All authenticated users)
router.get('/', 
    authenticateToken,
    validatePagination,
    (req, res) => {
        productsController.getAllProducts(req, res);
    }
);

/**
 * Parameterized routes last
 */

// POST /api/loan-products/:id/calculate - Calculate loan details (All authenticated users)
router.post('/:id/calculate', 
    authenticateToken,
    validateUUIDParam('id'),
    validateLoanCalculation,
    (req, res) => {
        productsController.calculateLoanDetails(req, res);
    }
);

// GET /api/loan-products/:id - Get product by ID (All authenticated users)
router.get('/:id', 
    authenticateToken,
    validateUUIDParam('id'),
    (req, res) => {
        productsController.getProductById(req, res);
    }
);

// PUT /api/loan-products/:id - Update product (Admin/Superuser only)
router.put('/:id', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    validateUpdateLoanProduct,
    (req, res) => {
        productsController.updateProduct(req, res);
    }
);

// DELETE /api/loan-products/:id - Hard delete product (Admin/Superuser only)
router.delete('/:id', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        productsController.deleteProduct(req, res);  // CHANGED: Now calls deleteProduct instead of deactivateProduct
    }
);

export default router;