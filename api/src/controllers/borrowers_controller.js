// File: src/controllers/borrowers_controller.js
// Borrowers controller for CRUD operations with KYC management

import { BorrowersService } from '../services/borrowers_service.js';
import { ResponseHelper } from '../utils/response_helper.js';

export class BorrowersController {
    constructor() {
        this.borrowersService = new BorrowersService();
    }

    /**
     * Create new borrower
     * POST /api/borrowers
     */
    createBorrower = async (req, res) => {
        try {
            const {
                full_name, phone_primary, phone_whatsapp, email, id_number,
                date_of_birth, address, category_id, employer_or_school,
                referrer, credit_score, risk_tier, notes
            } = req.body;

            // Get creator user ID from authenticated user
            const createdBy = req.user?.userId;
            if (!createdBy) {
                return ResponseHelper.unauthorized(res, 'User authentication required');
            }

            // Check if ID number already exists
            const idExists = await this.borrowersService.borrowerIdNumberExists(id_number);
            if (idExists) {
                return ResponseHelper.conflict(res, 'Borrower with this ID number already exists');
            }

            // Check if primary phone already exists
            const phoneExists = await this.borrowersService.borrowerPhoneExists(phone_primary);
            if (phoneExists) {
                return ResponseHelper.conflict(res, 'Borrower with this phone number already exists');
            }

            // Generate unique borrower code
            const borrowerCode = await this.borrowersService.generateBorrowerCode();

            // Create borrower data
            const borrowerData = {
                borrower_code: borrowerCode,
                full_name: full_name.trim(),
                phone_primary: phone_primary.trim(),
                phone_whatsapp: phone_whatsapp?.trim() || null,
                email: email?.trim() || null,
                id_number: id_number.trim(),
                date_of_birth,
                address: address.trim(),
                category_id,
                employer_or_school: employer_or_school?.trim() || null,
                referrer: referrer?.trim() || null,
                credit_score: credit_score !== undefined ? credit_score : 50,
                risk_tier: risk_tier || 'standard',
                status: 'active',
                kyc_status: 'incomplete',
                notes: notes?.trim() || null
            };

            // Create borrower
            const newBorrower = await this.borrowersService.createBorrower(borrowerData, createdBy);

            ResponseHelper.created(res, 'Borrower created successfully', {
                borrower: newBorrower
            });

        } catch (error) {
            console.error('Create borrower error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            if (error.message.includes('Invalid category')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to create borrower');
        }
    };

    /**
     * Get all borrowers with pagination and filtering
     * GET /api/borrowers
     */
    getAllBorrowers = async (req, res) => {
        try {
            const page = parseInt(req.query.page) || 1;
            const limit = parseInt(req.query.limit) || 20;
            const status = req.query.status || null; // active, inactive, blacklisted
            const kycStatus = req.query.kyc_status || null; // incomplete, pending, approved, rejected
            const categoryId = req.query.category_id || null;
            const search = req.query.search || null; // Search by name, phone, ID number

            const offset = (page - 1) * limit;

            const result = await this.borrowersService.getAllBorrowers(
                limit, offset, status, kycStatus, categoryId, search
            );

            ResponseHelper.paginated(res, result.borrowers, result.pagination, 'Borrowers retrieved successfully');

        } catch (error) {
            console.error('Get borrowers error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve borrowers');
        }
    };

    /**
     * Get borrower by ID
     * GET /api/borrowers/:id
     */
    getBorrowerById = async (req, res) => {
        try {
            const { id } = req.params;

            const borrower = await this.borrowersService.getBorrowerById(id);
            if (!borrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            ResponseHelper.success(res, 'Borrower retrieved successfully', {
                borrower
            });

        } catch (error) {
            console.error('Get borrower by ID error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve borrower');
        }
    };

    /**
     * Update borrower
     * PUT /api/borrowers/:id
     */
    updateBorrower = async (req, res) => {
        try {
            const { id } = req.params;
            const updateData = req.body;

            // Check if borrower exists
            const existingBorrower = await this.borrowersService.getBorrowerById(id);
            if (!existingBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            // Check if ID number is being updated and if it already exists
            if (updateData.id_number && updateData.id_number !== existingBorrower.id_number) {
                const idExists = await this.borrowersService.borrowerIdNumberExists(updateData.id_number, id);
                if (idExists) {
                    return ResponseHelper.conflict(res, 'Borrower with this ID number already exists');
                }
                updateData.id_number = updateData.id_number.trim();
            }

            // Check if primary phone is being updated and if it already exists
            if (updateData.phone_primary && updateData.phone_primary !== existingBorrower.phone_primary) {
                const phoneExists = await this.borrowersService.borrowerPhoneExists(updateData.phone_primary, id);
                if (phoneExists) {
                    return ResponseHelper.conflict(res, 'Borrower with this phone number already exists');
                }
                updateData.phone_primary = updateData.phone_primary.trim();
            }

            // Trim string fields if provided
            const stringFields = ['full_name', 'phone_whatsapp', 'email', 'address', 'employer_or_school', 'referrer', 'notes'];
            stringFields.forEach(field => {
                if (updateData[field]) {
                    updateData[field] = updateData[field].trim();
                }
            });

            // Update borrower
            const updatedBorrower = await this.borrowersService.updateBorrower(id, updateData);

            ResponseHelper.success(res, 'Borrower updated successfully', {
                borrower: updatedBorrower
            });

        } catch (error) {
            console.error('Update borrower error:', error);
            if (error.message.includes('already exists')) {
                return ResponseHelper.conflict(res, error.message);
            }
            if (error.message.includes('No valid fields')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            if (error.message.includes('Invalid category')) {
                return ResponseHelper.badRequest(res, error.message);
            }
            ResponseHelper.internalError(res, 'Failed to update borrower');
        }
    };

    /**
     * Update KYC status
     * PATCH /api/borrowers/:id/kyc-status
     */
    updateKycStatus = async (req, res) => {
        try {
            const { id } = req.params;
            const { kyc_status, notes } = req.body;

            // Get approver user ID from authenticated user
            const approvedBy = req.user?.userId;
            if (!approvedBy) {
                return ResponseHelper.unauthorized(res, 'User authentication required');
            }

            // Check if borrower exists
            const existingBorrower = await this.borrowersService.getBorrowerById(id);
            if (!existingBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            // Update KYC status
            const updatedBorrower = await this.borrowersService.updateKycStatus(
                id, kyc_status, approvedBy, notes
            );

            ResponseHelper.success(res, 'KYC status updated successfully', {
                borrower: updatedBorrower
            });

        } catch (error) {
            console.error('Update KYC status error:', error);
            ResponseHelper.internalError(res, 'Failed to update KYC status');
        }
    };

    /**
     * Get borrower statistics
     * GET /api/borrowers/statistics
     */
    getBorrowerStatistics = async (req, res) => {
        try {
            const statistics = await this.borrowersService.getBorrowerStatistics();

            ResponseHelper.success(res, 'Borrower statistics retrieved successfully', {
                statistics
            });

        } catch (error) {
            console.error('Get borrower statistics error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve borrower statistics');
        }
    };

    /**
     * Get borrowers by category
     * GET /api/borrowers/by-category/:categoryId
     */
    getBorrowersByCategory = async (req, res) => {
        try {
            const { categoryId } = req.params;
            const activeOnly = req.query.active_only !== 'false'; // Default to true

            const borrowers = await this.borrowersService.getBorrowersByCategory(categoryId, activeOnly);

            ResponseHelper.success(res, 'Borrowers by category retrieved successfully', {
                borrowers,
                category_id: categoryId
            });

        } catch (error) {
            console.error('Get borrowers by category error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve borrowers by category');
        }
    };

    /**
     * Search borrowers
     * GET /api/borrowers/search
     */
    searchBorrowers = async (req, res) => {
        try {
            const { q: query, limit = 10 } = req.query;

            if (!query || query.trim().length < 2) {
                return ResponseHelper.badRequest(res, 'Search query must be at least 2 characters');
            }

            const borrowers = await this.borrowersService.searchBorrowers(query.trim(), parseInt(limit));

            ResponseHelper.success(res, 'Search completed successfully', {
                borrowers,
                query: query.trim(),
                total_results: borrowers.length
            });

        } catch (error) {
            console.error('Search borrowers error:', error);
            ResponseHelper.internalError(res, 'Failed to search borrowers');
        }
    };

    /**
     * Get borrower credit history
     * GET /api/borrowers/:id/credit-history
     */
    getBorrowerCreditHistory = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if borrower exists
            const borrower = await this.borrowersService.getBorrowerById(id);
            if (!borrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            const creditHistory = await this.borrowersService.getBorrowerCreditHistory(id);

            ResponseHelper.success(res, 'Credit history retrieved successfully', {
                borrower_id: id,
                borrower_name: borrower.full_name,
                credit_history: creditHistory
            });

        } catch (error) {
            console.error('Get credit history error:', error);
            ResponseHelper.internalError(res, 'Failed to retrieve credit history');
        }
    };

    /**
     * Hard delete borrower (permanently remove from database)
     * DELETE /api/borrowers/:id
     */
    deleteBorrower = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if borrower exists
            const existingBorrower = await this.borrowersService.getBorrowerById(id);
            if (!existingBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            // Hard delete borrower - permanently remove from database
            const deletedBorrower = await this.borrowersService.hardDeleteBorrower(id);

            if (!deletedBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found or already deleted');
            }

            ResponseHelper.success(res, 'Borrower permanently deleted successfully', {
                deleted_borrower: deletedBorrower
            });

        } catch (error) {
            console.error('Hard delete borrower error:', error);

            // Handle foreign key constraint violations
            if (error.message.includes('being used by other records') || error.message.includes('constraint')) {
                return ResponseHelper.conflict(res, 'Cannot delete borrower - they have existing loans or other records. Please remove these references first.');
            }

            ResponseHelper.internalError(res, 'Failed to delete borrower');
        }
    };

    /**
     * Blacklist borrower
     * PATCH /api/borrowers/:id/blacklist
     */
    blacklistBorrower = async (req, res) => {
        try {
            const { id } = req.params;
            const { reason } = req.body;

            // Check if borrower exists
            const existingBorrower = await this.borrowersService.getBorrowerById(id);
            if (!existingBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            // Blacklist borrower
            const updatedBorrower = await this.borrowersService.updateBorrower(id, {
                status: 'blacklisted',
                notes: reason ? `BLACKLISTED: ${reason}` : 'BLACKLISTED'
            });

            ResponseHelper.success(res, 'Borrower blacklisted successfully', {
                borrower: updatedBorrower
            });

        } catch (error) {
            console.error('Blacklist borrower error:', error);
            ResponseHelper.internalError(res, 'Failed to blacklist borrower');
        }
    };

    /**
     * Reactivate borrower
     * PATCH /api/borrowers/:id/reactivate
     */
    reactivateBorrower = async (req, res) => {
        try {
            const { id } = req.params;

            // Check if borrower exists
            const existingBorrower = await this.borrowersService.getBorrowerById(id);
            if (!existingBorrower) {
                return ResponseHelper.notFound(res, 'Borrower not found');
            }

            // Reactivate borrower
            const updatedBorrower = await this.borrowersService.updateBorrower(id, {
                status: 'active',
                notes: existingBorrower.notes ? `${existingBorrower.notes}\nREACTIVATED: ${new Date().toISOString()}` : `REACTIVATED: ${new Date().toISOString()}`
            });

            ResponseHelper.success(res, 'Borrower reactivated successfully', {
                borrower: updatedBorrower
            });

        } catch (error) {
            console.error('Reactivate borrower error:', error);
            ResponseHelper.internalError(res, 'Failed to reactivate borrower');
        }
    };
}