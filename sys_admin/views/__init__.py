"""
SysAdmin Views - Modular Structure
All views are re-exported here for backward compatibility with urls.py
"""

# Dashboard
from .dashboard import (
    SysAdminDashboardView,
)

# Company Data (Country, State, City, Cascading Dropdowns)
from .company import (
    # Country
    CountryListView,
    CountryCreateView,
    CountryUpdateView,
    CountryDeleteView,
    CountryRowView,
    # State
    StateListView,
    StateCreateView,
    StateUpdateView,
    StateDeleteView,
    StateRowView,
    # City
    CityListView,
    CityCreateView,
    CityUpdateView,
    CityDeleteView,
    CityRowView,
    # Cascading
    StatesByCountryView,
)

# Financial Year Management
from .financial import (
    FinancialYearListView,
    FinancialYearCreateView,
    FinancialYearConfirmView,
    FinancialYearUpdateView,
    FinancialYearDeleteView,
    FinancialYearRowView,
    FinancialYearDetailsView,  # Legacy view for compatibility
)

# System Configuration (Unit Master, GST Master)
from .config import (
    # Unit Master
    UnitMasterListView,
    UnitMasterCreateView,
    UnitMasterUpdateView,
    UnitMasterDeleteView,
    # GST Master
    GSTMasterListView,
    GSTMasterCreateView,
    GSTMasterUpdateView,
    GSTMasterDeleteView,
    GSTMasterDetailView,
)


__all__ = [
    # Dashboard
    'SysAdminDashboardView',
    # Country
    'CountryListView',
    'CountryCreateView',
    'CountryUpdateView',
    'CountryDeleteView',
    'CountryRowView',
    # State
    'StateListView',
    'StateCreateView',
    'StateUpdateView',
    'StateDeleteView',
    'StateRowView',
    # City
    'CityListView',
    'CityCreateView',
    'CityUpdateView',
    'CityDeleteView',
    'CityRowView',
    # Cascading
    'StatesByCountryView',
    # Financial Year
    'FinancialYearListView',
    'FinancialYearCreateView',
    'FinancialYearConfirmView',
    'FinancialYearUpdateView',
    'FinancialYearDeleteView',
    'FinancialYearRowView',
    'FinancialYearDetailsView',
    # Unit Master
    'UnitMasterListView',
    'UnitMasterCreateView',
    'UnitMasterUpdateView',
    'UnitMasterDeleteView',
    # GST Master
    'GSTMasterListView',
    'GSTMasterCreateView',
    'GSTMasterUpdateView',
    'GSTMasterDeleteView',
    'GSTMasterDetailView',
]
