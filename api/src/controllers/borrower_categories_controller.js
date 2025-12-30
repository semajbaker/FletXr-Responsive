// File: src/controllers/borrower_categories_controller.js
// Borrower categories controller for CRUD operations

import { BorrowerCategoriesService } from '../services/borrower_categories_service.js';
import { ResponseHelper } from '../utils/response_helper.js';

export class BorrowerCategoriesController {
    constructor() {
        this.categoriesService = new BorrowerCategoriesService();
    }

    /**
     * Create new borrower category
     * POST /api/borrower-categories
     */
    createCategory = async (req, res) => {
        try {
            const { name, description, is_active } = req.body;

            // Check if category name already exists
            const nameExists = await this.categoriesService.categoryNameExists(name);
            if (nameExists) {
                return ResponseHelper.conflict(res, 'Category with this name already exists');
            }

            // Create category data
            const categoryData = {
                name: name.trim(),
                description: description?.trim() || null,
                is_active: is_active !== undefined ? is_active : true
            };

            // Create category
            const newCategory = await this.categoriesService.createCategory(categoryData);

            ResponseHelper.created(res, 'Borrower category created successfully', {
                category: newCategory
            });

        } catch (error) {
            console.error('Create category error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to create borrower category');
        }
    };

    /**
     * Get all borrower categories with pagination
     * GET /api/borrower-categories
     */
    getAllCategories = async (req, res) => {
        try {
            const page = parseInt(req.query.page) || 1;
            const limit = parseInt(req.query.limit) || 20;

            // CRITICAL FIX: Proper boolean conversion for active_only parameter
            let activeOnly = true; // Default to true

            if (req.query.active_only !== undefined) {
                // Handle string values properly
                const activeOnlyParam = req.query.active_only.toLowerCase();
                activeOnly = activeOnlyParam === 'true' || activeOnlyParam === '1';
            }

            console.log(`[DEBUG] Controller - active_only param: "${req.query.active_only}", converted to: ${activeOnly}`);

            const offset = (page - 1) * limit;

            const result = await this.categoriesService.getAllCategories(limit, offset, activeOnly);

            console.log(`[DEBUG] Controller - Retrieved ${result.categories.length} categories`);
            result.categories.forEach(cat => {
                console.log(`  - ${cat.name}: ${cat.is_active ? 'Active' : 'Inactive'}`);
            });

            ResponseHelper.paginated(res, result.categories, result.pagination, 'Categories retrieved successfully');

        } catch (error) {
            console.error('Get categories error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve categories');
        }
    };

    /**
     * Get borrower category by ID
     * GET /api/borrower-categories/:id
     */
    getCategoryById = async (req, res) => {
        try {
            const { id } = req.params;

            const category = await this.categoriesService.getCategoryById(id);
            if (!category) {
                return ResponseHelper.notFound(res, 'Borrower category not found');
            }

            ResponseHelper.success(res, 'Category retrieved successfully', {
                category
            });

        } catch (error) {
            console.error('Get category by ID error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve category');
        }
    };

    /**
     * Update borrower category
     * PUT /api/borrower-categories/:id
     */
    updateCategory = async (req, res) => {
        try {
            const { id } = req.params;
            const updateData = req.body;

            // Check if category exists
            const existingCategory = await this.categoriesService.getCategoryById(id);
            if (!existingCategory) {
                return ResponseHelper.notFound(res, 'Borrower category not found');
            }

            // Check if name is being updated and if it already exists
            if (updateData.name && updateData.name !== existingCategory.name) {
                const nameExists = await this.categoriesService.categoryNameExists(updateData.name, id);
                if (nameExists) {
                    return ResponseHelper.conflict(res, 'Category with this name already exists');
                }
                updateData.name = updateData.name.trim();
            }

            // Trim description if provided
            if (updateData.description) {
                updateData.description = updateData.description.trim();
            }

            // Update category
            const updatedCategory = await this.categoriesService.updateCategory(id, updateData);

            ResponseHelper.success(res, 'Category updated successfully', {
                category: updatedCategory
            });

        } catch (error) {
            console.error('Update category error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            if (error.message.includes('No valid fields')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to update category');
        }
    };

    /**
     * Get active categories for dropdown/selection
     * GET /api/borrower-categories/active
     */
    getActiveCategoriesForSelection = async (req, res) => {
        try {
            const categories = await this.categoriesService.getActiveCategoriesForSelection();

            ResponseHelper.success(res, 'Active categories retrieved successfully', {
                categories
            });

        } catch (error) {
            console.error('Get active categories error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve active categories');
        }
    };

    /**
     * Get category statistics
     * GET /api/borrower-categories/statistics
     */
    getCategoryStatistics = async (req, res) => {
        try {
            const statistics = await this.categoriesService.getCategoryStatistics();

            ResponseHelper.success(res, 'Category statistics retrieved successfully', {
                statistics
            });

        } catch (error) {
            console.error('Get category statistics error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve category statistics');
        }
    };

    /**
         * Hard delete category (permanently remove from database)
         * DELETE /api/borrower-categories/:id
         */
    deactivateCategory = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if category exists
            const existingCategory = await this.categoriesService.getCategoryById(id);
            if (!existingCategory) {
                return ResponseHelper.notFound(res, 'Borrower category not found');
            }

            // Hard delete category - permanently remove from database
            const deletedCategory = await this.categoriesService.hardDeleteCategory(id);

            if (!deletedCategory) {
                return ResponseHelper.notFound(res, 'Category not found or already deleted');
            }

            ResponseHelper.success(res, 'Category permanently deleted successfully', {
                deleted_category: deletedCategory
            });

        } catch (error) {
            console.error('Hard delete category error:', error);

            // Handle foreign key constraint violations
            if (error.message.includes('being used by other records') || error.message.includes('constraint')) {
                return ResponseHelper.conflict(res, 'Cannot delete category - it is being used by other records. Please remove these references first.');
            }

            ResponseHelper.internalError(res, 'Failed to delete category');
        }
    };
}