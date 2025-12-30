// File: services/user_service.js
// User data access service layer

import { DatabaseConnection } from '../config/database_connection.js';

export class UserService {
    constructor() {
        this.db = DatabaseConnection.getInstance();
    }

    /**
     * Create new user
     * @param {Object} userData - User data object
     * @returns {Promise<Object>} Created user
     */
    async createUser(userData) {
        const query = `
            INSERT INTO users (
                username, 
                email, 
                phone_number, 
                password_hash, 
                role, 
                is_active, 
                is_email_verified
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, username, email, phone_number, role, is_active, 
                     is_email_verified, created_at, updated_at
        `;
        
        const values = [
            userData.username,
            userData.email,
            userData.phone_number,
            userData.password_hash,
            userData.role,
            userData.is_active,
            userData.is_email_verified
        ];

        try {
            const result = await this.db.query(query, values);
            return result.rows[0];
        } catch (error) {
            console.error('Error creating user:', error);
            throw new Error('Failed to create user');
        }
    }

    /**
     * Find user by ID
     * @param {string} userId - User ID (UUID)
     * @returns {Promise<Object|null>} User object or null
     */
    async findById(userId) {
        const query = `
            SELECT id, username, email, phone_number, password_hash, role, 
                   is_active, is_email_verified, created_at, updated_at, last_login
            FROM users 
            WHERE id = $1 AND is_active = true
        `;

        try {
            const result = await this.db.query(query, [userId]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding user by ID:', error);
            throw new Error('Failed to find user');
        }
    }

    /**
     * Find user by email
     * @param {string} email - User email
     * @returns {Promise<Object|null>} User object or null
     */
    async findByEmail(email) {
        const query = `
            SELECT id, username, email, phone_number, password_hash, role, 
                   is_active, is_email_verified, created_at, updated_at, last_login
            FROM users 
            WHERE email = $1
        `;

        try {
            const result = await this.db.query(query, [email.toLowerCase()]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding user by email:', error);
            throw new Error('Failed to find user');
        }
    }

    /**
     * Find user by username
     * @param {string} username - Username
     * @returns {Promise<Object|null>} User object or null
     */
    async findByUsername(username) {
        const query = `
            SELECT id, username, email, phone_number, password_hash, role, 
                   is_active, is_email_verified, created_at, updated_at, last_login
            FROM users 
            WHERE username = $1
        `;

        try {
            const result = await this.db.query(query, [username.toLowerCase()]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding user by username:', error);
            throw new Error('Failed to find user');
        }
    }

    /**
     * Find user by email or username
     * @param {string} email - User email
     * @param {string} username - Username
     * @returns {Promise<Object|null>} User object or null
     */
    async findByEmailOrUsername(email, username) {
        const query = `
            SELECT id, username, email, phone_number, role, is_active, 
                   is_email_verified, created_at, updated_at
            FROM users 
            WHERE email = $1 OR username = $2
        `;

        try {
            const result = await this.db.query(query, [
                email.toLowerCase(), 
                username.toLowerCase()
            ]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding user by email or username:', error);
            throw new Error('Failed to find user');
        }
    }

    /**
     * Update user's last login timestamp
     * @param {string} userId - User ID (UUID)
     * @returns {Promise<boolean>} Success status
     */
    async updateLastLogin(userId) {
        const query = `
            UPDATE users 
            SET last_login = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        `;

        try {
            const result = await this.db.query(query, [userId]);
            return result.rowCount > 0;
        } catch (error) {
            console.error('Error updating last login:', error);
            throw new Error('Failed to update last login');
        }
    }

    /**
     * Update user profile
     * @param {string} userId - User ID (UUID)
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated user object
     */
    async updateUser(userId, updateData) {
        const allowedFields = ['username', 'email', 'phone_number', 'is_email_verified'];
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

        // Add updated_at
        updates.push(`updated_at = CURRENT_TIMESTAMP`);
        values.push(userId);

        const query = `
            UPDATE users 
            SET ${updates.join(', ')}
            WHERE id = $${paramIndex}
            RETURNING id, username, email, phone_number, role, is_active, 
                     is_email_verified, created_at, updated_at
        `;

        try {
            const result = await this.db.query(query, values);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error updating user:', error);
            throw new Error('Failed to update user');
        }
    }

    /**
     * Deactivate user account
     * @param {string} userId - User ID (UUID)
     * @returns {Promise<boolean>} Success status
     */
    async deactivateUser(userId) {
        const query = `
            UPDATE users 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        `;

        try {
            const result = await this.db.query(query, [userId]);
            return result.rowCount > 0;
        } catch (error) {
            console.error('Error deactivating user:', error);
            throw new Error('Failed to deactivate user');
        }
    }

    /**
     * Get users by role
     * @param {string} role - User role
     * @param {number} limit - Limit number of results
     * @param {number} offset - Offset for pagination
     * @returns {Promise<Array>} Array of users
     */
    async getUsersByRole(role, limit = 50, offset = 0) {
        const query = `
            SELECT id, username, email, phone_number, role, is_active, 
                   is_email_verified, created_at, updated_at, last_login
            FROM users 
            WHERE role = $1 AND is_active = true
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        `;

        try {
            const result = await this.db.query(query, [role, limit, offset]);
            return result.rows;
        } catch (error) {
            console.error('Error getting users by role:', error);
            throw new Error('Failed to get users by role');
        }
    }

    /**
     * Count total users
     * @returns {Promise<number>} Total user count
     */
    async getTotalUserCount() {
        const query = `SELECT COUNT(*) as total FROM users WHERE is_active = true`;

        try {
            const result = await this.db.query(query);
            return parseInt(result.rows[0].total);
        } catch (error) {
            console.error('Error getting user count:', error);
            throw new Error('Failed to get user count');
        }
    }
}