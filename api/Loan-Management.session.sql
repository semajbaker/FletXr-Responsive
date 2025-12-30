-- Database schema for Loan Management System

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- =======================
-- USERS & AUTHENTICATION
-- =======================

-- Users table with updated role-based access for LMS
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'customer' CHECK (role IN ('superuser', 'admin', 'loan_officer', 'collection_officer', 'auditor', 'customer')),
    is_active BOOLEAN DEFAULT true,
    is_email_verified BOOLEAN DEFAULT false,
    email_verification_token VARCHAR(512),
    password_reset_token VARCHAR(512),
    password_reset_expires TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_by UUID REFERENCES users(id),
    permissions JSONB DEFAULT '{}' -- Additional custom permissions per user
);

-- Sessions table for authentication management
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    refresh_token VARCHAR(512) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true
);

-- =======================
-- CORE BUSINESS ENTITIES
-- =======================

-- Borrower categories and products
CREATE TABLE borrower_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL, -- Student, Employed, Trader
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loan products with pricing rules
CREATE TABLE loan_products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    interest_type VARCHAR(50) DEFAULT 'flat_monthly' CHECK (interest_type IN ('flat_monthly', 'reducing_balance')),
    interest_rate DECIMAL(5,4) NOT NULL, -- e.g., 0.3000 for 30%
    max_amount DECIMAL(12,2) NOT NULL,
    default_term_days INTEGER NOT NULL,
    grace_days INTEGER DEFAULT 3,
    penalty_type VARCHAR(50) DEFAULT 'fixed' CHECK (penalty_type IN ('fixed', 'percentage')),
    penalty_value DECIMAL(10,2) NOT NULL,
    min_credit_score INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Borrowers with KYC information
CREATE TABLE borrowers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_code VARCHAR(50) UNIQUE NOT NULL, -- Auto-generated: NZM-BOR-001
    full_name VARCHAR(255) NOT NULL,
    phone_primary VARCHAR(20) NOT NULL,
    phone_whatsapp VARCHAR(20),
    email VARCHAR(255),
    id_number VARCHAR(50) UNIQUE NOT NULL,
    date_of_birth DATE,
    address TEXT NOT NULL,
    category_id UUID NOT NULL REFERENCES borrower_categories(id),
    employer_or_school VARCHAR(255),
    referrer VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'blacklisted')),
    credit_score INTEGER DEFAULT 50, -- 0-100 scale
    risk_tier VARCHAR(20) DEFAULT 'standard' CHECK (risk_tier IN ('low', 'standard', 'high')),
    kyc_status VARCHAR(50) DEFAULT 'incomplete' CHECK (kyc_status IN ('incomplete', 'pending', 'approved', 'rejected')),
    kyc_approved_at TIMESTAMP,
    kyc_approved_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- KYC Documents storage
CREATE TABLE borrower_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    borrower_id UUID NOT NULL REFERENCES borrowers(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL, -- ID_COPY, PROOF_OF_RESIDENCE, BANK_STATEMENT, PAYSLIP, OTHER
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    is_verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_by UUID REFERENCES users(id)
);

-- Loans management
CREATE TABLE loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_code VARCHAR(50) UNIQUE NOT NULL, -- Auto-generated: NZM-LOAN-001
    borrower_id UUID NOT NULL REFERENCES borrowers(id),
    product_id UUID NOT NULL REFERENCES loan_products(id),
    principal_amount DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,4) NOT NULL, -- Snapshot from product at time of creation
    interest_amount DECIMAL(12,2) NOT NULL,
    total_due_amount DECIMAL(12,2) NOT NULL,
    term_days INTEGER NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    disbursement_method VARCHAR(50) CHECK (disbursement_method IN ('cash', 'bank_transfer', 'mobile_money')),
    disbursement_reference VARCHAR(255),
    disbursed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'disbursed', 'active', 'overdue', 'paid', 'written_off')),
    agreement_file_path TEXT,
    internal_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP
);

-- Loan repayments
CREATE TABLE repayments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_code VARCHAR(50) UNIQUE NOT NULL, -- Auto-generated: NZM-PAY-001
    loan_id UUID NOT NULL REFERENCES loans(id),
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(12,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('cash', 'bank_transfer', 'mobile_money')),
    reference_number VARCHAR(255),
    payer_name VARCHAR(255),
    allocation_penalty DECIMAL(12,2) DEFAULT 0,
    allocation_interest DECIMAL(12,2) DEFAULT 0,
    allocation_principal DECIMAL(12,2) DEFAULT 0,
    receipt_file_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Penalties applied to loans
CREATE TABLE penalties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loans(id),
    penalty_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    penalty_type VARCHAR(100) NOT NULL,
    rule_description TEXT,
    is_waived BOOLEAN DEFAULT false,
    waived_by UUID REFERENCES users(id),
    waived_at TIMESTAMP,
    waiver_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================
-- VAULT SYSTEM (MONEY MANAGEMENT)
-- =======================

-- Main business vault accounts
CREATE TABLE vault_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_name VARCHAR(255) NOT NULL UNIQUE,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('cash', 'bank', 'mobile_money', 'operating_expense', 'loan_fund')),
    account_number VARCHAR(100),
    bank_name VARCHAR(255),
    current_balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- All financial transactions (double-entry bookkeeping)
CREATE TABLE vault_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_code VARCHAR(50) UNIQUE NOT NULL, -- Auto-generated: NZM-TXN-001
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL CHECK (transaction_type IN (
        'loan_disbursement', 'loan_repayment', 'penalty_collection', 
        'operating_expense', 'capital_injection', 'bank_deposit', 
        'bank_withdrawal', 'momo_transfer', 'cash_deposit', 'cash_withdrawal'
    )),
    description TEXT NOT NULL,
    reference_number VARCHAR(255),
    related_loan_id UUID REFERENCES loans(id),
    related_repayment_id UUID REFERENCES repayments(id),
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Transaction entries (debit/credit entries for each transaction)
CREATE TABLE vault_transaction_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL REFERENCES vault_transactions(id) ON DELETE CASCADE,
    vault_account_id UUID NOT NULL REFERENCES vault_accounts(id),
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL, -- Account balance after this entry
    description TEXT
);

-- =======================
-- COMMUNICATIONS & REMINDERS
-- =======================

-- Message templates for reminders
CREATE TABLE message_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_key VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'reminder_t_minus_3'
    template_name VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('sms', 'whatsapp', 'email')),
    subject VARCHAR(255), -- For email
    message_body TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminder queue and history
CREATE TABLE reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loans(id),
    borrower_id UUID NOT NULL REFERENCES borrowers(id),
    template_id UUID NOT NULL REFERENCES message_templates(id),
    channel VARCHAR(50) NOT NULL,
    recipient VARCHAR(255) NOT NULL, -- Phone/email
    message_content TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'sent', 'failed', 'cancelled')),
    delivery_status VARCHAR(50), -- delivered, read, failed
    response TEXT, -- Any response from recipient
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Collections activities and notes
CREATE TABLE collection_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID NOT NULL REFERENCES loans(id),
    borrower_id UUID NOT NULL REFERENCES borrowers(id),
    activity_type VARCHAR(50) NOT NULL CHECK (activity_type IN ('call', 'visit', 'sms', 'email', 'promise_to_pay', 'dispute')),
    activity_date DATE NOT NULL,
    officer_id UUID NOT NULL REFERENCES users(id),
    outcome VARCHAR(100),
    promise_to_pay_date DATE,
    amount_promised DECIMAL(12,2),
    notes TEXT,
    follow_up_date DATE,
    is_dispute BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================
-- REPORTING & AUDIT
-- =======================

-- Comprehensive audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    entity_type VARCHAR(100) NOT NULL, -- borrowers, loans, repayments, etc.
    entity_id UUID,
    action VARCHAR(100) NOT NULL, -- create, update, delete, approve, disburse, etc.
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System settings
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    data_type VARCHAR(50) DEFAULT 'string' CHECK (data_type IN ('string', 'number', 'boolean', 'json')),
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID REFERENCES users(id)
);

-- =======================
-- INDEXES FOR PERFORMANCE
-- =======================

-- Users and sessions indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(session_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- Business entity indexes
CREATE INDEX idx_borrowers_phone ON borrowers(phone_primary);
CREATE INDEX idx_borrowers_id_number ON borrowers(id_number);
CREATE INDEX idx_borrowers_status ON borrowers(status);
CREATE INDEX idx_borrowers_category ON borrowers(category_id);
CREATE INDEX idx_borrowers_code ON borrowers(borrower_code);

CREATE INDEX idx_loans_borrower ON loans(borrower_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_loans_due_date ON loans(due_date);
CREATE INDEX idx_loans_issue_date ON loans(issue_date);
CREATE INDEX idx_loans_code ON loans(loan_code);

CREATE INDEX idx_repayments_loan ON repayments(loan_id);
CREATE INDEX idx_repayments_date ON repayments(payment_date);
CREATE INDEX idx_repayments_code ON repayments(payment_code);

-- Vault indexes
CREATE INDEX idx_vault_transactions_date ON vault_transactions(transaction_date);
CREATE INDEX idx_vault_transactions_type ON vault_transactions(transaction_type);
CREATE INDEX idx_vault_transactions_loan ON vault_transactions(related_loan_id);
CREATE INDEX idx_vault_transaction_entries_account ON vault_transaction_entries(vault_account_id);

-- Collections and reminders indexes
CREATE INDEX idx_reminders_loan ON reminders(loan_id);
CREATE INDEX idx_reminders_scheduled ON reminders(scheduled_at);
CREATE INDEX idx_reminders_status ON reminders(status);
CREATE INDEX idx_collection_activities_loan ON collection_activities(loan_id);
CREATE INDEX idx_collection_activities_officer ON collection_activities(officer_id);

-- Audit indexes
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =======================
-- FUNCTIONS AND TRIGGERS
-- =======================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at 
    BEFORE UPDATE ON sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loan_products_updated_at 
    BEFORE UPDATE ON loan_products 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_borrowers_updated_at 
    BEFORE UPDATE ON borrowers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_loans_updated_at 
    BEFORE UPDATE ON loans 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vault_accounts_updated_at 
    BEFORE UPDATE ON vault_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_message_templates_updated_at 
    BEFORE UPDATE ON message_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at 
    BEFORE UPDATE ON system_settings 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update vault account balances
CREATE OR REPLACE FUNCTION update_vault_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the vault account balance
    UPDATE vault_accounts 
    SET current_balance = NEW.balance_after,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.vault_account_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update vault balances when entries are created
CREATE TRIGGER update_vault_balance_trigger
    AFTER INSERT ON vault_transaction_entries
    FOR EACH ROW EXECUTE FUNCTION update_vault_balance();

-- =======================
-- INITIAL DATA POPULATION
-- =======================

-- Insert default borrower categories
INSERT INTO borrower_categories (name, description) VALUES
('Student', 'University and college students'),
('Employed', 'Formally employed individuals with regular salary'),
('Trader', 'Small business owners and traders');

-- Insert default loan products
INSERT INTO loan_products (name, description, interest_rate, max_amount, default_term_days, grace_days, penalty_type, penalty_value) VALUES
('Student Quick Loan', '30-day quick loan for students', 0.3000, 500.00, 30, 3, 'fixed', 50.00),
('Employee Standard', 'Standard loan for employed individuals', 0.2500, 2000.00, 60, 3, 'percentage', 0.05),
('Trader Business Loan', 'Business loan for traders', 0.3500, 5000.00, 90, 5, 'fixed', 100.00);

-- Insert default vault accounts
INSERT INTO vault_accounts (account_name, account_type, description) VALUES
('Main Cash Vault', 'cash', 'Primary cash holding account'),
('Business Bank Account', 'bank', 'Main business bank account'),
('MTN Mobile Money', 'mobile_money', 'MTN MoMo business account'),
('Loan Fund', 'loan_fund', 'Dedicated fund for loan disbursements'),
('Operating Expenses', 'operating_expense', 'General operating expenses account');

-- Insert default message templates
INSERT INTO message_templates (template_key, template_name, channel, message_body) VALUES
('reminder_t_minus_3', '3 Days Before Due', 'sms', 'Hi {borrower_name}, friendly reminder your loan of E{total_due} is due on {due_date}. Please plan your payment. Ref: {loan_code}. --- Loan QuickFinance'),
('reminder_t_minus_1', '1 Day Before Due', 'sms', 'Reminder: E{total_due} due tomorrow ({due_date}). Pay via Bank/MoMo. Ref {loan_code}. Reply if you need help.'),
('reminder_due_today', 'Due Today', 'sms', 'Due today: E{total_due}. Please pay to avoid late fees. Ref {loan_code}. Thank you.'),
('reminder_overdue_3', '3 Days Overdue', 'sms', 'Your loan is 3 days overdue. Outstanding: E{outstanding}. Late fee may apply after {grace_days} days. Please pay immediately.'),
('reminder_overdue_7', '7 Days Overdue - Final', 'sms', 'Final notice before escalation: E{outstanding} overdue. Settle today or contact us to avoid legal action.');

-- Insert default system settings
INSERT INTO system_settings (setting_key, setting_value, data_type, description) VALUES
('company_name', 'Loan Investments', 'string', 'Legal company name'),
('trading_as', 'Loan QuickFinance', 'string', 'Trading as name'),
('currency', 'SZL', 'string', 'Base currency'),
('date_format', 'DD/MM/YYYY', 'string', 'System date format'),
('auto_send_reminders', 'true', 'boolean', 'Automatically send payment reminders'),
('max_loan_limit_new_customer', '500', 'number', 'Maximum loan amount for new customers');

-- Create superuser with proper bcrypt hash
-- Password: Password123!
-- Bcrypt hash generated with cost factor 12
INSERT INTO users (
    username, 
    email, 
    role, 
    password_hash, 
    is_active, 
    is_email_verified,
    created_at
) VALUES (
    'superuser', 
    'admin@example.com', 
    'superuser', 
    crypt('Password123!', gen_salt('bf', 12)), 
    true, 
    true,
    CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'System users with role-based access control';
COMMENT ON TABLE borrowers IS 'Customer/borrower information with KYC details';
COMMENT ON TABLE loans IS 'Loan records with terms and status tracking';
COMMENT ON TABLE vault_accounts IS 'Business money accounts (cash, bank, mobile money)';
COMMENT ON TABLE vault_transactions IS 'All financial transactions with double-entry bookkeeping';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for all system activities';