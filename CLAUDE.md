# CLAUDE.md

## ⚠️ CRITICAL: Anti-Hallucination Protocol

**BEFORE doing ANYTHING: READ actual code files. NEVER assume.**

### Core Rules

**NEVER:**
- ❌ Assume Django conventions without verification
- ❌ Confuse `aaspnet/` (ASP.NET legacy) with Django code
- ❌ Guess URLs, paths, or implementations
- ❌ Use "typically" or "usually" without code proof

**ALWAYS:**
- ✅ Read files using Read/Grep/Glob before answering
- ✅ Check existing implementations first
- ✅ Show file paths and line numbers in responses
- ✅ Ask if uncertain

**Example:**
```
❌ "Login is at /accounts/login/"
✅ "Let me check..." [reads urls.py] "Login is at /login/ per erp/urls.py:25"
```

**ASP.NET vs Django:**
- `aaspnet/` = Legacy reference (.aspx files)
- Root apps = Django implementation (.py files)

---

## Project: SAPL/Cortex ERP

ASP.NET WebForms → Django 5.2 + HTMX + Tailwind CSS migration.

**Critical:** Production database (280 tables). Models use `managed = False`. **NEVER run migrations.**

---

## Commands

```bash
# Dev server
python manage.py runserver

# Tests
pytest tests/e2e -v
pytest tests/playwright/ -v --headed
pytest -m smoke|htmx|crud
```

---

## Structure

```
erp/              # Django project (settings.py, urls.py)
core/             # Mixins, forms, base template
  mixins.py       # READ THIS FIRST - reusable view mixins
sys_admin/        # System admin module
sales_distribution/
inventory/
accounts/
[...14 more modules...]
aaspnet/          # ASP.NET reference (DO NOT use for Django)
```

**Each module:**
```
app/
  models.py       # managed=False
  views.py        # Uses core mixins
  forms.py        # Tailwind + HTMX
  urls.py
  services.py     # Business logic
  templates/app/
    partials/     # HTMX responses
```

---

## Key Patterns

### 1. Models (Read-Only)
```python
class SdCustMaster(models.Model):
    salesid = models.AutoField(db_column='SalesId', primary_key=True)
    class Meta:
        managed = False
        db_table = 'SD_Cust_master'
```
- DB columns: PascalCase
- Django fields: lowercase
- Map via `db_column`

### 2. Audit Fields (Required)
```python
obj.sysdate = datetime.now().strftime('%d-%m-%Y')
obj.systime = datetime.now().strftime('%H:%M:%S')
obj.sessionid = str(request.user.id)
obj.compid = request.session.get('compid', 1)
obj.finyearid = request.session.get('finyearid', 1)
```

### 3. Core Mixins (Use These)
- `BaseListViewMixin` - Search, HTMX, pagination
- `BaseCreateViewMixin` / `BaseUpdateViewMixin` / `BaseDeleteViewMixin`
- `CompanyFinancialYearMixin` - Auto-filter by company/year
- `HTMXResponseMixin` - Partial vs full page responses

See `core/mixins.py` and `core/CRUD_PATTERNS.md`

### 4. HTMX (Replaces PostBack)
```python
# Dual response
if request.headers.get('HX-Request'):
    return render(request, 'partials/form.html', ctx)
return render(request, 'full_page.html', ctx)
```

### 5. Service Layer
Extract business logic to `services.py`, keep views thin.

### 6. URLs
```python
path('customer/', CustomerListView.as_view(), name='customer-list')
path('customer/create/', ..., name='customer-create')
path('customer/<int:pk>/edit/', ..., name='customer-edit')
```
Use kebab-case: `{resource}-{action}`

---

## Tech Stack

- Django 5.2, SQLite
- Tailwind 3.x, HTMX 1.9, Alpine.js
- pytest, Playwright

---

## Workflow

**Adding Features:**
1. Never create models (use existing)
2. Check `core/mixins.py` first
3. Follow `sys_admin/` or `sales_distribution/` patterns
4. Extract logic to `services.py`
5. Use HTMX + Tailwind

**Common Pitfalls:**
- Running migrations
- `managed = True`
- Forgetting audit fields
- Duplicating mixin functionality
- Inline styles instead of Tailwind

---

## Migration Status

**Done:** sys_admin, sales_distribution, material_management, material_planning, material_costing
**In Progress:** inventory, accounts, human_resource
**Pending:** quality_control, project_management, machinery, mis, mr_office, daily_report_system, design

---

## References

- `README.md` - Full ASP.NET→Django migration guide
- `core/mixins.py` - Reusable patterns (CRITICAL)
- `core/CRUD_PATTERNS.md` - CRUD approaches
- `hallucinations.md` - Best practices

---

## Credentials

**ASP.NET (Legacy):**
- URL: http://localhost/NewERP/
- User: sapl0003
- Pass: Sapl@0003

**Django:**
- URL: http://localhost:8000/
- User: admin
- Pass: admin

---

## Playwright Best Practices

**Avoid large responses:**
- ✅ Use `browser_take_screenshot` (not `browser_snapshot`)
- ✅ Use `browser_evaluate` for targeted data extraction
- ✅ Use `browser_console_messages` / `browser_network_requests`

**Session management:**
```
1. browser_close()
2. browser_navigate(url)
3. browser_wait_for({time: 2})
4. browser_evaluate() or browser_take_screenshot()
5. browser_close()
```

**If stuck:** `taskkill /F /IM chrome.exe /T 2>nul`

**Isolated mode configured:** `--isolated` flag prevents profile locks.

---

## Critical Reminders

1. **NEVER RUN MIGRATIONS** - Schema is fixed
2. **READ core/mixins.py FIRST** - Don't duplicate
3. **POPULATE AUDIT FIELDS** - Always
4. **CHECK CODE BEFORE SUGGESTING** - No assumptions
5. **aaspnet/ = REFERENCE ONLY** - Don't implement from it
