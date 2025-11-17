# BINARY ISSUES - DETAILED EXAMPLES AND LOCATIONS

## File-by-File Issues Found

### ISSUE 1: MIXED LINE ENDINGS

#### Grouping_Events.csv
- **Path**: csv_data/Grouping_Events.csv
- **Size**: 6,606 bytes
- **Issue**: Mixed line endings (CRLF + LF)
- **Details**:
  - Lines with CRLF (Windows): 74
  - Lines with LF (Unix): 13
  - Probable cause: File created on Windows, edited on Unix/Linux

#### SD_Cust_master.csv  
- **Path**: csv_data/SD_Cust_master.csv
- **Size**: 131,072 bytes (128 KB)
- **Issue**: Mixed line endings (mostly CRLF, few LF)
- **Details**:
  - Lines with CRLF: 8
  - Lines with LF: 2
  - Issue much less severe than Grouping_Events.csv

---

### ISSUE 2: NON-ASCII UTF-8 CHARACTERS

#### tblDG_Item_Master.csv - MOST CRITICAL
- **Path**: csv_data/tblDG_Item_Master.csv
- **Size**: 17,058,251 bytes (16.3 MB)
- **Issue**: Non-ASCII UTF-8 encoded characters
- **Character Breakdown**:
  - Non-breaking space (U+00A0): 328 occurrences
  - En dash (U+2013): 72 occurrences
  - Em dash (U+2014): 3 occurrences
- **Total non-ASCII bytes**: 1,201 out of 17,058,251 (0.007%)
- **Where These Characters Are**: Product descriptions, names, specifications
- **Impact**: Export/comparison with ASCII-only systems will fail

#### tblMM_Supplier_master.csv
- **Path**: csv_data/tblMM_Supplier_master.csv
- **Size**: 722,144 bytes (705 KB)
- **Issue**: Non-ASCII UTF-8 characters
- **Characters**: En dash (U+2013) - 157 occurrences
- **Total non-ASCII bytes**: 534 out of 722,144 (0.074%)

#### tblACC_SalesInvoice_Master.csv
- **Path**: csv_data/tblACC_SalesInvoice_Master.csv
- **Size**: 476,688 bytes (466 KB)
- **Issue**: Non-ASCII UTF-8 characters
- **Characters**:
  - En dash (U+2013): 82 occurrences
  - Non-breaking space (U+00A0): 2 occurrences
- **Total non-ASCII bytes**: 250

#### Other Files with Non-ASCII
- SD_Cust_Enquiry_Master.csv: 194 non-ASCII bytes
- SD_Cust_WorkOrder_Master.csv: 164 non-ASCII bytes
- SD_Cust_WorkOrder_Products_Details.csv: 194 non-ASCII bytes


### ISSUE 3: EMPTY BINARY COLUMNS

#### tblDG_Item_Master.csv
- **Path**: csv_data/tblDG_Item_Master.csv
- **Size**: 17,058,251 bytes
- **Binary Columns**: FileData, AttData, FileName, FileSize, ContentType, AttContentType
- **Status**: ALL CELLS EMPTY (verified across 100 rows)
- **Verdict**: Attachment feature not implemented or data purged
- **Action**: No cleaning needed

#### tblACC_BillBooking_Attach_Master.csv
- **Path**: csv_data/tblACC_BillBooking_Attach_Master.csv
- **Size**: 36,256 bytes
- **Binary Columns**: FileData, FileName, FileSize, ContentType
- **Status**: ALL CELLS EMPTY
- **Verdict**: Safe

#### SD_Cust_Enquiry_Attach_Master.csv
- **Path**: csv_data/SD_Cust_Enquiry_Attach_Master.csv
- **Size**: 859 bytes
- **Binary Columns**: FileData, FileName, FileSize, ContentType
- **Status**: ALL CELLS EMPTY
- **Verdict**: Safe


## SPECIAL CHARACTERS EXPLANATION

### Non-breaking Space (U+00A0)
- Looks like regular space but prevents line wrapping
- Used in product names, titles, numbers
- Problematic for: ASCII-only systems, export/import

### En Dash (U+2013)
- Typographic dash: "–" (longer than hyphen)
- Used in ranges: "2020–2024"
- Looks professional but breaks ASCII parsers
- Problematic for: Legacy ASP.NET system, ASCII-only tools

### Em Dash (U+2014)
- Longer dash: "—"
- Used for emphasis
- Breaks ASCII parsers


## ENCODING VERIFICATION RESULTS

All files verified as VALID UTF-8:
- No invalid UTF-8 sequences detected
- No null bytes (0x00)
- No UTF-8 BOM markers (0xEF 0xBB 0xBF)
- No control characters (0x00-0x08, 0x0B-0x0C, 0x0E-0x1F)


## SUMMARY TABLE

| File | Size | Issue | Severity |
|------|------|-------|----------|
| tblDG_Item_Master.csv | 16.3 MB | Non-ASCII (1,201 bytes) | MEDIUM |
| tblMM_Supplier_master.csv | 705 KB | Non-ASCII (534 bytes) | MEDIUM |
| tblACC_SalesInvoice_Master.csv | 466 KB | Non-ASCII (250 bytes) | MEDIUM |
| Grouping_Events.csv | 6.6 KB | Mixed line endings | LOW |
| SD_Cust_master.csv | 128 KB | Mixed line endings | LOW |
| SD_Cust_Enquiry_Master.csv | 464 KB | Non-ASCII (194 bytes) | LOW |
| SD_Cust_WorkOrder_Master.csv | 459 KB | Non-ASCII (164 bytes) | LOW |


## NEXT STEPS

1. **Normalize non-ASCII characters** in high-impact files
2. **Fix line endings** in 2 files (quick 15-minute task)
3. **Test** Django import/export workflow
4. **Document** UTF-8 handling requirements


