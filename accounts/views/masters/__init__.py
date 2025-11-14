"""
Master views for the Accounts module.
"""

from .acchead import AccHeadListView, AccHeadCreateView, AccHeadUpdateView, AccHeadDeleteView
from .bank import BankListView, BankCreateView, BankUpdateView, BankDeleteView
from .currency import CurrencyListView, CurrencyCreateView, CurrencyUpdateView, CurrencyDeleteView
from .payment_terms import PaymentTermsListView, PaymentTermsCreateView, PaymentTermsUpdateView, PaymentTermsDeleteView
from .tds_code import TDSCodeListView, TDSCodeCreateView, TDSCodeUpdateView, TDSCodeDeleteView
from .misc import (
    ExcisableCommodityListView, ExcisableCommodityCreateView, ExcisableCommodityUpdateView, ExcisableCommodityDeleteView,
    ExciseListView, ExciseCreateView, ExciseUpdateView, ExciseDeleteView,
    FreightListView, FreightCreateView, FreightUpdateView, FreightDeleteView,
    IOUReasonsListView, IOUReasonsCreateView, IOUReasonsUpdateView, IOUReasonsDeleteView,
    IntrestTypeListView, IntrestTypeCreateView, IntrestTypeUpdateView, IntrestTypeDeleteView,
    InvoiceAgainstListView, InvoiceAgainstCreateView, InvoiceAgainstUpdateView, InvoiceAgainstDeleteView,
    LoanTypeListView, LoanTypeCreateView, LoanTypeUpdateView, LoanTypeDeleteView,
    OctoriListView, OctoriCreateView, OctoriUpdateView, OctoriDeleteView,
    PackingForwardingListView, PackingForwardingCreateView, PackingForwardingUpdateView, PackingForwardingDeleteView,
    PaidTypeListView, PaidTypeCreateView, PaidTypeUpdateView, PaidTypeDeleteView,
    PaymentReceiptAgainstListView, PaymentReceiptAgainstCreateView, PaymentReceiptAgainstUpdateView, PaymentReceiptAgainstDeleteView,
    PaymentModeListView, PaymentModeCreateView, PaymentModeUpdateView, PaymentModeDeleteView,
    TourExpencessListView, TourExpencessCreateView, TourExpencessUpdateView, TourExpencessDeleteView,
    VATListView, VATCreateView, VATUpdateView, VATDeleteView,
    WarrentyTermsListView, WarrentyTermsCreateView, WarrentyTermsUpdateView, WarrentyTermsDeleteView,
    CapitalListView, CapitalCreateView, CapitalUpdateView, CapitalDeleteView,
    LoanListView, LoanCreateView, LoanUpdateView, LoanDeleteView
)

__all__ = [
    'AccHeadListView', 'AccHeadCreateView', 'AccHeadUpdateView', 'AccHeadDeleteView',
    'BankListView', 'BankCreateView', 'BankUpdateView', 'BankDeleteView',
    'CurrencyListView', 'CurrencyCreateView', 'CurrencyUpdateView', 'CurrencyDeleteView',
    'PaymentTermsListView', 'PaymentTermsCreateView', 'PaymentTermsUpdateView', 'PaymentTermsDeleteView',
    'TDSCodeListView', 'TDSCodeCreateView', 'TDSCodeUpdateView', 'TDSCodeDeleteView',
    'ExcisableCommodityListView', 'ExcisableCommodityCreateView', 'ExcisableCommodityUpdateView', 'ExcisableCommodityDeleteView',
    'ExciseListView', 'ExciseCreateView', 'ExciseUpdateView', 'ExciseDeleteView',
    'FreightListView', 'FreightCreateView', 'FreightUpdateView', 'FreightDeleteView',
    'IOUReasonsListView', 'IOUReasonsCreateView', 'IOUReasonsUpdateView', 'IOUReasonsDeleteView',
    'IntrestTypeListView', 'IntrestTypeCreateView', 'IntrestTypeUpdateView', 'IntrestTypeDeleteView',
    'InvoiceAgainstListView', 'InvoiceAgainstCreateView', 'InvoiceAgainstUpdateView', 'InvoiceAgainstDeleteView',
    'LoanTypeListView', 'LoanTypeCreateView', 'LoanTypeUpdateView', 'LoanTypeDeleteView',
    'OctoriListView', 'OctoriCreateView', 'OctoriUpdateView', 'OctoriDeleteView',
    'PackingForwardingListView', 'PackingForwardingCreateView', 'PackingForwardingUpdateView', 'PackingForwardingDeleteView',
    'PaidTypeListView', 'PaidTypeCreateView', 'PaidTypeUpdateView', 'PaidTypeDeleteView',
    'PaymentReceiptAgainstListView', 'PaymentReceiptAgainstCreateView', 'PaymentReceiptAgainstUpdateView', 'PaymentReceiptAgainstDeleteView',
    'PaymentModeListView', 'PaymentModeCreateView', 'PaymentModeUpdateView', 'PaymentModeDeleteView',
    'TourExpencessListView', 'TourExpencessCreateView', 'TourExpencessUpdateView', 'TourExpencessDeleteView',
    'VATListView', 'VATCreateView', 'VATUpdateView', 'VATDeleteView',
    'WarrentyTermsListView', 'WarrentyTermsCreateView', 'WarrentyTermsUpdateView', 'WarrentyTermsDeleteView',
    'CapitalListView', 'CapitalCreateView', 'CapitalUpdateView', 'CapitalDeleteView',
    'LoanListView', 'LoanCreateView', 'LoanUpdateView', 'LoanDeleteView',
]
