"""
MR Office Module Forms
Converted from: aaspnet/Module/MROffice/Transactions/MROffice.aspx
"""

from django import forms
from .models import Tblmroffice


class MROfficeDocumentForm(forms.ModelForm):
    """
    Form for uploading documents to MR Office
    Handles file upload with module selection and format/document name
    """

    formodule = forms.TypedChoiceField(
        coerce=int,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
        }),
        label="For Module"
    )

    format = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Enter format/document name'
        }),
        label="Format/Document"
    )

    file_upload = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.txt,.csv'
        }),
        label="Attachment",
        help_text='Supported formats: PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, TXT, CSV (Max 10MB)'
    )

    class Meta:
        model = Tblmroffice
        fields = ['formodule', 'format']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate module choices from Tblmroffice.MODULE_CHOICES
        self.fields['formodule'].choices = Tblmroffice.MODULE_CHOICES

    def save(self, commit=True, user=None, request=None):
        """
        Save the form with file data
        Handles file upload and stores binary data in database
        """
        instance = super().save(commit=False)

        # Handle file upload
        if 'file_upload' in self.files:
            uploaded_file = self.files['file_upload']
            instance.filename = uploaded_file.name
            instance.size = str(uploaded_file.size)
            instance.contenttype = uploaded_file.content_type
            instance.data = uploaded_file.read()

        # Set audit fields
        if request:
            from datetime import datetime
            now = datetime.now()
            instance.sysdate = now.strftime('%d-%m-%Y')
            instance.systime = now.strftime('%H:%M:%S')
            instance.sessionid = str(request.user.id)
            instance.compid = request.session.get('compid', 1)
            instance.finyearid = request.session.get('finyearid', 1)

        if commit:
            instance.save()

        return instance
