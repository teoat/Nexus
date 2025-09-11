#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Database Migration - Reconciliation & Human Judgment System
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_reconciliation'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade database schema for reconciliation system"""
    
    # Create reconciliation_jobs table
    op.create_table('reconciliation_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', 'requires_human_judgment', 'escalated', name='reconciliationstatus'), nullable=True),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('target_system', sa.String(length=100), nullable=False),
        sa.Column('data_type', sa.String(length=100), nullable=False),
        sa.Column('matching_criteria', sa.JSON(), nullable=True),
        sa.Column('tolerance_threshold', sa.Float(), nullable=True),
        sa.Column('total_records', sa.Integer(), nullable=True),
        sa.Column('matched_records', sa.Integer(), nullable=True),
        sa.Column('unmatched_records', sa.Integer(), nullable=True),
        sa.Column('discrepancy_count', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reconciliation_discrepancies table
    op.create_table('reconciliation_discrepancies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discrepancy_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source_record_id', sa.String(length=255), nullable=True),
        sa.Column('target_record_id', sa.String(length=255), nullable=True),
        sa.Column('source_data', sa.JSON(), nullable=True),
        sa.Column('target_data', sa.JSON(), nullable=True),
        sa.Column('difference_details', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', 'requires_human_judgment', 'escalated', name='reconciliationstatus'), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['reconciliation_jobs.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create human_judgments table
    op.create_table('human_judgments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discrepancy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('judgment_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_review', 'approved', 'rejected', 'escalated', name='judgmentstatus'), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('suggested_action', sa.Text(), nullable=True),
        sa.Column('decision', sa.String(length=100), nullable=True),
        sa.Column('decision_reasoning', sa.Text(), nullable=True),
        sa.Column('decision_confidence', sa.Float(), nullable=True),
        sa.Column('alternative_solution', sa.Text(), nullable=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('escalated_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['reconciliation_jobs.id'], ),
        sa.ForeignKeyConstraint(['discrepancy_id'], ['reconciliation_discrepancies.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['escalated_to'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create evidence table
    op.create_table('evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('discrepancy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('judgment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('evidence_type', sa.Enum('transaction_log', 'audit_trail', 'system_log', 'user_action', 'api_call', 'database_change', 'file_upload', 'email', 'document', name='evidencetype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('source_system', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['reconciliation_jobs.id'], ),
        sa.ForeignKeyConstraint(['discrepancy_id'], ['reconciliation_discrepancies.id'], ),
        sa.ForeignKeyConstraint(['judgment_id'], ['human_judgments.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reconciliation_rules table
    op.create_table('reconciliation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_system', sa.String(length=100), nullable=False),
        sa.Column('target_system', sa.String(length=100), nullable=False),
        sa.Column('data_type', sa.String(length=100), nullable=False),
        sa.Column('matching_fields', sa.JSON(), nullable=True),
        sa.Column('matching_algorithm', sa.String(length=100), nullable=True),
        sa.Column('tolerance_settings', sa.JSON(), nullable=True),
        sa.Column('auto_resolve_threshold', sa.Float(), nullable=True),
        sa.Column('escalation_threshold', sa.Float(), nullable=True),
        sa.Column('rejection_threshold', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reconciliation_audit_logs table
    op.create_table('reconciliation_audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('discrepancy_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('judgment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('performed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['reconciliation_jobs.id'], ),
        sa.ForeignKeyConstraint(['discrepancy_id'], ['reconciliation_discrepancies.id'], ),
        sa.ForeignKeyConstraint(['judgment_id'], ['human_judgments.id'], ),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('ix_reconciliation_jobs_status', 'reconciliation_jobs', ['status'])
    op.create_index('ix_reconciliation_jobs_created_by', 'reconciliation_jobs', ['created_by'])
    op.create_index('ix_reconciliation_jobs_source_system', 'reconciliation_jobs', ['source_system'])
    op.create_index('ix_reconciliation_jobs_target_system', 'reconciliation_jobs', ['target_system'])
    
    op.create_index('ix_reconciliation_discrepancies_job_id', 'reconciliation_discrepancies', ['job_id'])
    op.create_index('ix_reconciliation_discrepancies_severity', 'reconciliation_discrepancies', ['severity'])
    op.create_index('ix_reconciliation_discrepancies_status', 'reconciliation_discrepancies', ['status'])
    
    op.create_index('ix_human_judgments_job_id', 'human_judgments', ['job_id'])
    op.create_index('ix_human_judgments_status', 'human_judgments', ['status'])
    op.create_index('ix_human_judgments_priority', 'human_judgments', ['priority'])
    op.create_index('ix_human_judgments_assigned_to', 'human_judgments', ['assigned_to'])
    
    op.create_index('ix_evidence_job_id', 'evidence', ['job_id'])
    op.create_index('ix_evidence_evidence_type', 'evidence', ['evidence_type'])
    op.create_index('ix_evidence_created_by', 'evidence', ['created_by'])
    
    op.create_index('ix_reconciliation_rules_source_system', 'reconciliation_rules', ['source_system'])
    op.create_index('ix_reconciliation_rules_target_system', 'reconciliation_rules', ['target_system'])
    op.create_index('ix_reconciliation_rules_is_active', 'reconciliation_rules', ['is_active'])
    
    op.create_index('ix_reconciliation_audit_logs_job_id', 'reconciliation_audit_logs', ['job_id'])
    op.create_index('ix_reconciliation_audit_logs_entity_type', 'reconciliation_audit_logs', ['entity_type'])
    op.create_index('ix_reconciliation_audit_logs_performed_by', 'reconciliation_audit_logs', ['performed_by'])
    op.create_index('ix_reconciliation_audit_logs_performed_at', 'reconciliation_audit_logs', ['performed_at'])

def downgrade():
    """Downgrade database schema"""
    
    # Drop indexes
    op.drop_index('ix_reconciliation_audit_logs_performed_at', 'reconciliation_audit_logs')
    op.drop_index('ix_reconciliation_audit_logs_performed_by', 'reconciliation_audit_logs')
    op.drop_index('ix_reconciliation_audit_logs_entity_type', 'reconciliation_audit_logs')
    op.drop_index('ix_reconciliation_audit_logs_job_id', 'reconciliation_audit_logs')
    
    op.drop_index('ix_reconciliation_rules_is_active', 'reconciliation_rules')
    op.drop_index('ix_reconciliation_rules_target_system', 'reconciliation_rules')
    op.drop_index('ix_reconciliation_rules_source_system', 'reconciliation_rules')
    
    op.drop_index('ix_evidence_created_by', 'evidence')
    op.drop_index('ix_evidence_evidence_type', 'evidence')
    op.drop_index('ix_evidence_job_id', 'evidence')
    
    op.drop_index('ix_human_judgments_assigned_to', 'human_judgments')
    op.drop_index('ix_human_judgments_priority', 'human_judgments')
    op.drop_index('ix_human_judgments_status', 'human_judgments')
    op.drop_index('ix_human_judgments_job_id', 'human_judgments')
    
    op.drop_index('ix_reconciliation_discrepancies_status', 'reconciliation_discrepancies')
    op.drop_index('ix_reconciliation_discrepancies_severity', 'reconciliation_discrepancies')
    op.drop_index('ix_reconciliation_discrepancies_job_id', 'reconciliation_discrepancies')
    
    op.drop_index('ix_reconciliation_jobs_target_system', 'reconciliation_jobs')
    op.drop_index('ix_reconciliation_jobs_source_system', 'reconciliation_jobs')
    op.drop_index('ix_reconciliation_jobs_created_by', 'reconciliation_jobs')
    op.drop_index('ix_reconciliation_jobs_status', 'reconciliation_jobs')
    
    # Drop tables
    op.drop_table('reconciliation_audit_logs')
    op.drop_table('reconciliation_rules')
    op.drop_table('evidence')
    op.drop_table('human_judgments')
    op.drop_table('reconciliation_discrepancies')
    op.drop_table('reconciliation_jobs')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS evidencetype')
    op.execute('DROP TYPE IF EXISTS judgmentstatus')
    op.execute('DROP TYPE IF EXISTS reconciliationstatus')
