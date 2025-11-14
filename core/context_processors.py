"""
Context processors for core app.
Makes common data available to all templates.
"""

def financial_years(request):
    """
    Add available financial years to template context.
    Auto-selects a financial year with data if current selection has no data.
    """
    if request.user.is_authenticated:
        try:
            from sys_admin.models import TblfinancialMaster
            from inventory.models import TblinvInwardMaster
            from django.db.models import Count
            
            # Get company ID from session
            compid = request.session.get('compid', 1)
            
            # Get all financial years for the company
            financial_years = TblfinancialMaster.objects.filter(
                compid=compid
            ).order_by('-finyearid')
            
            # Get current financial year from session
            current_finyearid = request.session.get('finyearid')

            # Get the current financial year object
            current_financial_year = None
            if current_finyearid:
                current_financial_year = TblfinancialMaster.objects.filter(
                    finyearid=current_finyearid
                ).first()

            # Auto-switch to latest active FY if current one is inactive or doesn't exist
            if not current_financial_year or current_financial_year.flag != 1:
                # Get latest active financial year (highest finyearid with flag=1)
                latest_active_fy = TblfinancialMaster.objects.filter(
                    compid=compid,
                    flag=1
                ).order_by('-finyearid').first()

                if latest_active_fy:
                    current_finyearid = latest_active_fy.finyearid
                    current_financial_year = latest_active_fy
                    request.session['finyearid'] = current_finyearid
                else:
                    # No active FY found - try to find one with data
                    fy_with_data = TblinvInwardMaster.objects.filter(
                        compid=compid
                    ).values('finyearid').annotate(
                        count=Count('id')
                    ).order_by('-finyearid').first()

                    if fy_with_data:
                        # Use FY with data
                        current_finyearid = fy_with_data['finyearid']
                        current_financial_year = TblfinancialMaster.objects.filter(
                            finyearid=current_finyearid
                        ).first()
                        request.session['finyearid'] = current_finyearid
                    elif not current_financial_year:
                        # Last resort: get the latest FY
                        latest_fy = TblfinancialMaster.objects.filter(
                            compid=compid
                        ).order_by('-finyearid').first()
                        if latest_fy:
                            current_finyearid = latest_fy.finyearid
                            current_financial_year = latest_fy
                            request.session['finyearid'] = current_finyearid

            return {
                'available_financial_years': financial_years,
                'current_finyearid': current_finyearid,
                'current_financial_year': current_financial_year,
            }
        except:
            pass
    
    return {
        'available_financial_years': [],
        'current_finyearid': None,
    }

