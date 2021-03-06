__author__ = 'Lothilius'

from triage_tickets.TicketList import TicketList
from tableau_data_publisher.data_assembler import TDEAssembler
from bv_authenticate.Authentication import Authentication as auth
from tableau_data_publisher.data_publisher import publish_data
from misc_helpers.data_manipulation import correct_date_dtype
import sys
import pandas as pd
from send_email.OutlookConnection import OutlookConnection as outlook


try:
    # Get tickets from the HDT view
    tickets = TicketList(helpdesk_que='YtoD-BizApps', with_resolution=True)
    tickets = tickets.reformat_as_dataframe(tickets)
    try:
        tickets.drop('ATTACHMENTS', axis=1, inplace=True)
    except:
        print 'No Attachments column.'
    tickets = correct_date_dtype(tickets, date_time_format='%Y-%m-%d %H:%M:%S')

    # Package in to a tde file
    data_file = TDEAssembler(data_frame=tickets, extract_name='BizApps_HDT')
    # Set values for publishing the data.
    file_name = str(data_file)
    server_url, username, password, site_id, data_source_name, project = auth.tableau_publishing('HDT')

    publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    outlook.send_email(to='martin.valenzuela@bazaarvoice.com',
                       subject='HDT-Data update complete', body='HDT-Data update complete')

except ValueError:
    error_result = "Unexpected AttributeError: %s, %s"\
                   % (sys.exc_info()[0], sys.exc_info()[1])
    subject = 'Error with Tableau refresh script'
    print error_result
    outlook.send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)