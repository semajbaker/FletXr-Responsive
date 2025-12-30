// File: src/services/loan_products_service.js
// Loan products data access service layer - FIXED VERSION

import { DatabaseConnection } from '../config/database_connection.js';

export class LoanProductsService {
    constructor() {
        this.db = DatabaseConnection.getInstance();
    }

    /**
     * Create new loan product
     * @param {Object} productData - Product data object
     * @param {string} createdBy - User ID of creator
     * @returns {Promise<Object>} Created product
     */
    async createProduct(productData, createdBy) {
        const query = `
            INSERT INTO loan_products (
                name, 
                description, 
                interest_type, 
                interest_rate, 
                max_amount, 
                default_term_days, 
                grace_days, 
                penalty_type, 
                penalty_value, 
                min_credit_score, 
                is_active,
                created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING id, name, description, interest_type, interest_rate, 
                     max_amount, default_term_days, grace_days, penalty_type, 
                     penalty_value, min_credit_score, is_active, created_at, 
                     updated_at, created_by
        `;
        
        const values = [
            productData.name,
            productData.description,
            productData.interest_type || 'flat_monthly',
            productData.interest_rate,
            productData.max_amount,
            productData.default_term_days,
            productData.grace_days || 3,
            productData.penalty_type || 'fixed',
            productData.penalty_value,
            productData.min_credit_score || 0,
            productData.is_active !== undefined ? productData.is_active : true,
            createdBy
        ];

        try {
            const result = await this.db.query(query, values);
            return result.rows[0];
        } catch (error) {
            console.error('Error creating loan product:', error);
            if (error.code === '23505') { // Unique violation
                throw new Error('Product with this name already exists');
            }
            if (error.code === '23514') { // Check constraint violation
                throw new Error('Invalid product data: check constraint violation');
            }
            throw new Error('Failed to create loan product');
        }
    }

    /**
     * Get all loan products with pagination
     * @param {number} limit - Limit number of results
     * @param {number} offset - Offset for pagination
     * @param {boolean} activeOnly - Filter for active products only
     * @returns {Promise<Object>} Products with pagination metadata
     */
    async getAllProducts(limit = 50, offset = 0, activeOnly = true) {
        const whereClause = activeOnly ? 'WHERE lp.is_active = true' : '';
        
        const countQuery = `
            SELECT COUNT(*) as total 
            FROM loan_products lp
            ${whereClause}
        `;

        const dataQuery = `
            SELECT 
                lp.id, lp.name, lp.description, lp.interest_type, 
                lp.interest_rate, lp.max_amount, lp.default_term_days, 
                lp.grace_days, lp.penalty_type, lp.penalty_value, 
                lp.min_credit_score, lp.is_active, lp.created_at, 
                lp.updated_at,
                u.username as created_by_username
            FROM loan_products lp
            LEFT JOIN users u ON lp.created_by = u.id
            ${whereClause}
            ORDER BY lp.created_at DESC
            LIMIT $1 OFFSET $2
        `;

        try {
            const [countResult, dataResult] = await Promise.all([
                this.db.query(countQuery),
                this.db.query(dataQuery, [limit, offset])
            ]);

            const total = parseInt(countResult.rows[0].total);
            const totalPages = Math.ceil(total / limit);
            const currentPage = Math.floor(offset / limit) + 1;

            return {
                products: dataResult.rows,
                pagination: {
                    page: currentPage,
                    limit,
                    total_items: total,
                    total_pages: totalPages,
                    has_next: currentPage < totalPages,
                    has_previous: currentPage > 1
                }
            };
        } catch (error) {
            console.error('Error getting loan products:', error);
            throw new Error('Failed to retrieve loan products');
        }
    }

    /**
     * Hard delete loan product (permanently remove from database) - ADDED MISSING FUNCTIONALITY
     * @param {string} productId - Product ID (UUID)
     * @returns {Promise<Object|null>} Deleted product object or null
     */
    async hardDeleteProduct(productId) {
        const query = `
            DELETE FROM loan_products 
            WHERE id = $1
            RETURNING id, name, description, interest_type, interest_rate, 
                     max_amount, default_term_days, grace_days, penalty_type, 
                     penalty_value, min_credit_score, is_active, created_at, 
                     updated_at, created_by
        `;

        try {
            const result = await this.db.query(query, [productId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error hard deleting loan product:', error);

            // Check for foreign key constraint violations
            if (error.code === '23503') {
                throw new Error('Cannot delete product - it is being used by other records');
            }

            throw new Error('Failed to delete loan product');
        }
    }

    /**
     * Get loan product by ID
     * @param {string} productId - Product ID (UUID)
     * @returns {Promise<Object|null>} Product object or null
     */
    async getProductById(productId) {
        const query = `
            SELECT 
                lp.id, lp.name, lp.description, lp.interest_type, 
                lp.interest_rate, lp.max_amount, lp.default_term_days, 
                lp.grace_days, lp.penalty_type, lp.penalty_value, 
                lp.min_credit_score, lp.is_active, lp.created_at, 
                lp.updated_at,
                u.username as created_by_username
            FROM loan_products lp
            LEFT JOIN users u ON lp.created_by = u.id
            WHERE lp.id = $1
        `;

        try {
            const result = await this.db.query(query, [productId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding loan product by ID:', error);
            throw new Error('Failed to find loan product');
        }
    }

    /**
     * Update loan product
     * @param {string} productId - Product ID (UUID)
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated product object
     */
    async updateProduct(productId, updateData) {
        const allowedFields = [
            'name', 'description', 'interest_type', 'interest_rate', 
            'max_amount', 'default_term_days', 'grace_days', 'penalty_type', 
            'penalty_value', 'min_credit_score', 'is_active'
        ];
        const updates = [];
        const values = [];
        let paramIndex = 1;

        // Build dynamic update query
        for (const [field, value] of Object.entries(updateData)) {
            if (allowedFields.includes(field) && value !== undefined) {
                updates.push(`${field} = $${paramIndex}`);
                values.push(value);
                paramIndex++;
            }
        }

        if (updates.length === 0) {
            throw new Error('No valid fields to update');
        }

        // Add updated_at (handled by trigger)
        values.push(productId);

        const query = `
            UPDATE loan_products 
            SET ${updates.join(', ')}
            WHERE id = $${paramIndex}
            RETURNING id, name, description, interest_type, interest_rate, 
                     max_amount, default_term_days, grace_days, penalty_type, 
                     penalty_value, min_credit_score, is_active, created_at, 
                     updated_at, created_by
        `;

        try {
            const result = await this.db.query(query, values);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error updating loan product:', error);
            if (error.code === '23505') { // Unique violation
                throw new Error('Product with this name already exists');
            }
            if (error.code === '23514') { // Check constraint violation
                throw new Error('Invalid product data: check constraint violation');
            }
            throw new Error('Failed to update loan product');
        }
    }

    /**
     * Get active products for dropdown/selection
     * @returns {Promise<Array>} Array of active products
     */
    async getActiveProductsForSelection() {
        const query = `
            SELECT id, name, description, interest_rate, max_amount, default_term_days
            FROM loan_products 
            WHERE is_active = true
            ORDER BY name ASC
        `;

        try {
            const result = await this.db.query(query);
            return result.rows;
        } catch (error) {
            console.error('Error getting active products:', error);
            throw new Error('Failed to get active products');
        }
    }

    /**
     * Get products by interest type
     * @param {string} interestType - Interest type ('flat_monthly' or 'reducing_balance')
     * @returns {Promise<Array>} Array of products
     */
    async getProductsByInterestType(interestType) {
        const query = `
            SELECT id, name, description, interest_type, interest_rate, 
                   max_amount, default_term_days, grace_days, penalty_type, 
                   penalty_value, min_credit_score, is_active, created_at
            FROM loan_products 
            WHERE interest_type = $1 AND is_active = true
            ORDER BY interest_rate ASC
        `;

        try {
            const result = await this.db.query(query, [interestType]);
            return result.rows;
        } catch (error) {
            console.error('Error getting products by interest type:', error);
            throw new Error('Failed to get products by interest type');
        }
    }

    /**
     * Get product statistics
     * @returns {Promise<Object>} Product statistics
     */
    async getProductStatistics() {
        const query = `
            SELECT 
                COUNT(*) as total_products,
                COUNT(*) FILTER (WHERE is_active = true) as active_products,
                COUNT(*) FILTER (WHERE is_active = false) as inactive_products,
                COUNT(*) FILTER (WHERE interest_type = 'flat_monthly') as flat_monthly_products,
                COUNT(*) FILTER (WHERE interest_type = 'reducing_balance') as reducing_balance_products,
                AVG(interest_rate) as avg_interest_rate,
                MIN(interest_rate) as min_interest_rate,
                MAX(interest_rate) as max_interest_rate,
                AVG(max_amount) as avg_max_amount,
                MIN(max_amount) as min_max_amount,
                MAX(max_amount) as max_max_amount
            FROM loan_products
        `;

        try {
            const result = await this.db.query(query);
            return result.rows[0];
        } catch (error) {
            console.error('Error getting product statistics:', error);
            throw new Error('Failed to get product statistics');
        }
    }

    /**
     * Check if product name exists
     * @param {string} name - Product name
     * @param {string} excludeId - Product ID to exclude from check (for updates)
     * @returns {Promise<boolean>} True if exists
     */
    async productNameExists(name, excludeId = null) {
        let query = `
            SELECT COUNT(*) as count 
            FROM loan_products 
            WHERE LOWER(name) = LOWER($1)
        `;
        const values = [name];

        if (excludeId) {
            query += ` AND id != $2`;
            values.push(excludeId);
        }

        try {
            const result = await this.db.query(query, values);
            return parseInt(result.rows[0].count) > 0;
        } catch (error) {
            console.error('Error checking product name existence:', error);
            throw new Error('Failed to check product name');
        }
    }

    /**
     * Calculate loan details for a product
     * @param {string} productId - Product ID
     * @param {number} principalAmount - Loan principal amount
     * @param {number} termDays - Loan term in days (optional, uses default if not provided)
     * @returns {Promise<Object>} Calculated loan details
     */
    async calculateLoanDetails(productId, principalAmount, termDays = null) {
        const product = await this.getProductById(productId);
        if (!product) {
            throw new Error('Product not found');
        }

        if (!product.is_active) {
            throw new Error('Product is not active');
        }

        if (principalAmount > product.max_amount) {
            throw new Error(`Amount exceeds maximum limit of ${product.max_amount}`);
        }

        const loanTermDays = termDays || product.default_term_days;
        let interestAmount = 0;

        if (product.interest_type === 'flat_monthly') {
            // Flat monthly: Interest = Principal * Rate * (Days / 30)
            const monthlyPeriods = loanTermDays / 30;
            interestAmount = principalAmount * product.interest_rate * monthlyPeriods;
        } else if (product.interest_type === 'reducing_balance') {
            // Reducing balance calculation (simplified)
            // For accurate reducing balance, you'd need installment calculations
            const dailyRate = product.interest_rate / 365;
            interestAmount = principalAmount * dailyRate * loanTermDays;
        }

        const totalDueAmount = principalAmount + interestAmount;

        return {
            product_id: productId,
            product_name: product.name,
            principal_amount: parseFloat(principalAmount),
            interest_rate: product.interest_rate,
            interest_type: product.interest_type,
            term_days: loanTermDays,
            interest_amount: parseFloat(interestAmount.toFixed(2)),
            total_due_amount: parseFloat(totalDueAmount.toFixed(2)),
            grace_days: product.grace_days,
            penalty_type: product.penalty_type,
            penalty_value: product.penalty_value
        };
    }
}