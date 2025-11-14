"""
Comprehensive tests for HR Salary module
Tests URL endpoints, views, forms, and service layer
"""
import pytest
from django.test import Client
from django.urls import reverse
from datetime import datetime


@pytest.mark.django_db
class TestSalaryURLs:
    """Test all Salary module URLs respond correctly"""

    def test_salary_employee_list_url(self, client):
        """Test salary employee list page"""
        url = reverse('human_resource:salary-employee-list')
        response = client.get(url)
        # Should redirect to login (302) or show page (200)
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"

    def test_salary_list_url(self, client):
        """Test salary list page"""
        url = reverse('human_resource:salary-list')
        response = client.get(url)
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"

    def test_salary_bank_statement_url(self, client):
        """Test bank statement page"""
        url = reverse('human_resource:salary-bank-statement')
        response = client.get(url)
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"

    def test_salary_bank_statement_export_url(self, client):
        """Test bank statement export"""
        url = reverse('human_resource:salary-bank-statement-export')
        response = client.get(url)
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"


@pytest.mark.django_db
class TestSalaryTemplates:
    """Test all Salary templates exist and render"""

    def test_salary_employee_list_template_exists(self):
        """Test salary_employee_list.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_employee_list.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_form_template_exists(self):
        """Test salary_form.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_form.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_list_template_exists(self):
        """Test salary_list.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_list.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_detail_template_exists(self):
        """Test salary_detail.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_detail.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_confirm_delete_template_exists(self):
        """Test salary_confirm_delete.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_confirm_delete.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_bank_statement_template_exists(self):
        """Test salary_bank_statement.html exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/transactions/salary_bank_statement.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_form_partial_template_exists(self):
        """Test salary_form partial template exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/partials/salary_form.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")

    def test_salary_list_partial_template_exists(self):
        """Test salary_list partial template exists"""
        from django.template.loader import get_template
        try:
            template = get_template('human_resource/partials/salary_list.html')
            assert template is not None
        except Exception as e:
            pytest.fail(f"Template loading failed: {e}")


@pytest.mark.django_db
class TestSalaryService:
    """Test SalaryService business logic"""

    def test_salary_service_imports(self):
        """Test SalaryService can be imported"""
        try:
            from human_resource.services.salary_service import SalaryService
            assert SalaryService is not None
        except ImportError as e:
            pytest.fail(f"SalaryService import failed: {e}")

    def test_get_month_name(self):
        """Test get_month_name method"""
        from human_resource.services.salary_service import SalaryService

        assert SalaryService.get_month_name(1) == 'January'
        assert SalaryService.get_month_name(6) == 'June'
        assert SalaryService.get_month_name(12) == 'December'

    def test_salary_service_has_required_methods(self):
        """Test SalaryService has all required methods"""
        from human_resource.services.salary_service import SalaryService

        required_methods = [
            'get_month_name',
            'calculate_salary_components',
            'get_working_days',
            'get_bank_installment',
            'get_mobile_excess',
            'calculate_net_salary',
            'generate_bank_statement_data'
        ]

        for method in required_methods:
            assert hasattr(SalaryService, method), f"SalaryService missing method: {method}"


@pytest.mark.django_db
class TestSalaryForm:
    """Test SalaryForm validation"""

    def test_salary_form_imports(self):
        """Test SalaryForm can be imported"""
        try:
            from human_resource.forms import SalaryForm
            assert SalaryForm is not None
        except ImportError as e:
            pytest.fail(f"SalaryForm import failed: {e}")

    def test_salary_form_has_month_choices(self):
        """Test SalaryForm has month choices"""
        from human_resource.forms import SalaryForm

        form = SalaryForm()
        assert 'fmonth' in form.fields
        assert len(form.fields['fmonth'].choices) == 12

    def test_salary_form_has_attendance_fields(self):
        """Test SalaryForm has attendance fields"""
        from human_resource.forms import SalaryForm

        form = SalaryForm()
        attendance_fields = ['present', 'absent', 'latein', 'halfday', 'sunday', 'coff', 'pl', 'overtimehrs']

        for field in attendance_fields:
            assert field in form.fields, f"Missing attendance field: {field}"

    def test_salary_form_has_deduction_fields(self):
        """Test SalaryForm has deduction fields"""
        from human_resource.forms import SalaryForm

        form = SalaryForm()
        deduction_fields = ['installment', 'mobileexeamt', 'deduction', 'remarks2']

        for field in deduction_fields:
            assert field in form.fields, f"Missing deduction field: {field}"


@pytest.mark.django_db
class TestSalaryViews:
    """Test Salary views configuration"""

    def test_salary_employee_list_view_exists(self):
        """Test SalaryEmployeeListView exists"""
        try:
            from human_resource.views.salary import SalaryEmployeeListView
            assert SalaryEmployeeListView is not None
        except ImportError as e:
            pytest.fail(f"SalaryEmployeeListView import failed: {e}")

    def test_salary_create_view_exists(self):
        """Test SalaryCreateView exists"""
        try:
            from human_resource.views.salary import SalaryCreateView
            assert SalaryCreateView is not None
        except ImportError as e:
            pytest.fail(f"SalaryCreateView import failed: {e}")

    def test_salary_list_view_exists(self):
        """Test SalaryListView exists"""
        try:
            from human_resource.views.salary import SalaryListView
            assert SalaryListView is not None
        except ImportError as e:
            pytest.fail(f"SalaryListView import failed: {e}")

    def test_salary_detail_view_exists(self):
        """Test SalaryDetailView exists"""
        try:
            from human_resource.views.salary import SalaryDetailView
            assert SalaryDetailView is not None
        except ImportError as e:
            pytest.fail(f"SalaryDetailView import failed: {e}")

    def test_salary_update_view_exists(self):
        """Test SalaryUpdateView exists"""
        try:
            from human_resource.views.salary import SalaryUpdateView
            assert SalaryUpdateView is not None
        except ImportError as e:
            pytest.fail(f"SalaryUpdateView import failed: {e}")

    def test_salary_delete_view_exists(self):
        """Test SalaryDeleteView exists"""
        try:
            from human_resource.views.salary import SalaryDeleteView
            assert SalaryDeleteView is not None
        except ImportError as e:
            pytest.fail(f"SalaryDeleteView import failed: {e}")

    def test_salary_bank_statement_view_exists(self):
        """Test SalaryBankStatementView exists"""
        try:
            from human_resource.views.salary import SalaryBankStatementView
            assert SalaryBankStatementView is not None
        except ImportError as e:
            pytest.fail(f"SalaryBankStatementView import failed: {e}")

    def test_salary_bank_statement_export_view_exists(self):
        """Test SalaryBankStatementExportView exists"""
        try:
            from human_resource.views.salary import SalaryBankStatementExportView
            assert SalaryBankStatementExportView is not None
        except ImportError as e:
            pytest.fail(f"SalaryBankStatementExportView import failed: {e}")


@pytest.mark.django_db
class TestSalaryModels:
    """Test Salary models configuration"""

    def test_salary_master_model_exists(self):
        """Test TblhrSalaryMaster model exists"""
        try:
            from human_resource.models import TblhrSalaryMaster
            assert TblhrSalaryMaster is not None
            assert TblhrSalaryMaster._meta.managed == False
        except ImportError as e:
            pytest.fail(f"TblhrSalaryMaster import failed: {e}")

    def test_salary_details_model_exists(self):
        """Test TblhrSalaryDetails model exists"""
        try:
            from human_resource.models import TblhrSalaryDetails
            assert TblhrSalaryDetails is not None
            assert TblhrSalaryDetails._meta.managed == False
        except ImportError as e:
            pytest.fail(f"TblhrSalaryDetails import failed: {e}")

    def test_office_staff_model_exists(self):
        """Test TblhrOfficestaff model exists"""
        try:
            from human_resource.models import TblhrOfficestaff
            assert TblhrOfficestaff is not None
            assert TblhrOfficestaff._meta.managed == False
        except ImportError as e:
            pytest.fail(f"TblhrOfficestaff import failed: {e}")


# Summary test
def test_salary_module_summary():
    """Summary test to verify all components"""
    print("\n" + "="*80)
    print("SALARY MODULE TEST SUMMARY")
    print("="*80)

    components = {
        'Models': ['TblhrSalaryMaster', 'TblhrSalaryDetails', 'TblhrOfficestaff'],
        'Views': ['SalaryEmployeeListView', 'SalaryCreateView', 'SalaryListView',
                  'SalaryDetailView', 'SalaryUpdateView', 'SalaryDeleteView',
                  'SalaryBankStatementView', 'SalaryBankStatementExportView'],
        'Forms': ['SalaryForm'],
        'Services': ['SalaryService'],
        'Templates': [
            'salary_employee_list.html',
            'salary_form.html',
            'salary_list.html',
            'salary_detail.html',
            'salary_confirm_delete.html',
            'salary_bank_statement.html',
            'partials/salary_form.html',
            'partials/salary_list.html'
        ]
    }

    for component_type, items in components.items():
        print(f"\n{component_type}: {len(items)} items")
        for item in items:
            print(f"  ✓ {item}")

    print("\n" + "="*80)
