#!/usr/bin/env python3
"""
Playwright Test Generator - Creates test templates for unmigrated features
"""
import csv
from pathlib import Path
from collections import defaultdict

# Path configurations
DJANGO_ROOT = Path('/home/user/sapl')
CSV_FILE = DJANGO_ROOT / 'aspx_django_mapping.csv'
TESTS_DIR = DJANGO_ROOT / 'tests' / 'playwright'


def analyze_test_coverage():
    """Analyze current test coverage from CSV mapping"""
    if not CSV_FILE.exists():
        print("❌ CSV mapping file not found. Run detailed_file_mapping.py first.")
        return

    total_files = 0
    tested_files = 0
    by_module = defaultdict(lambda: {'total': 0, 'tested': 0, 'files': []})

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_files += 1
            module = row['Django App']
            has_test = row['Playwright Test'] == 'Yes'

            by_module[module]['total'] += 1
            if has_test:
                tested_files += 1
                by_module[module]['tested'] += 1
            else:
                by_module[module]['files'].append(row)

    print("=" * 80)
    print("PLAYWRIGHT TEST COVERAGE ANALYSIS")
    print("=" * 80)
    print()
    print(f"📊 Total Files: {total_files}")
    print(f"✅ Files with Tests: {tested_files}")
    print(f"❌ Files without Tests: {total_files - tested_files}")
    print(f"📈 Coverage: {(tested_files / total_files * 100):.1f}%")
    print()

    print("=" * 80)
    print("MODULE-WISE TEST COVERAGE")
    print("=" * 80)
    print()

    for module in sorted(by_module.keys()):
        data = by_module[module]
        coverage = (data['tested'] / data['total'] * 100) if data['total'] > 0 else 0

        print(f"📦 {module}")
        print(f"   Total: {data['total']} | Tested: {data['tested']} | Coverage: {coverage:.1f}%")

        if coverage < 100:
            untested = data['total'] - data['tested']
            print(f"   ⚠️  Missing {untested} tests")

    print()

    return by_module


def generate_test_template(module, category, feature_name, aspx_file):
    """Generate Playwright test template"""
    test_name = feature_name.lower().replace(' ', '_').replace('/', '_')
    class_name = ''.join(word.capitalize() for word in test_name.split('_'))

    template = f'''"""
Playwright test for {feature_name}
ASP.NET Source: {aspx_file}
Django App: {module}
Category: {category}
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def authenticated_page(page: Page):
    """Fixture to provide authenticated page"""
    page.goto("http://localhost:8000/login/")
    page.fill("#id_username", "admin")
    page.fill("#id_password", "admin")
    page.click("button[type=submit]")
    expect(page).to_have_url("http://localhost:8000/")
    return page


class Test{class_name}:
    """Test suite for {feature_name}"""

    def test_list_view_loads(self, authenticated_page: Page):
        """Test that the list view loads successfully"""
        # TODO: Navigate to the list view
        authenticated_page.goto("http://localhost:8000/{module}/{test_name}/")

        # TODO: Verify page loads
        expect(authenticated_page).to_have_title(/{feature_name}/i)

        # TODO: Verify key elements are present
        # expect(authenticated_page.locator("h1")).to_contain_text("{feature_name}")

    def test_create_new_record(self, authenticated_page: Page):
        """Test creating a new record"""
        # TODO: Navigate to create view
        authenticated_page.goto("http://localhost:8000/{module}/{test_name}/create/")

        # TODO: Fill form fields
        # authenticated_page.fill("#id_field_name", "Test Value")

        # TODO: Submit form
        # authenticated_page.click("button[type=submit]")

        # TODO: Verify success
        # expect(authenticated_page.locator(".alert-success")).to_be_visible()

    def test_edit_existing_record(self, authenticated_page: Page):
        """Test editing an existing record"""
        # TODO: Create a test record first or use existing one
        # TODO: Navigate to edit view
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/1/edit/")

        # TODO: Modify field
        # authenticated_page.fill("#id_field_name", "Updated Value")

        # TODO: Submit
        # authenticated_page.click("button[type=submit]")

        # TODO: Verify update
        # expect(authenticated_page.locator(".alert-success")).to_be_visible()

    def test_delete_record(self, authenticated_page: Page):
        """Test deleting a record"""
        # TODO: Create a test record first
        # TODO: Navigate to list view
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/")

        # TODO: Click delete button
        # authenticated_page.click("button.delete-btn")

        # TODO: Confirm deletion
        # authenticated_page.click("button.confirm-delete")

        # TODO: Verify deletion
        # expect(authenticated_page.locator(".alert-success")).to_contain_text("deleted")

    def test_search_functionality(self, authenticated_page: Page):
        """Test search/filter functionality"""
        # TODO: Navigate to list view
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/")

        # TODO: Enter search term
        # authenticated_page.fill("#search", "test search")
        # authenticated_page.click("button[type=submit]")

        # TODO: Verify filtered results
        # expect(authenticated_page.locator(".search-results")).to_be_visible()

    @pytest.mark.htmx
    def test_htmx_partial_update(self, authenticated_page: Page):
        """Test HTMX partial page updates"""
        # TODO: Navigate to page with HTMX
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/")

        # TODO: Trigger HTMX request
        # authenticated_page.click("#htmx-trigger")

        # TODO: Verify partial update
        # expect(authenticated_page.locator("#updated-section")).to_be_visible()

    def test_form_validation(self, authenticated_page: Page):
        """Test form validation"""
        # TODO: Navigate to create form
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/create/")

        # TODO: Submit empty form
        # authenticated_page.click("button[type=submit]")

        # TODO: Verify validation errors
        # expect(authenticated_page.locator(".error-message")).to_be_visible()

    def test_pagination(self, authenticated_page: Page):
        """Test pagination if applicable"""
        # TODO: Navigate to list view with many records
        # authenticated_page.goto("http://localhost:8000/{module}/{test_name}/")

        # TODO: Verify pagination controls
        # expect(authenticated_page.locator(".pagination")).to_be_visible()

        # TODO: Click next page
        # authenticated_page.click("a.page-next")

        # TODO: Verify page 2 loads
        # expect(authenticated_page).to_have_url(/page=2/)
'''

    return template


def create_missing_test_files():
    """Create test file templates for features without tests"""
    if not CSV_FILE.exists():
        print("❌ CSV mapping file not found.")
        return

    # Ensure tests directory exists
    TESTS_DIR.mkdir(parents=True, exist_ok=True)

    # Group by module
    by_module = defaultdict(list)

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Playwright Test'] == 'No' and row['App Exists'] == 'Yes':
                by_module[row['Django App']].append(row)

    print("=" * 80)
    print("GENERATING TEST TEMPLATES")
    print("=" * 80)
    print()

    created_count = 0

    for module, files in by_module.items():
        # Group by category
        by_category = defaultdict(list)
        for file in files:
            by_category[file['Category']].append(file)

        for category, category_files in by_category.items():
            # Create one test file per category per module
            if not category_files:
                continue

            test_file_name = f"test_{module}_{category.lower()}.py"
            test_file_path = TESTS_DIR / test_file_name

            # Skip if file already exists
            if test_file_path.exists():
                print(f"⏭️  Skipping {test_file_name} (already exists)")
                continue

            # Take first file as template
            sample_file = category_files[0]
            feature_name = f"{module} {category}".title()
            aspx_path = sample_file['ASPX File Path']

            test_content = generate_test_template(module, category, feature_name, aspx_path)

            # Add comment about other files in this category
            if len(category_files) > 1:
                comment = f"\n# Note: This test file covers {len(category_files)} .aspx files in {module}/{category}:\n"
                for f in category_files[:10]:
                    comment += f"# - {f['ASPX File Path'].split('/')[-1]}\n"
                if len(category_files) > 10:
                    comment += f"# ... and {len(category_files) - 10} more files\n"

                test_content = test_content.replace('"""', '"""' + comment, 1)

            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)

            print(f"✅ Created: {test_file_name} (covers {len(category_files)} features)")
            created_count += 1

    print()
    print(f"📝 Total test templates created: {created_count}")
    print()


if __name__ == '__main__':
    analyze_test_coverage()
    print()
    create_missing_test_files()
