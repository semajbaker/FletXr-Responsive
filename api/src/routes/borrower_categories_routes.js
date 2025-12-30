// File: src/routes/borrower_categories_routes.js
import express from 'express';
import { BorrowerCategoriesController } from '../controllers/borrower_categories_controller.js';
import { authenticateToken } from '../middleware/auth_middleware.js';
import { authorizeRoles } from '../middleware/authorization_middleware.js';
import { 
    validateCreateBorrowerCategory, 
    validateUpdateBorrowerCategory,
    validateUUIDParam,
    validatePagination
} from '../middleware/business_validation_middleware.js';

const router = express.Router();
const categoriesController = new BorrowerCategoriesController();

/**
 * Static routes first to avoid conflicts
 */

// GET /api/borrower-categories/statistics - Get statistics (Admin/Superuser only)
router.get('/statistics', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    (req, res) => {
        categoriesController.getCategoryStatistics(req, res);
    }
);

// GET /api/borrower-categories/active - Get active categories (All authenticated users)
router.get('/active', 
    authenticateToken,
    (req, res) => {
        categoriesController.getActiveCategoriesForSelection(req, res);
    }
);

/**
 * Main CRUD routes
 */

// POST /api/borrower-categories - Create new category (Admin/Superuser only)
router.post('/', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateCreateBorrowerCategory,
    (req, res) => {
        categoriesController.createCategory(req, res);
    }
);

// GET /api/borrower-categories - Get all categories with pagination (All authenticated users)
router.get('/', 
    authenticateToken,
    validatePagination,
    (req, res) => {
        categoriesController.getAllCategories(req, res);
    }
);

/**
 * Parameterized routes last
 */

// GET /api/borrower-categories/:id - Get category by ID (All authenticated users)
router.get('/:id', 
    authenticateToken,
    validateUUIDParam('id'),
    (req, res) => {
        categoriesController.getCategoryById(req, res);
    }
);

// PUT /api/borrower-categories/:id - Update category (Admin/Superuser only)
router.put('/:id', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    validateUpdateBorrowerCategory,
    (req, res) => {
        categoriesController.updateCategory(req, res);
    }
);

// DELETE /api/borrower-categories/:id - Deactivate category (Admin/Superuser only)
router.delete('/:id', 
    authenticateToken,
    authorizeRoles(['admin', 'superuser']),
    validateUUIDParam('id'),
    (req, res) => {
        categoriesController.deactivateCategory(req, res);
    }
);

export default router;