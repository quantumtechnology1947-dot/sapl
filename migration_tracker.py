#!/usr/bin/env python3
"""
Migration Tracker - Interactive CLI for tracking migration progress
"""
import csv
import sys
from pathlib import Path
from datetime import datetime

CSV_FILE = Path('/home/user/sapl/aspx_django_mapping.csv')


def load_mappings():
    """Load the CSV mapping file"""
    if not CSV_FILE.exists():
        print("❌ CSV file not found. Run detailed_file_mapping.py first.")
        sys.exit(1)

    mappings = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            mappings.append(row)

    return mappings


def show_statistics():
    """Show migration statistics"""
    mappings = load_mappings()

    total = len(mappings)
    app_exists = sum(1 for m in mappings if m['App Exists'] == 'Yes')
    migrated = sum(1 for m in mappings if m['Migration Status'] == 'Likely Migrated')
    partially = sum(1 for m in mappings if m['Migration Status'] == 'Partially Migrated')
    tested = sum(1 for m in mappings if m['Playwright Test'] == 'Yes')

    print("\n" + "=" * 80)
    print("MIGRATION STATISTICS")
    print("=" * 80)
    print(f"\n📊 Total Files: {total}")
    print(f"✅ Apps Created: {app_exists}/{total} ({app_exists/total*100:.1f}%)")
    print(f"✅ Fully Migrated: {migrated}/{total} ({migrated/total*100:.1f}%)")
    print(f"⚠️  Partially Migrated: {partially}/{total} ({partially/total*100:.1f}%)")
    print(f"🧪 With Tests: {tested}/{total} ({tested/total*100:.1f}%)")
    print(f"❌ Remaining: {total - migrated}/{total} ({(total-migrated)/total*100:.1f}%)\n")


def show_module_progress(module_name=None):
    """Show progress for a specific module or all modules"""
    mappings = load_mappings()

    # Group by module
    from collections import defaultdict
    by_module = defaultdict(list)

    for m in mappings:
        by_module[m['Django App']].append(m)

    if module_name:
        if module_name not in by_module:
            print(f"❌ Module '{module_name}' not found.")
            print(f"\nAvailable modules: {', '.join(sorted(by_module.keys()))}")
            return

        modules_to_show = {module_name: by_module[module_name]}
    else:
        modules_to_show = by_module

    print("\n" + "=" * 80)
    print("MODULE PROGRESS")
    print("=" * 80)

    for module in sorted(modules_to_show.keys()):
        files = modules_to_show[module]
        total = len(files)
        app_exists = files[0]['App Exists'] == 'Yes'
        migrated = sum(1 for f in files if f['Migration Status'] == 'Likely Migrated')
        partially = sum(1 for f in files if f['Migration Status'] == 'Partially Migrated')
        tested = sum(1 for f in files if f['Playwright Test'] == 'Yes')

        progress = (migrated / total * 100) if total > 0 else 0
        test_coverage = (tested / total * 100) if total > 0 else 0

        status_icon = '✅' if app_exists else '❌'
        progress_bar = create_progress_bar(progress)

        print(f"\n{status_icon} {module}")
        print(f"   Files: {total} | Migrated: {migrated} | Partially: {partially} | Tests: {tested}")
        print(f"   Progress: {progress_bar} {progress:.1f}%")
        print(f"   Test Coverage: {test_coverage:.1f}%")

        if module_name and total <= 20:
            # Show individual files for small modules
            print(f"\n   Files:")
            for f in files[:20]:
                status = {
                    'Likely Migrated': '✅',
                    'Partially Migrated': '⚠️',
                    'Not Migrated': '❌',
                    'Not Started': '⏳',
                    'App Not Created': '🚫',
                }.get(f['Migration Status'], '❓')
                test = '🧪' if f['Playwright Test'] == 'Yes' else '  '
                filename = f['ASPX File Path'].split('/')[-1]
                print(f"      {status} {test} {filename}")


def create_progress_bar(percent, width=20):
    """Create a text-based progress bar"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f'[{bar}]'


def search_files(keyword):
    """Search for files containing keyword"""
    mappings = load_mappings()
    keyword_lower = keyword.lower()

    results = [
        m for m in mappings
        if keyword_lower in m['ASPX File Path'].lower()
        or keyword_lower in m['ASP.NET Module'].lower()
        or keyword_lower in m['Django App'].lower()
    ]

    print(f"\n🔍 Found {len(results)} files matching '{keyword}':\n")

    for r in results[:50]:  # Limit to 50 results
        status = {
            'Likely Migrated': '✅',
            'Partially Migrated': '⚠️',
            'Not Migrated': '❌',
            'Not Started': '⏳',
            'App Not Created': '🚫',
        }.get(r['Migration Status'], '❓')

        print(f"{status} {r['ASPX File Path']}")
        print(f"   → Django: {r['Django App']} | Status: {r['Migration Status']}")

    if len(results) > 50:
        print(f"\n... and {len(results) - 50} more results")


def mark_as_migrated(aspx_path):
    """Mark a file as migrated in the CSV"""
    mappings = load_mappings()

    # Find the file
    found = False
    for m in mappings:
        if m['ASPX File Path'] == aspx_path:
            m['Migration Status'] = 'Likely Migrated'
            m['Notes'] = f"Manually marked as migrated on {datetime.now().strftime('%Y-%m-%d')}"
            found = True
            break

    if not found:
        print(f"❌ File not found: {aspx_path}")
        return

    # Write back to CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = list(mappings[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mappings)

    print(f"✅ Marked as migrated: {aspx_path}")


def show_help():
    """Show help message"""
    print("""
Migration Tracker - Interactive CLI

Usage:
    python migration_tracker.py stats              Show overall statistics
    python migration_tracker.py modules             Show all module progress
    python migration_tracker.py module <name>       Show specific module details
    python migration_tracker.py search <keyword>    Search for files
    python migration_tracker.py mark <path>         Mark file as migrated
    python migration_tracker.py help                Show this help

Examples:
    python migration_tracker.py stats
    python migration_tracker.py module sales_distribution
    python migration_tracker.py search customer
    python migration_tracker.py mark "Module/SalesDistribution/Masters/CustomerMaster_New.aspx"
    """)


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == 'stats':
        show_statistics()

    elif command == 'modules':
        show_module_progress()

    elif command == 'module':
        if len(sys.argv) < 3:
            print("❌ Please specify a module name")
            return
        module_name = sys.argv[2]
        show_module_progress(module_name)

    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Please specify a search keyword")
            return
        keyword = ' '.join(sys.argv[2:])
        search_files(keyword)

    elif command == 'mark':
        if len(sys.argv) < 3:
            print("❌ Please specify the ASPX file path")
            return
        aspx_path = ' '.join(sys.argv[2:])
        mark_as_migrated(aspx_path)

    elif command in ['help', '--help', '-h']:
        show_help()

    else:
        print(f"❌ Unknown command: {command}")
        show_help()


if __name__ == '__main__':
    main()
