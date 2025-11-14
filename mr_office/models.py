"""
MR Office Module Models

This module handles document/file management for various modules in the ERP system.
Stores files in binary format with metadata (filename, size, content type).
"""

from django.db import models


class Tblmroffice(models.Model):
    """
    MR Office - Document/File Storage

    Stores files and documents for different modules in the ERP system.
    Files are stored as binary data with associated metadata.
    """

    # Module choices for categorization
    MODULE_CHOICES = [
        (1, 'Inventory'),
        (2, 'Accounts'),
        (3, 'Sales'),
        (4, 'Purchase'),
        (5, 'HR'),
        (6, 'Project Management'),
        (7, 'Quality Control'),
        (8, 'MIS'),
        (9, 'General'),
    ]

    id = models.AutoField(db_column='Id', primary_key=True)
    sysdate = models.CharField(db_column='SysDate', max_length=50, blank=True, null=True)
    systime = models.CharField(db_column='SysTime', max_length=50, blank=True, null=True)
    compid = models.IntegerField(db_column='CompId', blank=True, null=True)
    sessionid = models.CharField(db_column='SessionId', max_length=50, blank=True, null=True)
    finyearid = models.IntegerField(db_column='FinYearId', blank=True, null=True)
    formodule = models.IntegerField(db_column='ForModule', blank=True, null=True)
    format = models.TextField(db_column='Format', blank=True, null=True)
    filename = models.TextField(db_column='FileName', blank=True, null=True)
    size = models.TextField(db_column='Size', blank=True, null=True)
    contenttype = models.TextField(db_column='ContentType', blank=True, null=True)
    data = models.BinaryField(db_column='Data', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblMROffice'
        verbose_name = 'MR Office Document'
        verbose_name_plural = 'MR Office Documents'
        ordering = ['-id']

    def __str__(self):
        if self.filename:
            return f"{self.filename} ({self.get_module_display()})"
        return f"Document {self.id}"

    def get_module_display(self):
        """Get human-readable module name"""
        module_dict = dict(self.MODULE_CHOICES)
        return module_dict.get(self.formodule, 'Unknown')

    @property
    def file_size_display(self):
        """Return human-readable file size"""
        if not self.size:
            return "Unknown"
        try:
            size_bytes = int(self.size)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        except (ValueError, TypeError):
            return self.size

    @property
    def has_file(self):
        """Check if file data exists"""
        return bool(self.data)

    @property
    def file_extension(self):
        """Get file extension from filename"""
        if self.filename and '.' in self.filename:
            return self.filename.split('.')[-1].upper()
        return 'Unknown'

