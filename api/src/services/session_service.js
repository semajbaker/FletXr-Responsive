// File: services/session_service.js
// Session management service layer

import { DatabaseConnection } from '../config/database_connection.js';

export class SessionService {
    constructor() {
        this.db = DatabaseConnection.getInstance();
    }

    /**
     * Create new session
     * @param {Object} sessionData - Session data object
     * @returns {Promise<Object>} Created session
     */
    async createSession(sessionData) {
        const query = `
            INSERT INTO sessions (
                user_id, 
                session_token, 
                refresh_token, 
                expires_at, 
                ip_address, 
                user_agent, 
                is_active
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, user_id, session_token, refresh_token, expires_at, 
                     created_at, ip_address, user_agent, is_active
        `;
        
        const values = [
            sessionData.user_id,
            sessionData.session_token,
            sessionData.refresh_token,
            sessionData.expires_at,
            sessionData.ip_address,
            sessionData.user_agent,
            sessionData.is_active || true
        ];

        try {
            const result = await this.db.query(query, values);
            return result.rows[0];
        } catch (error) {
            console.error('Error creating session:', error);
            throw new Error('Failed to create session');
        }
    }

    /**
     * Find active session by session token
     * @param {string} sessionToken - Session token
     * @returns {Promise<Object|null>} Session object or null
     */
    async findActiveSessionByToken(sessionToken) {
        const query = `
            SELECT id, user_id, session_token, refresh_token, expires_at, 
                   created_at, updated_at, ip_address, user_agent, is_active
            FROM sessions 
            WHERE session_token = $1 
              AND is_active = true 
              AND expires_at > CURRENT_TIMESTAMP
        `;

        try {
            const result = await this.db.query(query, [sessionToken]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding session by token:', error);
            throw new Error('Failed to find session');
        }
    }

    /**
     * Find active session by refresh token
     * @param {string} refreshToken - Refresh token
     * @returns {Promise<Object|null>} Session object or null
     */
    async findActiveSessionByRefreshToken(refreshToken) {
        const query = `
            SELECT id, user_id, session_token, refresh_token, expires_at, 
                   created_at, updated_at, ip_address, user_agent, is_active
            FROM sessions 
            WHERE refresh_token = $1 
              AND is_active = true 
              AND expires_at > CURRENT_TIMESTAMP
        `;

        try {
            const result = await this.db.query(query, [refreshToken]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error finding session by refresh token:', error);
            throw new Error('Failed to find session');
        }
    }

    /**
     * Update session
     * @param {string} sessionId - Session ID (UUID)
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object|null>} Updated session object
     */
    async updateSession(sessionId, updateData) {
        const allowedFields = ['session_token', 'refresh_token', 'expires_at'];
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
        values.push(sessionId);

        const query = `
            UPDATE sessions 
            SET ${updates.join(', ')}
            WHERE id = $${paramIndex} AND is_active = true
            RETURNING id, user_id, session_token, refresh_token, expires_at, 
                     created_at, updated_at, ip_address, user_agent, is_active
        `;

        try {
            const result = await this.db.query(query, values);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error updating session:', error);
            throw new Error('Failed to update session');
        }
    }

    /**
     * Deactivate session by token
     * @param {string} sessionToken - Session token
     * @returns {Promise<boolean>} Success status
     */
    async deactivateSessionByToken(sessionToken) {
        const query = `
            UPDATE sessions 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE session_token = $1
        `;

        try {
            const result = await this.db.query(query, [sessionToken]);
            return result.rowCount > 0;
        } catch (error) {
            console.error('Error deactivating session:', error);
            throw new Error('Failed to deactivate session');
        }
    }

    /**
     * Deactivate all sessions for a user
     * @param {string} userId - User ID (UUID)
     * @returns {Promise<number>} Number of deactivated sessions
     */
    async deactivateAllUserSessions(userId) {
        const query = `
            UPDATE sessions 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1 AND is_active = true
        `;

        try {
            const result = await this.db.query(query, [userId]);
            return result.rowCount;
        } catch (error) {
            console.error('Error deactivating user sessions:', error);
            throw new Error('Failed to deactivate user sessions');
        }
    }

    /**
     * Get active sessions for a user
     * @param {string} userId - User ID (UUID)
     * @param {number} limit - Limit number of results
     * @returns {Promise<Array>} Array of active sessions
     */
    async getActiveUserSessions(userId, limit = 10) {
        const query = `
            SELECT id, session_token, expires_at, created_at, updated_at, 
                   ip_address, user_agent, is_active
            FROM sessions 
            WHERE user_id = $1 
              AND is_active = true 
              AND expires_at > CURRENT_TIMESTAMP
            ORDER BY created_at DESC
            LIMIT $2
        `;

        try {
            const result = await this.db.query(query, [userId, limit]);
            return result.rows;
        } catch (error) {
            console.error('Error getting user sessions:', error);
            throw new Error('Failed to get user sessions');
        }
    }

    /**
     * Clean up expired sessions
     * @returns {Promise<number>} Number of cleaned sessions
     */
    async cleanupExpiredSessions() {
        const query = `
            DELETE FROM sessions 
            WHERE expires_at < CURRENT_TIMESTAMP 
               OR (is_active = false AND updated_at < CURRENT_TIMESTAMP - INTERVAL '30 days')
        `;

        try {
            const result = await this.db.query(query);
            console.log(`Cleaned up ${result.rowCount} expired sessions`);
            return result.rowCount;
        } catch (error) {
            console.error('Error cleaning up expired sessions:', error);
            throw new Error('Failed to cleanup expired sessions');
        }
    }

    /**
     * Get session statistics
     * @returns {Promise<Object>} Session statistics
     */
    async getSessionStatistics() {
        const query = `
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
                COUNT(*) FILTER (WHERE expires_at > CURRENT_TIMESTAMP) as valid_sessions,
                COUNT(DISTINCT user_id) as unique_users
            FROM sessions
        `;

        try {
            const result = await this.db.query(query);
            return result.rows[0];
        } catch (error) {
            console.error('Error getting session statistics:', error);
            throw new Error('Failed to get session statistics');
        }
    }

    /**
     * Validate session and get user info
     * @param {string} sessionToken - Session token
     * @returns {Promise<Object|null>} User and session info or null
     */
    async validateSessionAndGetUser(sessionToken) {
        const query = `
            SELECT 
                s.id as session_id,
                s.user_id,
                s.expires_at,
                s.ip_address,
                s.user_agent,
                u.username,
                u.email,
                u.role,
                u.is_active as user_active,
                u.is_email_verified
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = $1 
              AND s.is_active = true 
              AND s.expires_at > CURRENT_TIMESTAMP
              AND u.is_active = true
        `;

        try {
            const result = await this.db.query(query, [sessionToken]);
            return result.rows[0] || null;
        } catch (error) {
            console.error('Error validating session:', error);
            throw new Error('Failed to validate session');
        }
    }
}