#!/usr/bin/env python3
"""
ASP.NET to Django Migration Audit Script
Parses Web.sitemap and generates comprehensive migration status report
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re

# Base paths
AASPNET_PATH = Path("/home/user/sapl/aaspnet")
DJANGO_PATH = Path("/home/user/sapl")
SITEMAP_PATH = AASPNET_PATH / "Web.sitemap"

# Module mapping: ASP.NET to Django
MODULE_MAPPING = {
    "SysAdmin": "sys_admin",
    "SalesDistribution": "sales_distribution",
    "Design": "design",
    "MaterialPlanning": "material_planning",
    "MaterialManagement": "material_management",
    "ProjectManagement": "project_management",
    "Inventory": "inventory",
    "QualityControl": "quality_control",
    "Accounts": "accounts",
    "HR": "human_resource",
    "MROffice": "mr_office",
    "MIS": "mis",
    "Machinery": "machinery",
    "Report": "reports",
    "DailyReportingSystem": "daily_report_system",
}

class MigrationAuditor:
    def __init__(self):
        self.menu_items = []
        self.aspx_files = defaultdict(list)
        self.django_views = defaultdict(list)
        self.django_urls = defaultdict(list)

    def parse_sitemap(self):
        """Parse Web.sitemap and extract all menu items"""
        tree = ET.parse(SITEMAP_PATH)
        root = tree.getroot()

        # Remove namespace for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        def extract_menu_items(node, path=[]):
            for child in node.findall('siteMapNode'):
                url = child.get('url', '')
                title = child.get('title', '')

                if url and title:
                    menu_path = " > ".join(path + [title])

                    # Extract module and file info from URL
                    module_match = re.search(r'Module/([^/]+)', url)
                    file_match = re.search(r'/([^/]+\.aspx)', url)

                    module = module_match.group(1) if module_match else None
                    file = file_match.group(1) if file_match else None

                    self.menu_items.append({
                        'path': menu_path,
                        'url': url,
                        'title': title,
                        'module': module,
                        'file': file,
                    })

                # Recurse
                extract_menu_items(child, path + [title])

        extract_menu_items(root)

    def scan_aspx_files(self):
        """Scan for all .aspx files in aaspnet/Module"""
        module_path = AASPNET_PATH / "Module"

        for aspx_file in module_path.rglob("*.aspx"):
            rel_path = aspx_file.relative_to(module_path)
            module = rel_path.parts[0]

            self.aspx_files[module].append({
                'path': str(rel_path),
                'file': aspx_file.name,
                'full_path': str(aspx_file),
            })

    def scan_django_views(self):
        """Scan Django apps for views"""
        for django_module in MODULE_MAPPING.values():
            module_path = DJANGO_PATH / django_module

            if not module_path.exists():
                continue

            # Check for views.py or views/ directory
            views_file = module_path / "views.py"
            views_dir = module_path / "views"

            if views_file.exists():
                self.django_views[django_module].append(str(views_file))

            if views_dir.exists():
                for view_file in views_dir.rglob("*.py"):
                    if view_file.name != "__init__.py":
                        self.django_views[django_module].append(str(view_file))

    def scan_django_urls(self):
        """Scan Django apps for URL patterns"""
        for django_module in MODULE_MAPPING.values():
            module_path = DJANGO_PATH / django_module
            urls_file = module_path / "urls.py"

            if urls_file.exists():
                with open(urls_file, 'r') as f:
                    content = f.read()

                # Count path() patterns
                url_patterns = re.findall(r"path\(['\"]([^'\"]+)", content)
                self.django_urls[django_module] = url_patterns

    def generate_report(self):
        """Generate comprehensive migration audit report"""
        report = []

        report.append("=" * 100)
        report.append("ASP.NET TO DJANGO MIGRATION AUDIT REPORT")
        report.append("=" * 100)
        report.append("")

        # Summary Statistics
        report.append("## SUMMARY STATISTICS")
        report.append("-" * 100)
        report.append(f"Total Menu Items in Web.sitemap: {len(self.menu_items)}")

        total_aspx = sum(len(files) for files in self.aspx_files.values())
        report.append(f"Total .aspx Files Found: {total_aspx}")

        total_views = sum(len(views) for views in self.django_views.values())
        report.append(f"Total Django View Files: {total_views}")

        total_urls = sum(len(urls) for urls in self.django_urls.values())
        report.append(f"Total Django URL Patterns: {total_urls}")
        report.append("")

        # Module-wise breakdown
        report.append("## MODULE-WISE BREAKDOWN")
        report.append("-" * 100)
        report.append(f"{'ASP.NET Module':<30} {'ASPX Files':<15} {'Django App':<30} {'Views':<10} {'URLs':<10} {'Status':<15}")
        report.append("-" * 100)

        for aspnet_module, django_module in MODULE_MAPPING.items():
            aspx_count = len(self.aspx_files.get(aspnet_module, []))
            view_count = len(self.django_views.get(django_module, []))
            url_count = len(self.django_urls.get(django_module, []))

            # Determine status
            if aspx_count == 0:
                status = "N/A"
            elif view_count == 0 and url_count == 0:
                status = "❌ Not Started"
            elif view_count > 0 and url_count > 0:
                status = "🟡 In Progress"
            else:
                status = "🟢 Partial"

            report.append(f"{aspnet_module:<30} {aspx_count:<15} {django_module:<30} {view_count:<10} {url_count:<10} {status:<15}")

        report.append("")

        # Detailed Menu Item Analysis
        report.append("## DETAILED MENU ITEM ANALYSIS")
        report.append("-" * 100)

        # Group by module
        by_module = defaultdict(list)
        for item in self.menu_items:
            if item['module']:
                by_module[item['module']].append(item)

        for module in sorted(by_module.keys()):
            report.append(f"\n### Module: {module}")
            report.append(f"Django App: {MODULE_MAPPING.get(module, 'UNMAPPED')}")
            report.append("-" * 80)

            items = by_module[module]
            report.append(f"Total Menu Items: {len(items)}")

            # List all menu items
            for item in items:
                report.append(f"  - {item['path']}")
                report.append(f"    URL: {item['url']}")
                if item['file']:
                    report.append(f"    File: {item['file']}")
                report.append("")

        # Files without menu mapping
        report.append("\n## ASPX FILES NOT IN SITEMAP")
        report.append("-" * 100)
        report.append("(These are supporting pages like _New, _Edit, _Delete, _Print, etc.)")
        report.append("")

        menu_files = set(item['file'] for item in self.menu_items if item['file'])

        for module in sorted(self.aspx_files.keys()):
            unmapped = [f for f in self.aspx_files[module] if f['file'] not in menu_files]

            if unmapped:
                report.append(f"\n### {module} ({len(unmapped)} files)")

                # Group by type
                by_type = defaultdict(list)
                for f in unmapped:
                    if '_New' in f['file']:
                        by_type['Create'].append(f['file'])
                    elif '_Edit' in f['file']:
                        by_type['Edit'].append(f['file'])
                    elif '_Delete' in f['file']:
                        by_type['Delete'].append(f['file'])
                    elif '_Print' in f['file']:
                        by_type['Print'].append(f['file'])
                    elif 'Dashboard' in f['file']:
                        by_type['Dashboard'].append(f['file'])
                    else:
                        by_type['Other'].append(f['file'])

                for type_name in ['Dashboard', 'Create', 'Edit', 'Delete', 'Print', 'Other']:
                    if type_name in by_type:
                        report.append(f"  {type_name}: {len(by_type[type_name])} files")

        return "\n".join(report)

    def run(self):
        """Run complete audit"""
        print("Parsing Web.sitemap...")
        self.parse_sitemap()

        print("Scanning .aspx files...")
        self.scan_aspx_files()

        print("Scanning Django views...")
        self.scan_django_views()

        print("Scanning Django URLs...")
        self.scan_django_urls()

        print("Generating report...")
        report = self.generate_report()

        # Save report
        report_file = DJANGO_PATH / "MIGRATION_AUDIT_REPORT.md"
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\nReport saved to: {report_file}")
        print("\n" + "=" * 100)
        print(report[:2000] + "\n...\n(See full report in MIGRATION_AUDIT_REPORT.md)")

if __name__ == "__main__":
    auditor = MigrationAuditor()
    auditor.run()
