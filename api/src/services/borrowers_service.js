// File: src/services/borrowers_service.js
// Borrowers data access service layer with KYC management

import { DatabaseConnection } from '../config/database_connection.js';

export class BorrowersService {
    constructor() {
        this.db = DatabaseConnection.getInstance();
    }

    /**
     * Generate unique borrower code
     * @returns {Promise<string>} Generated borrower code
     */
    async generateBorrowerCode() {
        const query = `
            SELECT COUNT(*) as count FROM borrowers
        `;

        try {
            const result = await this.db.query(query);
            const count = parseInt(result.rows[0].count) + 1;
            return `NZM-BOR-${count.toString().padStart(3, '0')}`;
        } catch (error) {
            console.error('Error generating borrower code:', error);
            throw new Error('Failed to generate borrower code');
        }
    }

    /**
     * Create new borrower
     * @param {Object} borrowerData - Borrower data object
     * @param {string} createdBy - User ID of creator
     * @returns {Promise<Object>} Created borrower
     */
    async createBorrower(borrowerData, createdBy) {
        const query = `
            INSERT INTO borrowers (
                borrower_code, full_name, phone_primary, phone_whatsapp, email,
                id_number, date_of_birth, address, category_id, employer_or_school,
                referrer, status, credit_score, risk_tier, kyc_status, notes, created_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            RETURNING 
                id, borrower_code, full_name, phone_primary, phone_whatsapp, email,
                id_number, date_of_birth, address, category_id, employer_or_school,
                referrer, status, credit_score, risk_tier, kyc_status, notes,
                created_at, updated_at
        `;

        const values = [
            borrowerData.borrower_code,
            borrowerData.full_name,
            borrowerData.phone_primary,
            borrowerData.phone_whatsapp,
            borrowerData.email,
            borrowerData.id_number,
            borrowerData.date_of_birth,
            borrowerData.address,
            borrowerData.category_id,
            borrowerData.employer_or_school,
            borrowerData.referrer,
            borrowerData.status || 'active',
            borrowerData.credit_score || 50,
            borrowerData.risk_tier || 'standard',
            borrowerData.kyc_status || 'incomplete',
            borrowerData.notes,
            createdBy
        ];

        try {
            const result = await this.db.query(query, values);
            return result.rows[0];
        } catch (error) {
            console.error('Error creating borrower:', error);
            if (error.code === '23505') { // Unique violation
                if (error.constraint?.includes('id_number')) {
                    throw new Error('Borrower with this ID number already exists');
                }
                if (error.constraint?.includes('phone_primary')) {
                    throw new Error('Borrower with this phone number already exists');
                }
                throw new Error('Borrower already exists');
            }
            if (error.code === '23503') { // Foreign key violation
                throw new Error('Invalid category ID provided');
            }
            throw new Error('Failed to create borrower');
        }
    }

    /**
     * Get all borrowers with pagination and filtering
     * @param {number} limit - Limit number of results
     * @param {number} offset - Offset for pagination
     * @param {string} status - Filter by status
     * @param {string} kycStatus - Filter by KYC status
     * @param {string} categoryId - Filter by category ID
     * @param {string} search - Search query
     * @returns {Promise<Object>} Borrowers with pagination metadata
     */
    async getAllBorrowers(limit = 50, offset = 0, status = null, kycStatus = null, categoryId = null, search = null) {
        let whereConditions = [];
        let queryParams = [];
        let paramIndex = 1;

        // Build WHERE conditions
        if (status) {
            whereConditions.push(`b.status = $${paramIndex}`);
            queryParams.push(status);
            paramIndex++;
        }

        if (kycStatus) {
            whereConditions.push(`b.kyc_status = $${paramIndex}`);
            queryParams.push(kycStatus);
            paramIndex++;
        }

        if (categoryId) {
            whereConditions.push(`b.category_id = $${paramIndex}`);
            queryParams.push(categoryId);
            paramIndex++;
        }

        if (search) {
            whereConditions.push(`(
                LOWER(b.full_name) LIKE LOWER($${paramIndex}) OR 
                b.phone_primary LIKE $${paramIndex} OR 
                b.id_number LIKE $${paramIndex} OR
                b.borrower_code LIKE $${paramIndex}
            )`);
            queryParams.push(`%${search}%`);
            paramIndex++;
        }

        const whereClause = whereConditions.length > 0 ? `WHERE ${whereConditions.join(' AND ')}` : '';

        const countQuery = `
            SELECT COUNT(*) as total 
            FROM borrowers b
            ${whereClause}
        `;

        const dataQuery = `
            SELECT 
                b.id, b.borrower_code, b.full_name, b.phone_primary, b.phone_whatsapp,
                b.email, b.id_number, b.date_of_birth, b.address, b.category_id,
                b.employer_or_school, b.referrer, b.status, b.credit_score, b.risk_tier,
                b.kyc_status, b.kyc_approved_at, b.notes, b.created_at, b.updated_at,
                bc.name as category_name,
                u1.username as created_by_username,
                u2.username as kyc_approved_by_username
            FROM borrowers b
            LEFT JOIN borrower_categories bc ON b.category_id = bc.id
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.kyc_approved_by = u2.id
            ${whereClause}
            ORDER BY b.created_at DESC
            LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
        `;

        queryParams.push(limit, offset);

        try {
            const [countResult, dataResult] = await Promise.all([
                this.db.query(countQuery, queryParams.slice(0, -2)), // Remove limit and offset for count
                this.db.query(dataQuery, queryParams)
            ]);

            const total = parseInt(countResult.rows[0].total);
            const totalPages = Math.ceil(total / limit);
            const currentPage = Math.floor(offset / limit) + 1;

            return {
                borrowers: dataResult.rows,
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
            console.error('Error getting borrowers:', error);
            throw new Error('Failed to retrieve borrowers');
        }
    }

    /**
     * Get borrower by ID
     * @param {string} borrowerId - Borrower ID (UUID)
     * @returns {Promise<Object|null>} Borrower object or null
     */
    async getBorrowerById(borrowerId) {
        const query = `
            SELECT 
                b.id, b.borrower_code, b.full_name, b.phone_primary, b.phone_whatsapp,
                b.email, b.id_number, b.date_of_birth, b.address, b.category_id,
                b.employer_or_school, b.referrer, b.status, b.credit_score, b.risk_tier,
                b.kyc_status, b.kyc_approved_at, b.notes, b.created_at, b.updated_at,
                bc.name as category_name,
                u1.username as created_by_username,
                u2.username as kyc_approved_by_username
            FROM borrowers b
            LEFT JOIN borrower_categories bc ON b.category_id = bc.id
            LEFT JOIN users u1 ON b.created_by = u1.id
            LEFT JOIN users u2 ON b.kyc_approved_by = u2.id
            WHERE b.id = $1
        `;

        try {
            const result = await this.db.query(query, [borrowerId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding borrower by ID:', error);
            throw new Error('Failed to find borrower');
        }
    }

    /**
     * Update borrower
     * @param {string} borrowerId - Borrower ID (UUID)
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated borrower object
     */
    async updateBorrower(borrowerId, updateData) {
        const allowedFields = [
            'full_name', 'phone_primary', 'phone_whatsapp', 'email', 'id_number',
            'date_of_birth', 'address', 'category_id', 'employer_or_school',
            'referrer', 'status', 'credit_score', 'risk_tier', 'kyc_status', 'notes'
        ];
        const updates = [];
        const values = [];
        let paramIndex = 1;

        // Build dynamic update query
        for (const [field, value] of Object.entries(updateData)) {
            if (allowedFields.includes(field) && value !== undefined) {
                updates.push(`${field} = ${paramIndex}`);
                values.push(value);
                paramIndex++;
            }
        }

        if (updates.length === 0) {
            throw new Error('No valid fields to update');
        }

        values.push(borrowerId);

        const query = `
            UPDATE borrowers 
            SET ${updates.join(', ')}
            WHERE id = ${paramIndex}
            RETURNING 
                id, borrower_code, full_name, phone_primary, phone_whatsapp, email,
                id_number, date_of_birth, address, category_id, employer_or_school,
                referrer, status, credit_score, risk_tier, kyc_status, notes,
                created_at, updated_at
        `;

        try {
            const result = await this.db.query(query, values);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error updating borrower:', error);
            if (error.code === '23505') { // Unique violation
                if (error.constraint?.includes('id_number')) {
                    throw new Error('Borrower with this ID number already exists');
                }
                if (error.constraint?.includes('phone_primary')) {
                    throw new Error('Borrower with this phone number already exists');
                }
                throw new Error('Borrower already exists');
            }
            if (error.code === '23503') { // Foreign key violation
                throw new Error('Invalid category ID provided');
            }
            throw new Error('Failed to update borrower');
        }
    }

    /**
     * Update KYC status
     * @param {string} borrowerId - Borrower ID (UUID)
     * @param {string} kycStatus - New KYC status
     * @param {string} approvedBy - User ID of approver
     * @param {string} notes - Additional notes
     * @returns {Promise<Object|null>} Updated borrower object
     */
    async updateKycStatus(borrowerId, kycStatus, approvedBy, notes = null) {
        const updateData = {
            kyc_status: kycStatus
        };

        if (kycStatus === 'approved') {
            updateData.kyc_approved_at = new Date().toISOString();
            updateData.kyc_approved_by = approvedBy;
        }

        if (notes) {
            updateData.notes = notes;
        }

        return this.updateBorrower(borrowerId, updateData);
    }

    /**
     * Hard delete borrower (permanently remove from database)
     * @param {string} borrowerId - Borrower ID (UUID)
     * @returns {Promise<Object|null>} Deleted borrower object or null
     */
    async hardDeleteBorrower(borrowerId) {
        const query = `
            DELETE FROM borrowers 
            WHERE id = $1
            RETURNING 
                id, borrower_code, full_name, phone_primary, phone_whatsapp, email,
                id_number, date_of_birth, address, category_id, employer_or_school,
                referrer, status, credit_score, risk_tier, kyc_status, notes,
                created_at, updated_at
        `;

        try {
            const result = await this.db.query(query, [borrowerId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error hard deleting borrower:', error);

            // Check for foreign key constraint violations
            if (error.code === '23503') {
                throw new Error('Cannot delete borrower - they are being used by other records');
            }

            throw new Error('Failed to delete borrower');
        }
    }

    /**
     * Get borrower statistics
     * @returns {Promise<Object>} Borrower statistics
     */
    async getBorrowerStatistics() {
        const query = `
            SELECT 
                COUNT(*) as total_borrowers,
                COUNT(*) FILTER (WHERE status = 'active') as active_borrowers,
                COUNT(*) FILTER (WHERE status = 'inactive') as inactive_borrowers,
                COUNT(*) FILTER (WHERE status = 'blacklisted') as blacklisted_borrowers,
                COUNT(*) FILTER (WHERE kyc_status = 'incomplete') as incomplete_kyc,
                COUNT(*) FILTER (WHERE kyc_status = 'pending') as pending_kyc,
                COUNT(*) FILTER (WHERE kyc_status = 'approved') as approved_kyc,
                COUNT(*) FILTER (WHERE kyc_status = 'rejected') as rejected_kyc,
                COUNT(*) FILTER (WHERE risk_tier = 'low') as low_risk,
                COUNT(*) FILTER (WHERE risk_tier = 'standard') as standard_risk,
                COUNT(*) FILTER (WHERE risk_tier = 'high') as high_risk,
                AVG(credit_score) as avg_credit_score,
                MIN(credit_score) as min_credit_score,
                MAX(credit_score) as max_credit_score
            FROM borrowers
        `;

        try {
            const result = await this.db.query(query);
            return result.rows[0];
        } catch (error) {
            console.error('Error getting borrower statistics:', error);
            throw new Error('Failed to get borrower statistics');
        }
    }

    /**
     * Get borrowers by category
     * @param {string} categoryId - Category ID (UUID)
     * @param {boolean} activeOnly - Filter for active borrowers only
     * @returns {Promise<Array>} Array of borrowers
     */
    async getBorrowersByCategory(categoryId, activeOnly = true) {
        const whereClause = activeOnly ? "AND b.status = 'active'" : '';

        const query = `
            SELECT 
                b.id, b.borrower_code, b.full_name, b.phone_primary, b.email,
                b.status, b.credit_score, b.risk_tier, b.kyc_status, b.created_at,
                bc.name as category_name
            FROM borrowers b
            LEFT JOIN borrower_categories bc ON b.category_id = bc.id
            WHERE b.category_id = $1 ${whereClause}
            ORDER BY b.full_name ASC
        `;

        try {
            const result = await this.db.query(query, [categoryId]);
            return result.rows;
        } catch (error) {
            console.error('Error getting borrowers by category:', error);
            throw new Error('Failed to get borrowers by category');
        }
    }

    /**
     * Search borrowers
     * @param {string} query - Search query
     * @param {number} limit - Limit number of results
     * @returns {Promise<Array>} Array of matching borrowers
     */
    async searchBorrowers(query, limit = 10) {
        const searchQuery = `
            SELECT 
                b.id, b.borrower_code, b.full_name, b.phone_primary, b.email,
                b.id_number, b.status, b.kyc_status, b.created_at,
                bc.name as category_name
            FROM borrowers b
            LEFT JOIN borrower_categories bc ON b.category_id = bc.id
            WHERE 
                LOWER(b.full_name) LIKE LOWER($1) OR 
                b.phone_primary LIKE $1 OR 
                b.id_number LIKE $1 OR
                b.borrower_code LIKE $1 OR
                LOWER(b.email) LIKE LOWER($1)
            ORDER BY 
                CASE 
                    WHEN LOWER(b.full_name) LIKE LOWER($1) THEN 1
                    WHEN b.borrower_code LIKE $1 THEN 2
                    ELSE 3
                END,
                b.full_name ASC
            LIMIT $2
        `;

        try {
            const result = await this.db.query(searchQuery, [`%${query}%`, limit]);
            return result.rows;
        } catch (error) {
            console.error('Error searching borrowers:', error);
            throw new Error('Failed to search borrowers');
        }
    }

    /**
     * Get borrower credit history
     * @param {string} borrowerId - Borrower ID (UUID)
     * @returns {Promise<Object>} Credit history data
     */
    async getBorrowerCreditHistory(borrowerId) {
        const query = `
            SELECT 
                l.id, l.loan_code, l.principal_amount, l.total_due_amount,
                l.issue_date, l.due_date, l.status, l.created_at,
                lp.name as product_name,
                COALESCE(SUM(r.amount_paid), 0) as total_paid,
                (l.total_due_amount - COALESCE(SUM(r.amount_paid), 0)) as outstanding_amount
            FROM loans l
            LEFT JOIN loan_products lp ON l.product_id = lp.id
            LEFT JOIN repayments r ON l.id = r.loan_id
            WHERE l.borrower_id = $1
            GROUP BY l.id, lp.name
            ORDER BY l.created_at DESC
        `;

        const summaryQuery = `
            SELECT 
                COUNT(*) as total_loans,
                COUNT(*) FILTER (WHERE l.status = 'paid') as paid_loans,
                COUNT(*) FILTER (WHERE l.status = 'active') as active_loans,
                COUNT(*) FILTER (WHERE l.status = 'overdue') as overdue_loans,
                COALESCE(SUM(l.principal_amount), 0) as total_borrowed,
                COALESCE(SUM(r.amount_paid), 0) as total_repaid
            FROM loans l
            LEFT JOIN repayments r ON l.id = r.loan_id
            WHERE l.borrower_id = $1
        `;

        try {
            const [loansResult, summaryResult] = await Promise.all([
                this.db.query(query, [borrowerId]),
                this.db.query(summaryQuery, [borrowerId])
            ]);

            return {
                summary: summaryResult.rows[0],
                loans: loansResult.rows
            };
        } catch (error) {
            console.error('Error getting borrower credit history:', error);
            throw new Error('Failed to get borrower credit history');
        }
    }

    /**
     * Check if borrower ID number exists
     * @param {string} idNumber - ID number
     * @param {string} excludeId - Borrower ID to exclude from check (for updates)
     * @returns {Promise<boolean>} True if exists
     */
    async borrowerIdNumberExists(idNumber, excludeId = null) {
        let query = `
            SELECT COUNT(*) as count 
            FROM borrowers 
            WHERE id_number = $1
        `;
        const values = [idNumber];

        if (excludeId) {
            query += ` AND id != $2`;
            values.push(excludeId);
        }

        try {
            const result = await this.db.query(query, values);
            return parseInt(result.rows[0].count) > 0;
        } catch (error) {
            console.error('Error checking borrower ID number existence:', error);
            throw new Error('Failed to check ID number');
        }
    }

    /**
     * Check if borrower phone exists
     * @param {string} phone - Phone number
     * @param {string} excludeId - Borrower ID to exclude from check (for updates)
     * @returns {Promise<boolean>} True if exists
     */
    async borrowerPhoneExists(phone, excludeId = null) {
        let query = `
            SELECT COUNT(*) as count 
            FROM borrowers 
            WHERE phone_primary = $1
        `;
        const values = [phone];

        if (excludeId) {
            query += ` AND id != $2`;
            values.push(excludeId);
        }

        try {
            const result = await this.db.query(query, values);
            return parseInt(result.rows[0].count) > 0;
        } catch (error) {
            console.error('Error checking borrower phone existence:', error);
            throw new Error('Failed to check phone number');
        }
    }
}