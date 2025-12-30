// File: src/services/borrower_categories_service.js
// Borrower categories data access service layer

import { DatabaseConnection } from '../config/database_connection.js';

export class BorrowerCategoriesService {
    constructor() {
        this.db = DatabaseConnection.getInstance();
    }

    /**
     * Create new borrower category
     * @param {Object} categoryData - Category data object
     * @returns {Promise<Object>} Created category
     */
    async createCategory(categoryData) {
        const query = `
            INSERT INTO borrower_categories (
                name, 
                description, 
                is_active
            )
            VALUES ($1, $2, $3)
            RETURNING id, name, description, is_active, created_at
        `;

        const values = [
            categoryData.name,
            categoryData.description,
            categoryData.is_active !== undefined ? categoryData.is_active : true
        ];

        try {
            const result = await this.db.query(query, values);
            return result.rows[0];
        } catch (error) {
            console.error('Error creating borrower category:', error);
            if (error.code === '23505') { // Unique violation
                throw new Error('Category with this name already exists');
            }
            throw new Error('Failed to create borrower category');
        }
    }

    /**
     * Get all borrower categories with pagination
     * @param {number} limit - Limit number of results
     * @param {number} offset - Offset for pagination
     * @param {boolean} activeOnly - Filter for active categories only
     * @returns {Promise<Object>} Categories with pagination metadata
     */
    async getAllCategories(limit = 50, offset = 0, activeOnly = true) {
        const whereClause = activeOnly ? 'WHERE is_active = true' : '';

        const countQuery = `
            SELECT COUNT(*) as total 
            FROM borrower_categories 
            ${whereClause}
        `;

        const dataQuery = `
            SELECT id, name, description, is_active, created_at
            FROM borrower_categories 
            ${whereClause}
            ORDER BY created_at DESC
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
                categories: dataResult.rows,
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
            console.error('Error getting borrower categories:', error);
            throw new Error('Failed to retrieve borrower categories');
        }
    }
    /**
         * Hard delete borrower category (permanently remove from database)
         * @param {string} categoryId - Category ID (UUID)
         * @returns {Promise<Object|null>} Deleted category object or null
         */
    async hardDeleteCategory(categoryId) {
        const query = `
            DELETE FROM borrower_categories 
            WHERE id = $1
            RETURNING id, name, description, is_active, created_at
        `;

        try {
            const result = await this.db.query(query, [categoryId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error hard deleting borrower category:', error);

            // Check for foreign key constraint violations
            if (error.code === '23503') {
                throw new Error('Cannot delete category - it is being used by other records');
            }

            throw new Error('Failed to delete borrower category');
        }
    }
    /**
     * Get borrower category by ID
     * @param {string} categoryId - Category ID (UUID)
     * @returns {Promise<Object|null>} Category object or null
     */
    async getCategoryById(categoryId) {
        const query = `
            SELECT id, name, description, is_active, created_at
            FROM borrower_categories 
            WHERE id = $1
        `;

        try {
            const result = await this.db.query(query, [categoryId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding borrower category by ID:', error);
            throw new Error('Failed to find borrower category');
        }
    }

    /**
     * Update borrower category
     * @param {string} categoryId - Category ID (UUID)
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated category object
     */
    async updateCategory(categoryId, updateData) {
        const allowedFields = ['name', 'description', 'is_active'];
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

        values.push(categoryId);

        const query = `
            UPDATE borrower_categories 
            SET ${updates.join(', ')}
            WHERE id = $${paramIndex}
            RETURNING id, name, description, is_active, created_at
        `;

        try {
            const result = await this.db.query(query, values);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error updating borrower category:', error);
            if (error.code === '23505') { // Unique violation
                throw new Error('Category with this name already exists');
            }
            throw new Error('Failed to update borrower category');
        }
    }

    /**
     * Get active categories for dropdown/selection
     * @returns {Promise<Array>} Array of active categories
     */
    async getActiveCategoriesForSelection() {
        const query = `
            SELECT id, name, description
            FROM borrower_categories 
            WHERE is_active = true
            ORDER BY name ASC
        `;

        try {
            const result = await this.db.query(query);
            return result.rows;
        } catch (error) {
            console.error('Error getting active categories:', error);
            throw new Error('Failed to get active categories');
        }
    }

    /**
     * Get category statistics
     * @returns {Promise<Object>} Category statistics
     */
    async getCategoryStatistics() {
        const query = `
            SELECT 
                COUNT(*) as total_categories,
                COUNT(*) FILTER (WHERE is_active = true) as active_categories,
                COUNT(*) FILTER (WHERE is_active = false) as inactive_categories
            FROM borrower_categories
        `;

        try {
            const result = await this.db.query(query);
            return result.rows[0];
        } catch (error) {
            console.error('Error getting category statistics:', error);
            throw new Error('Failed to get category statistics');
        }
    }

    /**
     * Check if category name exists
     * @param {string} name - Category name
     * @param {string} excludeId - Category ID to exclude from check (for updates)
     * @returns {Promise<boolean>} True if exists
     */
    async categoryNameExists(name, excludeId = null) {
        let query = `
            SELECT COUNT(*) as count 
            FROM borrower_categories 
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
            console.error('Error checking category name existence:', error);
            throw new Error('Failed to check category name');
        }
    }
}