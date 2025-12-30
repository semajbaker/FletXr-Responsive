// File: src/controllers/loan_products_controller.js
// Loan products controller for CRUD operations - FIXED VERSION

import { LoanProductsService } from '../services/loan_products_service.js';
import { ResponseHelper } from '../utils/response_helper.js';

export class LoanProductsController {
    constructor() {
        this.productsService = new LoanProductsService();
    }

    /**
     * Create new loan product
     * POST /api/loan-products
     */
    createProduct = async (req, res) => {
        try {
            const {
                name, description, interest_type, interest_rate, max_amount,
                default_term_days, grace_days, penalty_type, penalty_value,
                min_credit_score, is_active
            } = req.body;

            // Get creator user ID from authenticated user
            const createdBy = req.user?.userId;
            if (!createdBy) {
                return ResponseHelper.unauthorized(res, 'User authentication required');
            }

            // Check if product name already exists
            const nameExists = await this.productsService.productNameExists(name);
            if (nameExists) {
                return ResponseHelper.conflict(res, 'Product with this name already exists');
            }

            // Create product data
            const productData = {
                name: name.trim(),
                description: description?.trim() || null,
                interest_type: interest_type || 'flat_monthly',
                interest_rate: parseFloat(interest_rate),
                max_amount: parseFloat(max_amount),
                default_term_days: parseInt(default_term_days),
                grace_days: grace_days !== undefined ? parseInt(grace_days) : 3,
                penalty_type: penalty_type || 'fixed',
                penalty_value: parseFloat(penalty_value),
                min_credit_score: min_credit_score !== undefined ? parseInt(min_credit_score) : 0,
                is_active: is_active !== undefined ? is_active : true
            };

            // Create product
            const newProduct = await this.productsService.createProduct(productData, createdBy);

            ResponseHelper.created(res, 'Loan product created successfully', {
                product: newProduct
            });

        } catch (error) {
            console.error('Create product error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            if (error.message.includes('check constraint violation')) {
                return ResponseHelper.badRequest(res, 'Invalid product data provided');
            }
            ResponseHelper.internalError(res, 'Failed to create loan product');
        }
    };

    /**
     * Get all loan products with pagination
     * GET /api/loan-products
     */
    getAllProducts = async (req, res) => {
        try {
            const page = parseInt(req.query.page) || 1;
            const limit = parseInt(req.query.limit) || 20;

            // CRITICAL FIX: Proper boolean conversion for active_only parameter (same as categories)
            let activeOnly = true; // Default to true

            if (req.query.active_only !== undefined) {
                // Handle string values properly
                const activeOnlyParam = req.query.active_only.toLowerCase();
                activeOnly = activeOnlyParam === 'true' || activeOnlyParam === '1';
            }

            console.log(`[DEBUG] Controller - active_only param: "${req.query.active_only}", converted to: ${activeOnly}`);

            const offset = (page - 1) * limit;

            const result = await this.productsService.getAllProducts(limit, offset, activeOnly);

            console.log(`[DEBUG] Controller - Retrieved ${result.products.length} products`);
            result.products.forEach(prod => {
                console.log(`  - ${prod.name}: ${prod.is_active ? 'Active' : 'Inactive'}`);
            });

            ResponseHelper.paginated(res, result.products, result.pagination, 'Products retrieved successfully');

        } catch (error) {
            console.error('Get products error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve products');
        }
    };

    /**
     * Get loan product by ID
     * GET /api/loan-products/:id
     */
    getProductById = async (req, res) => {
        try {
            const { id } = req.params;

            const product = await this.productsService.getProductById(id);
            if (!product) {
                return ResponseHelper.notFound(res, 'Loan product not found');
            }

            ResponseHelper.success(res, 'Product retrieved successfully', {
                product
            });

        } catch (error) {
            console.error('Get product by ID error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve product');
        }
    };

    /**
     * Update loan product
     * PUT /api/loan-products/:id
     */
    updateProduct = async (req, res) => {
        try {
            const { id } = req.params;
            const updateData = { ...req.body };

            // Check if product exists
            const existingProduct = await this.productsService.getProductById(id);
            if (!existingProduct) {
                return ResponseHelper.notFound(res, 'Loan product not found');
            }

            // Check if name is being updated and if it already exists
            if (updateData.name && updateData.name !== existingProduct.name) {
                const nameExists = await this.productsService.productNameExists(updateData.name, id);
                if (nameExists) {
                    return ResponseHelper.conflict(res, 'Product with this name already exists');
                }
                updateData.name = updateData.name.trim();
            }

            // Trim and parse data types
            if (updateData.description) {
                updateData.description = updateData.description.trim();
            }

            if (updateData.interest_rate !== undefined) {
                updateData.interest_rate = parseFloat(updateData.interest_rate);
            }

            if (updateData.max_amount !== undefined) {
                updateData.max_amount = parseFloat(updateData.max_amount);
            }

            if (updateData.default_term_days !== undefined) {
                updateData.default_term_days = parseInt(updateData.default_term_days);
            }

            if (updateData.grace_days !== undefined) {
                updateData.grace_days = parseInt(updateData.grace_days);
            }

            if (updateData.penalty_value !== undefined) {
                updateData.penalty_value = parseFloat(updateData.penalty_value);
            }

            if (updateData.min_credit_score !== undefined) {
                updateData.min_credit_score = parseInt(updateData.min_credit_score);
            }

            // Update product
            const updatedProduct = await this.productsService.updateProduct(id, updateData);

            ResponseHelper.success(res, 'Product updated successfully', {
                product: updatedProduct
            });

        } catch (error) {
            console.error('Update product error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            if (error.message.includes('check constraint violation')) {
                return ResponseHelper.badRequest(res, 'Invalid product data provided');
            }
            if (error.message.includes('No valid fields')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to update product');
        }
    };

    /**
     * Get active products for dropdown/selection
     * GET /api/loan-products/active
     */
    getActiveProductsForSelection = async (req, res) => {
        try {
            const products = await this.productsService.getActiveProductsForSelection();

            ResponseHelper.success(res, 'Active products retrieved successfully', {
                products
            });

        } catch (error) {
            console.error('Get active products error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve active products');
        }
    };

    /**
     * Get products by interest type
     * GET /api/loan-products/by-interest-type/:interestType
     */
    getProductsByInterestType = async (req, res) => {
        try {
            const { interestType } = req.params;

            // Validate interest type
            if (!['flat_monthly', 'reducing_balance'].includes(interestType)) {
                return ResponseHelper.badRequest(res, 'Invalid interest type. Must be flat_monthly or reducing_balance');
            }

            const products = await this.productsService.getProductsByInterestType(interestType);

            ResponseHelper.success(res, `Products with ${interestType} interest type retrieved successfully`, {
                products,
                interest_type: interestType
            });

        } catch (error) {
            console.error('Get products by interest type error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve products by interest type');
        }
    };

    /**
     * Get product statistics
     * GET /api/loan-products/statistics
     */
    getProductStatistics = async (req, res) => {
        try {
            const statistics = await this.productsService.getProductStatistics();

            // Convert numeric strings to numbers for better JSON response
            const formattedStats = {
                total_products: parseInt(statistics.total_products),
                active_products: parseInt(statistics.active_products),
                inactive_products: parseInt(statistics.inactive_products),
                flat_monthly_products: parseInt(statistics.flat_monthly_products),
                reducing_balance_products: parseInt(statistics.reducing_balance_products),
                avg_interest_rate: statistics.avg_interest_rate ? parseFloat(statistics.avg_interest_rate) : null,
                min_interest_rate: statistics.min_interest_rate ? parseFloat(statistics.min_interest_rate) : null,
                max_interest_rate: statistics.max_interest_rate ? parseFloat(statistics.max_interest_rate) : null,
                avg_max_amount: statistics.avg_max_amount ? parseFloat(statistics.avg_max_amount) : null,
                min_max_amount: statistics.min_max_amount ? parseFloat(statistics.min_max_amount) : null,
                max_max_amount: statistics.max_max_amount ? parseFloat(statistics.max_max_amount) : null
            };

            ResponseHelper.success(res, 'Product statistics retrieved successfully', {
                statistics: formattedStats
            });

        } catch (error) {
            console.error('Get product statistics error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve product statistics');
        }
    };

    /**
     * Calculate loan details for a product
     * POST /api/loan-products/:id/calculate
     */
    calculateLoanDetails = async (req, res) => {
        try {
            const { id } = req.params;
            const { principal_amount, term_days } = req.body;

            const calculationResult = await this.productsService.calculateLoanDetails(
                id,
                parseFloat(principal_amount),
                term_days ? parseInt(term_days) : null
            );

            ResponseHelper.success(res, 'Loan details calculated successfully', {
                calculation: calculationResult
            });

        } catch (error) {
            console.error('Calculate loan details error:', error);
            if (error.message.includes('not found')) {
                return ResponseHelper.notFound(res, error.message);
            }
            if (error.message.includes('not active')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            if (error.message.includes('exceeds maximum')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to calculate loan details');
        }
    };

    /**
         * Hard delete product (permanently remove from database)
         * DELETE /api/loan-products/:id
         */
    deleteProduct = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if product exists
            const existingProduct = await this.productsService.getProductById(id);
            if (!existingProduct) {
                return ResponseHelper.notFound(res, 'Loan product not found');
            }

            // Hard delete product - permanently remove from database
            const deletedProduct = await this.productsService.hardDeleteProduct(id);

            if (!deletedProduct) {
                return ResponseHelper.notFound(res, 'Product not found or already deleted');
            }

            ResponseHelper.success(res, 'Product permanently deleted successfully', {
                deleted_product: deletedProduct
            });

        } catch (error) {
            console.error('Hard delete product error:', error);

            // Handle foreign key constraint violations
            if (error.message.includes('being used by other records') || error.message.includes('constraint')) {
                return ResponseHelper.conflict(res, 'Cannot delete product - it is being used by other records. Please remove these references first.');
            }

            ResponseHelper.internalError(res, 'Failed to delete product');
        }
    };

    /**
     * Deactivate product (soft delete) - RENAMED FOR CLARITY
     * PATCH /api/loan-products/:id/deactivate
     */
    deactivateProduct = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if product exists
            const existingProduct = await this.productsService.getProductById(id);
            if (!existingProduct) {
                return ResponseHelper.notFound(res, 'Loan product not found');
            }

            // Deactivate product
            const updatedProduct = await this.productsService.updateProduct(id, { is_active: false });

            ResponseHelper.success(res, 'Product deactivated successfully', {
                product: updatedProduct
            });

        } catch (error) {
            console.error('Deactivate product error:', error);
            ResponseHelper.internalError(res, 'Failed to deactivate product');
        }
    };
}