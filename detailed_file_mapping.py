#!/usr/bin/env python3
"""
Detailed File Mapping - Creates comprehensive mapping of every .aspx file to Django components
"""
import os
import re
from pathlib import Path
from collections import defaultdict
import csv

# Path configurations
AASPNET_ROOT = Path('/home/user/sapl/aaspnet')
DJANGO_ROOT = Path('/home/user/sapl')

# Module name mappings ASP.NET -> Django
MODULE_MAPPING = {
    'SysAdmin': 'sys_admin',
    'SalesDistribution': 'sales_distribution',
    'Design': 'design',
    'MaterialPlanning': 'material_planning',
    'MaterialManagement': 'material_management',
    'ProjectManagement': 'project_management',
    'Report': 'reports',
    'Inventory': 'inventory',
    'QualityControl': 'quality_control',
    'Accounts': 'accounts',
    'HR': 'human_resource',
    'MROffice': 'mr_office',
    'MIS': 'mis',
    'Machinery': 'machinery',
    'DailyReportingSystem': 'daily_report_system',
    'SysSupport': 'sys_admin',
    'Scheduler': 'human_resource',
    'Chatting': 'core',
}


def find_all_aspx_files():
    """Find all .aspx files in the aaspnet/Module directory"""
    module_path = AASPNET_ROOT / 'Module'
    aspx_files = []

    for aspx_file in module_path.rglob('*.aspx'):
        rel_path = aspx_file.relative_to(AASPNET_ROOT)

        # Extract module from path
        parts = rel_path.parts
        if len(parts) >= 2 and parts[0] == 'Module':
            module_name = parts[1]

            # Determine category (Masters, Transactions, Reports, etc.)
            category = 'Root'
            if len(parts) >= 3:
                if parts[2] in ['Masters', 'Transactions', 'Reports']:
                    category = parts[2]

            aspx_files.append({
                'aspx_path': str(rel_path),
                'module': module_name,
                'category': category,
                'filename': aspx_file.name,
                'full_path': str(aspx_file),
            })

    return sorted(aspx_files, key=lambda x: x['aspx_path'])


def check_django_component(aspx_info):
    """Check if Django component exists for this aspx file"""
    module = aspx_info['module']
    django_app = MODULE_MAPPING.get(module, module.lower())
    django_app_path = DJANGO_ROOT / django_app

    result = {
        'django_app': django_app,
        'app_exists': django_app_path.exists(),
        'has_views': False,
        'has_urls': False,
        'has_templates': False,
        'migration_status': 'Not Started',
        'notes': ''
    }

    if not result['app_exists']:
        result['migration_status'] = 'App Not Created'
        result['notes'] = f'Django app "{django_app}" does not exist'
        return result

    # Check for basic structure
    result['has_views'] = (django_app_path / 'views.py').exists()
    result['has_urls'] = (django_app_path / 'urls.py').exists()
    result['has_templates'] = (django_app_path / 'templates').exists()

    # Try to infer if this specific feature is migrated
    # Convert filename to potential view/template names
    base_name = aspx_info['filename'].replace('.aspx', '')

    # Common patterns
    pattern_name = base_name.lower().replace('_', '')

    # Check views.py for mentions
    if result['has_views']:
        views_file = django_app_path / 'views.py'
        try:
            content = views_file.read_text().lower()
            if pattern_name in content or base_name.lower() in content:
                result['migration_status'] = 'Likely Migrated'
                result['notes'] = f'Found reference to "{base_name}" in views.py'
            else:
                result['migration_status'] = 'Partially Migrated'
                result['notes'] = 'App exists but specific feature not found'
        except:
            result['migration_status'] = 'Unknown'
            result['notes'] = 'Could not read views.py'
    else:
        result['migration_status'] = 'Not Migrated'
        result['notes'] = 'App exists but no views.py found'

    return result


def check_playwright_test(aspx_info):
    """Check if Playwright test exists for this feature"""
    tests_dir = DJANGO_ROOT / 'tests' / 'playwright'

    if not tests_dir.exists():
        return {'has_test': False, 'test_file': None}

    # Try to find related test file
    base_name = aspx_info['filename'].replace('.aspx', '').lower()
    module = aspx_info['module'].lower()

    # Common test file patterns
    patterns = [
        f"test_{module}_{base_name}.py",
        f"test_{base_name}.py",
        f"test_{module}.py",
    ]

    for pattern in patterns:
        test_file = tests_dir / pattern
        if test_file.exists():
            return {'has_test': True, 'test_file': str(test_file.relative_to(DJANGO_ROOT))}

    return {'has_test': False, 'test_file': None}


def generate_csv_mapping():
    """Generate CSV file with detailed mapping"""
    aspx_files = find_all_aspx_files()

    csv_file = DJANGO_ROOT / 'aspx_django_mapping.csv'

    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'ASPX File Path',
            'ASP.NET Module',
            'Category',
            'Django App',
            'App Exists',
            'Migration Status',
            'Has Views',
            'Has URLs',
            'Has Templates',
            'Playwright Test',
            'Test File',
            'Notes'
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for aspx in aspx_files:
            django_info = check_django_component(aspx)
            test_info = check_playwright_test(aspx)

            writer.writerow({
                'ASPX File Path': aspx['aspx_path'],
                'ASP.NET Module': aspx['module'],
                'Category': aspx['category'],
                'Django App': django_info['django_app'],
                'App Exists': 'Yes' if django_info['app_exists'] else 'No',
                'Migration Status': django_info['migration_status'],
                'Has Views': 'Yes' if django_info['has_views'] else 'No',
                'Has URLs': 'Yes' if django_info['has_urls'] else 'No',
                'Has Templates': 'Yes' if django_info['has_templates'] else 'No',
                'Playwright Test': 'Yes' if test_info['has_test'] else 'No',
                'Test File': test_info['test_file'] or '',
                'Notes': django_info['notes']
            })

    print(f"✅ CSV mapping generated: {csv_file}")
    print(f"📊 Total .aspx files mapped: {len(aspx_files)}")

    return aspx_files


def generate_markdown_summary():
    """Generate Markdown summary report"""
    aspx_files = find_all_aspx_files()

    # Group by module and category
    by_module = defaultdict(lambda: defaultdict(list))

    for aspx in aspx_files:
        by_module[aspx['module']][aspx['category']].append(aspx)

    md_file = DJANGO_ROOT / 'MIGRATION_MAPPING.md'

    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# ASP.NET to Django Migration Mapping\n\n")
        f.write("## Overview\n\n")
        f.write(f"- **Total ASP.NET Modules:** {len(by_module)}\n")
        f.write(f"- **Total .aspx Files:** {len(aspx_files)}\n\n")

        f.write("## Module-wise Breakdown\n\n")

        for module in sorted(by_module.keys()):
            django_app = MODULE_MAPPING.get(module, module.lower())
            django_app_path = DJANGO_ROOT / django_app
            app_exists = django_app_path.exists()

            categories = by_module[module]
            total_files = sum(len(files) for files in categories.values())

            f.write(f"### {module} → `{django_app}`\n\n")
            f.write(f"- **Django App Exists:** {'✅ Yes' if app_exists else '❌ No'}\n")
            f.write(f"- **Total Files:** {total_files}\n\n")

            for category in sorted(categories.keys()):
                files = categories[category]
                f.write(f"#### {category} ({len(files)} files)\n\n")

                for aspx in files[:20]:  # Limit to first 20
                    django_info = check_django_component(aspx)
                    test_info = check_playwright_test(aspx)

                    status_icon = {
                        'Likely Migrated': '✅',
                        'Partially Migrated': '⚠️',
                        'Not Migrated': '❌',
                        'Not Started': '⏳',
                        'App Not Created': '🚫',
                        'Unknown': '❓'
                    }.get(django_info['migration_status'], '❓')

                    test_icon = '🧪' if test_info['has_test'] else '⬜'

                    f.write(f"- {status_icon} {test_icon} `{aspx['filename']}` - {django_info['migration_status']}\n")

                if len(files) > 20:
                    f.write(f"- ... and {len(files) - 20} more files\n")

                f.write("\n")

            f.write("---\n\n")

        f.write("## Legend\n\n")
        f.write("- ✅ Likely Migrated\n")
        f.write("- ⚠️ Partially Migrated\n")
        f.write("- ❌ Not Migrated\n")
        f.write("- ⏳ Not Started\n")
        f.write("- 🚫 App Not Created\n")
        f.write("- ❓ Unknown\n")
        f.write("- 🧪 Has Playwright Test\n")
        f.write("- ⬜ No Playwright Test\n")

    print(f"✅ Markdown summary generated: {md_file}")


if __name__ == '__main__':
    print("=" * 80)
    print("Generating Detailed File Mapping...")
    print("=" * 80)
    print()

    generate_csv_mapping()
    print()
    generate_markdown_summary()
    print()
    print("=" * 80)
    print("✅ Mapping complete!")
    print("=" * 80)
