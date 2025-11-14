"""
Human Resource Views Package
Re-exports all views from modular files for backward compatibility with urls.py
"""

# Dashboard
from .dashboard import HRDashboardView

# Masters (55 views)
from .masters import (
    # Business Group
    BusinessGroupListView, BusinessGroupCreateView, BusinessGroupUpdateView,
    BusinessGroupDeleteView, BusinessGroupRowView,

    # Department
    DepartmentListView, DepartmentCreateView, DepartmentUpdateView,
    DepartmentDeleteView, DepartmentRowView,

    # Designation
    DesignationListView, DesignationCreateView, DesignationUpdateView,
    DesignationDeleteView, DesignationRowView,

    # Grade
    GradeListView, GradeCreateView, GradeUpdateView,
    GradeDeleteView, GradeRowView,

    # Holiday Master
    HolidayMasterListView, HolidayMasterCreateView, HolidayMasterUpdateView,
    HolidayMasterDeleteView, HolidayMasterRowView,

    # Working Days
    WorkingDaysListView, WorkingDaysCreateView, WorkingDaysUpdateView,
    WorkingDaysDeleteView, WorkingDaysRowView,

    # Corporate Mobile No
    CorporateMobileNoListView, CorporateMobileNoCreateView, CorporateMobileNoUpdateView,
    CorporateMobileNoDeleteView, CorporateMobileNoRowView,

    # Gate Pass Reason
    GatePassReasonListView, GatePassReasonCreateView, GatePassReasonUpdateView,
    GatePassReasonDeleteView, GatePassReasonRowView,

    # Intercom Extension
    IntercomExtListView, IntercomExtCreateView, IntercomExtUpdateView,
    IntercomExtDeleteView, IntercomExtRowView,

    # PF Slab
    PFSlabListView, PFSlabCreateView, PFSlabUpdateView,
    PFSlabDeleteView, PFSlabRowView,

    # Swap Card
    SwapCardListView, SwapCardCreateView, SwapCardUpdateView,
    SwapCardDeleteView, SwapCardRowView,
)

# Employee (5 views)
from .employee import (
    EmployeeListView, EmployeeDetailView, EmployeeCreateView,
    EmployeeUpdateView, EmployeeDeleteView,
)

# Salary (8 views)
from .salary import (
    SalaryEmployeeListView, SalaryCreateView, SalaryListView,
    SalaryDetailView, SalaryUpdateView, SalaryDeleteView,
    SalaryBankStatementView, SalaryBankStatementExportView,
)

# Loan (10 views)
from .loan import (
    BankLoanListView, BankLoanCreateView, BankLoanUpdateView,
    BankLoanDetailView, BankLoanDeleteView,
    MobileBillListView, MobileBillCreateView, MobileBillUpdateView,
    MobileBillDetailView, MobileBillDeleteView,
)

# Recruitment (5 views)
from .recruitment import (
    OfferLetterListView, OfferLetterCreateView, OfferLetterUpdateView,
    OfferLetterDetailView, OfferLetterDeleteView,
)

# Gate Pass (5 views)
from .gatepass import (
    GatePassListView, GatePassCreateView, GatePassUpdateView,
    GatePassDetailView, GatePassDeleteView,
)

# Travel (5 views)
from .travel import (
    TourIntimationListView, TourIntimationCreateView, TourIntimationUpdateView,
    TourIntimationDetailView, TourIntimationDeleteView,
)


__all__ = [
    # Dashboard (1 view)
    'HRDashboardView',

    # Masters (55 views)
    'BusinessGroupListView', 'BusinessGroupCreateView', 'BusinessGroupUpdateView',
    'BusinessGroupDeleteView', 'BusinessGroupRowView',
    'DepartmentListView', 'DepartmentCreateView', 'DepartmentUpdateView',
    'DepartmentDeleteView', 'DepartmentRowView',
    'DesignationListView', 'DesignationCreateView', 'DesignationUpdateView',
    'DesignationDeleteView', 'DesignationRowView',
    'GradeListView', 'GradeCreateView', 'GradeUpdateView',
    'GradeDeleteView', 'GradeRowView',
    'HolidayMasterListView', 'HolidayMasterCreateView', 'HolidayMasterUpdateView',
    'HolidayMasterDeleteView', 'HolidayMasterRowView',
    'WorkingDaysListView', 'WorkingDaysCreateView', 'WorkingDaysUpdateView',
    'WorkingDaysDeleteView', 'WorkingDaysRowView',
    'CorporateMobileNoListView', 'CorporateMobileNoCreateView', 'CorporateMobileNoUpdateView',
    'CorporateMobileNoDeleteView', 'CorporateMobileNoRowView',
    'GatePassReasonListView', 'GatePassReasonCreateView', 'GatePassReasonUpdateView',
    'GatePassReasonDeleteView', 'GatePassReasonRowView',
    'IntercomExtListView', 'IntercomExtCreateView', 'IntercomExtUpdateView',
    'IntercomExtDeleteView', 'IntercomExtRowView',
    'PFSlabListView', 'PFSlabCreateView', 'PFSlabUpdateView',
    'PFSlabDeleteView', 'PFSlabRowView',
    'SwapCardListView', 'SwapCardCreateView', 'SwapCardUpdateView',
    'SwapCardDeleteView', 'SwapCardRowView',

    # Employee (5 views)
    'EmployeeListView', 'EmployeeDetailView', 'EmployeeCreateView',
    'EmployeeUpdateView', 'EmployeeDeleteView',

    # Salary (8 views)
    'SalaryEmployeeListView', 'SalaryCreateView', 'SalaryListView',
    'SalaryDetailView', 'SalaryUpdateView', 'SalaryDeleteView',
    'SalaryBankStatementView', 'SalaryBankStatementExportView',

    # Loan (10 views)
    'BankLoanListView', 'BankLoanCreateView', 'BankLoanUpdateView',
    'BankLoanDetailView', 'BankLoanDeleteView',
    'MobileBillListView', 'MobileBillCreateView', 'MobileBillUpdateView',
    'MobileBillDetailView', 'MobileBillDeleteView',

    # Recruitment (5 views)
    'OfferLetterListView', 'OfferLetterCreateView', 'OfferLetterUpdateView',
    'OfferLetterDetailView', 'OfferLetterDeleteView',

    # Gate Pass (5 views)
    'GatePassListView', 'GatePassCreateView', 'GatePassUpdateView',
    'GatePassDetailView', 'GatePassDeleteView',

    # Travel (5 views)
    'TourIntimationListView', 'TourIntimationCreateView', 'TourIntimationUpdateView',
    'TourIntimationDetailView', 'TourIntimationDeleteView',
]
