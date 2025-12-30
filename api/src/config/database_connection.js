// File: config/database_connection.js
// PostgreSQL database connection configuration

import pkg from 'pg';
import dotenv from 'dotenv';

dotenv.config(); // <-- Load variables from .env

const { Pool } = pkg;

export class DatabaseConnection {
    constructor() {
        if (!DatabaseConnection.instance) {
            // Validate required environment variables
            const requiredVars = ["DB_USER", "DB_HOST", "DB_NAME", "DB_PASSWORD", "DB_PORT"];
            requiredVars.forEach((v) => {
                if (!process.env[v]) {
                    console.warn(`⚠️  Warning: Environment variable ${v} is not set. Using default fallback.`);
                }
            });

            this.pool = new Pool({
                user: process.env.DB_USER || 'postgres',
                host: process.env.DB_HOST || 'localhost',
                database: process.env.DB_NAME || 'flutter_auth_app',
                password: process.env.DB_PASSWORD || 'password',
                port: process.env.DB_PORT ? parseInt(process.env.DB_PORT, 10) : 5432,
                max: 20, // Maximum number of clients in the pool
                idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
                connectionTimeoutMillis: 2000, // Return error after 2 seconds if connection could not be established
                statement_timeout: 30000, // Timeout for individual statements
                query_timeout: 30000, // Timeout for queries
                ssl: process.env.NODE_ENV === 'production'
                    ? { rejectUnauthorized: false }
                    : false
            });

            // Handle pool errors
            this.pool.on('error', (err) => {
                console.error('Unexpected error on idle PostgreSQL client:', err);
                process.exit(-1);
            });

            // Graceful shutdown
            process.on('SIGINT', async () => {
                console.log('Closing PostgreSQL connection pool...');
                await this.pool.end();
                process.exit(0);
            });

            process.on('SIGTERM', async () => {
                console.log('Closing PostgreSQL connection pool...');
                await this.pool.end();
                process.exit(0);
            });

            DatabaseConnection.instance = this;
        }

        return DatabaseConnection.instance;
    }

    static getInstance() {
        if (!DatabaseConnection.instance) {
            DatabaseConnection.instance = new DatabaseConnection();
        }
        return DatabaseConnection.instance;
    }

    async query(text, params = []) {
        const start = Date.now();
        try {
            const result = await this.pool.query(text, params);
            const duration = Date.now() - start;
            if (process.env.NODE_ENV === 'development' && duration > 1000) {
                console.warn(`Slow query detected (${duration}ms):`, text.substring(0, 100));
            }
            return result;
        } catch (error) {
            const duration = Date.now() - start;
            console.error('Database query error:', {
                error: error.message,
                query: text.substring(0, 100),
                params: params?.length || 0,
                duration
            });
            throw error;
        }
    }

    async transaction(callback) {
        const client = await this.pool.connect();
        try {
            await client.query('BEGIN');
            const result = await callback(client);
            await client.query('COMMIT');
            return result;
        } catch (error) {
            await client.query('ROLLBACK');
            throw error;
        } finally {
            client.release();
        }
    }

    async testConnection() {
        try {
            const result = await this.query('SELECT NOW() as current_time');
            console.log('Database connection successful:', result.rows[0].current_time);
            return true;
        } catch (error) {
            console.error('Database connection failed:', error.message);
            return false;
        }
    }

    getPoolStatus() {
        return {
            totalCount: this.pool.totalCount,
            idleCount: this.pool.idleCount,
            waitingCount: this.pool.waitingCount
        };
    }

    async closePool() {
        try {
            await this.pool.end();
            console.log('Database connection pool closed');
        } catch (error) {
            console.error('Error closing database pool:', error);
        }
    }

    async batchQuery(queries) {
        const promises = queries.map(query =>
            this.query(query.text, query.params)
        );
        try {
            return await Promise.all(promises);
        } catch (error) {
            console.error('Batch query error:', error);
            throw error;
        }
    }

    async preparedQuery(name, text, params = []) {
        const client = await this.pool.connect();
        try {
            await client.query(`PREPARE ${name} AS ${text}`);
            const result = await client.query(`EXECUTE ${name}`, params);
            await client.query(`DEALLOCATE ${name}`);
            return result;
        } catch (error) {
            console.error('Prepared query error:', error);
            throw error;
        } finally {
            client.release();
        }
    }

    async ensureDatabaseExists() {
        const dbName = process.env.DB_NAME || 'flutter_auth_app';
        try {
            const tempPool = new Pool({
                ...this.pool.options,
                database: 'postgres'
            });

            const result = await tempPool.query(
                'SELECT 1 FROM pg_database WHERE datname = $1',
                [dbName]
            );

            if (result.rows.length === 0) {
                console.log(`Creating database: ${dbName}`);
                await tempPool.query(`CREATE DATABASE ${dbName}`);
                console.log(`Database ${dbName} created successfully`);
            }

            await tempPool.end();
            return true;
        } catch (error) {
            console.error('Error ensuring database exists:', error);
            return false;
        }
    }
}
