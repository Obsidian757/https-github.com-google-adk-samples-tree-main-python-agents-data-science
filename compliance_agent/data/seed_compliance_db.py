"""Seed script to initialize the DuckDB compliance database.

Creates tables for AI inventory, licenses, compliance frameworks,
gap assessments, and usage tracking. Loads realistic sample data
modeled after the TEKsystems / federal contractor use case.
"""

import duckdb

DB_PATH = "compliance.duckdb"


def seed() -> None:
    con = duckdb.connect(DB_PATH)

    # -- AI Systems Inventory --------------------------------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS ai_systems (
            system_id       VARCHAR PRIMARY KEY,
            system_name     VARCHAR NOT NULL,
            vendor          VARCHAR NOT NULL,
            description     VARCHAR,
            deployment_type VARCHAR,          -- 'saas', 'on-prem', 'hybrid'
            agency          VARCHAR,          -- 'DOD', 'HHS', 'DHS', 'VA', etc.
            data_classification VARCHAR,      -- 'public', 'cui', 'phi', 'pii'
            hipaa_relevant  BOOLEAN DEFAULT FALSE,
            owner           VARCHAR,
            status          VARCHAR DEFAULT 'active'  -- 'active','pilot','retired'
        )
    """)

    con.execute("""
        INSERT OR REPLACE INTO ai_systems VALUES
        ('SYS-001','ChatGPT Enterprise','OpenAI','General-purpose LLM for staff productivity','saas','DHS','cui',FALSE,'IT Division','active'),
        ('SYS-002','ChatGPT Enterprise - Clinical','OpenAI','LLM for clinical note summarization','saas','HHS','phi',TRUE,'Clinical Ops','pilot'),
        ('SYS-003','Microsoft Copilot','Microsoft','O365-integrated AI assistant','saas','DHS','cui',FALSE,'IT Division','active'),
        ('SYS-004','Palantir AIP','Palantir','Threat analysis and intelligence','on-prem','DOD','classified',FALSE,'Intel Division','active'),
        ('SYS-005','Amazon Bedrock - Claims','AWS','Automated claims processing','hybrid','VA','pii',TRUE,'Benefits Processing','active'),
        ('SYS-006','Google Vertex AI','Google','ML model training and serving','saas','DHS','cui',FALSE,'Data Science Team','pilot'),
        ('SYS-007','UiPath AI Center','UiPath','Intelligent document processing','on-prem','VA','phi',TRUE,'Records Management','active'),
        ('SYS-008','Salesforce Einstein','Salesforce','CRM predictive analytics','saas','HHS','pii',FALSE,'Outreach Division','active')
    """)

    # -- License Inventory -----------------------------------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            license_id      VARCHAR PRIMARY KEY,
            system_id       VARCHAR REFERENCES ai_systems(system_id),
            license_type    VARCHAR,          -- 'enterprise', 'team', 'individual'
            total_seats     INTEGER NOT NULL,
            assigned_seats  INTEGER DEFAULT 0,
            active_seats    INTEGER DEFAULT 0,  -- used in last 30 days
            cost_per_seat   DECIMAL(10,2),
            billing_cycle   VARCHAR DEFAULT 'monthly',
            renewal_date    DATE,
            hipaa_tier      BOOLEAN DEFAULT FALSE,  -- TRUE = HIPAA-safe config
            department      VARCHAR,
            o365_restricted BOOLEAN DEFAULT FALSE   -- limited to specific O365 users
        )
    """)

    con.execute("""
        INSERT OR REPLACE INTO licenses VALUES
        ('LIC-001','SYS-001','enterprise',6000,4200,3100,30.00,'monthly','2026-06-01',FALSE,'All Departments',FALSE),
        ('LIC-002','SYS-002','enterprise',500,320,280,45.00,'monthly','2026-06-01',TRUE,'Clinical Ops',TRUE),
        ('LIC-003','SYS-003','enterprise',6000,5800,4900,30.00,'monthly','2026-09-01',FALSE,'All Departments',FALSE),
        ('LIC-004','SYS-004','enterprise',150,150,140,250.00,'annual','2027-01-15',FALSE,'Intel Division',TRUE),
        ('LIC-005','SYS-005','team',200,180,165,75.00,'monthly','2026-08-01',TRUE,'Benefits Processing',TRUE),
        ('LIC-006','SYS-006','team',50,35,22,0.00,'usage-based','2026-12-01',FALSE,'Data Science Team',FALSE),
        ('LIC-007','SYS-007','enterprise',100,95,88,120.00,'annual','2026-11-01',TRUE,'Records Management',TRUE),
        ('LIC-008','SYS-008','enterprise',300,290,210,50.00,'monthly','2026-07-15',FALSE,'Outreach Division',FALSE)
    """)

    # -- Compliance Frameworks -------------------------------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS compliance_frameworks (
            framework_id    VARCHAR PRIMARY KEY,
            name            VARCHAR NOT NULL,
            short_name      VARCHAR,
            issuing_body    VARCHAR,
            effective_date  DATE,
            compliance_deadline DATE,
            description     VARCHAR,
            applies_to      VARCHAR   -- 'all', 'dod', 'hipaa', 'cfo-act'
        )
    """)

    con.execute("""
        INSERT OR REPLACE INTO compliance_frameworks VALUES
        ('FW-001','OMB M-25-21','M-25-21','OMB','2025-04-03','2026-06-30','Accelerating Federal Use of AI through Innovation, Governance, and Public Trust','all'),
        ('FW-002','OMB M-25-22','M-25-22','OMB','2025-04-03','2026-06-30','Driving Efficient Acquisition of Artificial Intelligence in Government','all'),
        ('FW-003','NIST AI Risk Management Framework','AI RMF 1.0','NIST','2023-01-26',NULL,'Voluntary framework for managing AI risks','all'),
        ('FW-004','Executive Order 14110','EO 14110','White House','2023-10-30','2026-03-01','Safe, Secure, and Trustworthy AI','all'),
        ('FW-005','HIPAA Security Rule - AI Addendum','HIPAA-AI','HHS','2025-01-01','2026-03-31','HIPAA requirements for AI systems processing PHI','hipaa'),
        ('FW-006','DHS AI Strategy 2024-2026','DHS-AI','DHS','2024-03-18','2026-12-31','DHS-specific AI governance and deployment strategy','dod'),
        ('FW-007','DFARS 252.204-7012','DFARS-7012','DOD','2017-12-31',NULL,'Safeguarding Covered Defense Information - AI clause','dod')
    """)

    # -- Gap Assessments -------------------------------------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS gap_assessments (
            assessment_id   VARCHAR PRIMARY KEY,
            system_id       VARCHAR REFERENCES ai_systems(system_id),
            framework_id    VARCHAR REFERENCES compliance_frameworks(framework_id),
            requirement     VARCHAR NOT NULL,
            status          VARCHAR DEFAULT 'gap',  -- 'compliant','partial','gap','not-applicable'
            severity        VARCHAR DEFAULT 'medium',-- 'critical','high','medium','low'
            remediation     VARCHAR,
            estimated_effort_days INTEGER,
            assigned_to     VARCHAR,
            due_date        DATE,
            assessed_date   DATE
        )
    """)

    con.execute("""
        INSERT OR REPLACE INTO gap_assessments VALUES
        ('GA-001','SYS-001','FW-001','AI use case inventory registered','compliant','low',NULL,0,'IT Division','2026-06-30','2026-01-15'),
        ('GA-002','SYS-001','FW-001','Risk assessment completed','partial','high','Complete NIST AI RMF risk assessment for ChatGPT Enterprise',15,'Risk Team','2026-03-15','2026-01-15'),
        ('GA-003','SYS-001','FW-003','AI RMF GOVERN function documented','gap','high','Document governance structure, roles, and responsibilities',20,'Compliance','2026-04-01','2026-01-15'),
        ('GA-004','SYS-001','FW-004','Model transparency reporting','gap','critical','Implement model card and transparency documentation',10,'AI Ethics','2026-03-01','2026-01-15'),
        ('GA-005','SYS-002','FW-005','PHI data handling controls','partial','critical','Implement BAA-compliant data handling; disable training on PHI',5,'Clinical Ops','2026-03-31','2026-01-20'),
        ('GA-006','SYS-002','FW-005','HIPAA access controls','gap','critical','Implement role-based access; audit logging for all PHI queries',12,'Security','2026-03-31','2026-01-20'),
        ('GA-007','SYS-003','FW-001','AI use case inventory registered','compliant','low',NULL,0,'IT Division','2026-06-30','2026-01-15'),
        ('GA-008','SYS-003','FW-002','Procurement compliance documented','partial','medium','Document AI acquisition justification per M-25-22',8,'Procurement','2026-06-30','2026-01-18'),
        ('GA-009','SYS-004','FW-007','DFARS CUI handling for AI','compliant','low',NULL,0,'Intel Division','2026-06-30','2026-01-10'),
        ('GA-010','SYS-004','FW-006','DHS AI strategy alignment','partial','medium','Map Palantir capabilities to DHS AI strategy objectives',10,'Strategy','2026-06-30','2026-01-10'),
        ('GA-011','SYS-005','FW-005','PHI/PII segregation in AI pipeline','gap','critical','Implement data classification and segregation controls',18,'Engineering','2026-03-31','2026-01-22'),
        ('GA-012','SYS-005','FW-001','Continuous monitoring plan','gap','high','Establish ongoing performance and bias monitoring',14,'Data Science Team','2026-06-30','2026-01-22'),
        ('GA-013','SYS-001','FW-002','Credit usage governance policy','gap','high','Implement per-department credit limits and monitoring in Global Admin Console',7,'IT Division','2026-04-01','2026-02-01'),
        ('GA-014','SYS-001','FW-001','License reclamation process','gap','medium','Define process for identifying and reclaiming unused licenses monthly',5,'IT Division','2026-04-15','2026-02-01'),
        ('GA-015','SYS-003','FW-001','O365 user restriction policy','partial','medium','Limit Copilot access to approved user groups; exclude HIPAA data users',8,'Security','2026-05-01','2026-02-01'),
        ('GA-016','SYS-006','FW-003','AI RMF MAP function completed','gap','medium','Complete use-case mapping and stakeholder analysis',12,'Data Science Team','2026-06-30','2026-01-25')
    """)

    # -- Usage Tracking --------------------------------------------------------
    con.execute("""
        CREATE TABLE IF NOT EXISTS usage_tracking (
            tracking_id     VARCHAR PRIMARY KEY,
            license_id      VARCHAR REFERENCES licenses(license_id),
            month           DATE NOT NULL,
            active_users    INTEGER,
            total_queries   INTEGER,
            avg_queries_per_user DECIMAL(10,2),
            credit_consumed DECIMAL(12,2),
            credit_limit    DECIMAL(12,2),
            flagged_queries INTEGER DEFAULT 0,  -- queries touching restricted data
            department      VARCHAR
        )
    """)

    con.execute("""
        INSERT OR REPLACE INTO usage_tracking VALUES
        ('UT-001','LIC-001','2025-10-01',2800,145000,51.79,87000.00,180000.00,12,'All Departments'),
        ('UT-002','LIC-001','2025-11-01',3000,162000,54.00,97200.00,180000.00,8,'All Departments'),
        ('UT-003','LIC-001','2025-12-01',3100,178000,57.42,106800.00,180000.00,15,'All Departments'),
        ('UT-004','LIC-001','2026-01-01',3100,185000,59.68,111000.00,180000.00,22,'All Departments'),
        ('UT-005','LIC-002','2025-10-01',240,18000,75.00,10800.00,22500.00,3,'Clinical Ops'),
        ('UT-006','LIC-002','2025-11-01',260,21000,80.77,12600.00,22500.00,1,'Clinical Ops'),
        ('UT-007','LIC-002','2025-12-01',270,23500,87.04,14100.00,22500.00,5,'Clinical Ops'),
        ('UT-008','LIC-002','2026-01-01',280,26000,92.86,15600.00,22500.00,7,'Clinical Ops'),
        ('UT-009','LIC-003','2025-10-01',4500,210000,46.67,135000.00,180000.00,4,'All Departments'),
        ('UT-010','LIC-003','2025-11-01',4700,228000,48.51,136800.00,180000.00,2,'All Departments'),
        ('UT-011','LIC-003','2025-12-01',4850,245000,50.52,147000.00,180000.00,6,'All Departments'),
        ('UT-012','LIC-003','2026-01-01',4900,260000,53.06,156000.00,180000.00,9,'All Departments'),
        ('UT-013','LIC-005','2025-10-01',150,9500,63.33,11250.00,15000.00,2,'Benefits Processing'),
        ('UT-014','LIC-005','2025-11-01',158,10800,68.35,13500.00,15000.00,0,'Benefits Processing'),
        ('UT-015','LIC-005','2025-12-01',162,11500,70.99,14375.00,15000.00,4,'Benefits Processing'),
        ('UT-016','LIC-005','2026-01-01',165,12200,73.94,15250.00,15000.00,6,'Benefits Processing'),
        ('UT-017','LIC-008','2025-10-01',180,8200,45.56,9000.00,15000.00,0,'Outreach Division'),
        ('UT-018','LIC-008','2025-11-01',195,9100,46.67,10150.00,15000.00,1,'Outreach Division'),
        ('UT-019','LIC-008','2025-12-01',200,9800,49.00,10900.00,15000.00,0,'Outreach Division'),
        ('UT-020','LIC-008','2026-01-01',210,10500,50.00,11500.00,15000.00,2,'Outreach Division')
    """)

    con.close()
    print(f"Compliance database seeded at {DB_PATH}")


if __name__ == "__main__":
    seed()
