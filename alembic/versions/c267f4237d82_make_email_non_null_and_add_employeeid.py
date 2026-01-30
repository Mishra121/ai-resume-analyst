"""Make email non-null and add employeeid

Revision ID: c267f4237d82
Revises: 679265dbec31
Create Date: 2026-01-23 12:56:50.851066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c267f4237d82'
down_revision: Union[str, Sequence[str], None] = '679265dbec31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make 'email' NOT NULL in employees
    op.alter_column(
        'employees',
        'email',
        existing_type=sa.VARCHAR(),
        nullable=False
    )

    op.add_column(
        'employees',
        sa.Column('employeeid', sa.String(), nullable=True)
    )

    # Remove 'employee_id' column from resumes
    with op.batch_alter_table('resumes') as batch_op:
        batch_op.drop_constraint("resumes_employee_id_fkey", type_="foreignkey")
        batch_op.drop_column("employee_id")

    # Add 'employee_email' column in resumes and create FK
    op.add_column(
        'resumes',
        sa.Column('employee_email', sa.String(), nullable=False)
    )
    op.create_foreign_key(
        "fk_resumes_employee_email",
        "resumes",
        "employees",
        ["employee_email"],
        ["email"],
        ondelete="CASCADE"
    )

def downgrade() -> None:
    """Downgrade schema."""
    # Drop FK and column 'employee_email' from resumes
    op.drop_constraint("fk_resumes_employee_email", "resumes", type_="foreignkey")
    op.drop_column("resumes", "employee_email")

    # Re-add 'employee_id' column and foreign key in resumes
    with op.batch_alter_table('resumes') as batch_op:
        batch_op.add_column(sa.Column('employee_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(
            "resumes_employee_id_fkey",
            "employees",
            ["employee_id"],
            ["id"],
            ondelete="CASCADE"
        )

    # Drop 'employeeid' column from employees
    with op.batch_alter_table('employees') as batch_op:
        batch_op.drop_column("employeeid")

    # Revert 'email' to nullable
    op.alter_column(
        'employees',
        'email',
        existing_type=sa.VARCHAR(),
        nullable=True
    )



