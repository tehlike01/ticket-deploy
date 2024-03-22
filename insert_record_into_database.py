import xmlrpc.client
import requests
import get_ticket_from_api
from datetime import datetime
from operator import itemgetter

# Configuration
url = 'http://localhost:8069'
db = 'odoo16'  # Replace with your actual database name
username = 'admin'  # Replace with your actual username
password = 'admin'  # Replace with the user's password

# Common login service
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})

# Object service
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Log file
log_file = open("log.txt", "a")

#------GETTING ALL THE TICKET NUMBERS AGAINST CUSTOMER ID-------

def get_tickets_by_customer_id(customer_id):
    domain = [['customer_id', '=', customer_id]]
    records = models.execute_kw(db, uid, password, 'help.ticket', 'search_read', [domain], {'fields': ['name']})
    ticket_names = [record['name'] for record in records]
    return ticket_names

#-----------------GET ALL USERS NAME------------------
def get_all_author_names():
    if uid:
        # Retrieve all author names from the database
        author_names = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                         [[('name', '!=', False)]], {'fields': ['name']})
        return [author['name'] for author in author_names]
    else:
        log_file.write("Failed to authenticate.\n")
        return []

#-----------------GETTING PK ID FROM RES.PARTNER----------------------
def get_id_by_author_name(author_name):
    if uid:
        ids = models.execute_kw(db, uid, password, 'res.partner', 'search',
                                [[('name', '=', author_name)]], {'limit': 1})
        if ids:
            return ids[0] 
        else:
            log_message = "No ticket found for ticket name: {} {}\n".format(author_name, datetime.now())
            log_file.write(log_message)
            return None
    else:
        log_message = "Failed to authenticate. {}\n".format(datetime.now())
        log_file.write(log_message)
        return None

#-----------------GETTING PK ID FROM HELP.TICKET----------------------
def get_id_by_ticket_name(ticket_name):
    if uid:
        ids = models.execute_kw(db, uid, password, 'help.ticket', 'search',
                                [[('name', '=', ticket_name)]], {'limit': 1})
        if ids:
            return ids[0] 
        else:
            log_message = "No ticket found for ticket name: {} {}\n".format(ticket_name, datetime.now())
            log_file.write(log_message)
            return None
    else:
        log_message = "Failed to authenticate. {}\n".format(datetime.now())
        log_file.write(log_message)
        return None

#------------------GETING ALL THE CUSTMER NAME-----------------------
def get_all_customers_name():
    if uid:
        customer_names = models.execute_kw(db, uid, password, 'res.partner', 'search_read',
                                           [[]], {'fields': ['name']})
        if customer_names:
            return [customer['name'] for customer in customer_names]  # Return a list of customer names
        else:
            log_file.write("No customers found.\n")
            return []
    else:
        log_file.write("Failed to authenticate.\n")
        return None

#-------------INSERTING CUSTOMER DETAILS IN RES.PARTNER-----------------
def insert_customer_by_customer_id(customer_id):
    customer_details = get_ticket_from_api.get_customer_details(customer_id)
    
    existing_customer_names = set(get_all_customers_name())

    for customer_data in customer_details:
        # Check if the customer already exists
        if str(customer_data['name']) in existing_customer_names:
            log_message = "Customer with name '{}' already exists. Skipping insertion. {}\n".format(customer_data['name'], datetime.now())
            print(log_message)
            log_file.write(log_message)
        else:
            # Insert the customer record into the database
            record_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [customer_data])
            log_message = "Customer Created with ID: {} {}\n".format(record_id, datetime.now())
            print(log_message)
            log_file.write(log_message)

    log_file.flush()

#----------------------INSERTING RECORD------------------------------
def insert_tickets_by_customer_id(customer_id):
    tickets_data = get_ticket_from_api.get_all_tickets(customer_id)
    
    for ticket_data in tickets_data:
        cust_name = get_ticket_from_api.get_customer_name(ticket_data['name'])
        existing_ticket_names = set(get_tickets_by_customer_id(get_id_by_author_name(cust_name)))
        customer_id = get_id_by_author_name(cust_name)
        # Check if the ticket name already exists
        if str(ticket_data['name']) in existing_ticket_names:
            log_message = "Ticket with name '{}' already exists. Skipping insertion. {}\n".format(ticket_data['name'], datetime.now())
            print(log_message)
            log_file.write(log_message)
        else:
            if ticket_data['tags'] == 'New': 
                stage_id = 1
            elif ticket_data['tags'] == 'Resolved':  
                stage_id = 4
            else:
                stage_id = 3
            ticket_val = {
                    'customer_id': get_id_by_author_name(cust_name),
                    'subject': ticket_data['subject'],
                    'description': ticket_data['description'],
                    'name': ticket_data['name'],
                    'customer_name': ticket_data['customer_name'],
                    'stage_id' : stage_id,
                }
            # Insert the ticket record into the database
            record_id = models.execute_kw(db, uid, password, 'help.ticket', 'create', [ticket_val])
            log_message = "Ticket Created with ID: {} {}\n".format(record_id, datetime.now())
            print(log_message)
            log_file.write(log_message)

    log_file.flush()

#-----------------UPDATING THE TICKET RECORD--------------------------
def update_tickets_by_customer_id(customer_id):
    tickets_data = get_ticket_from_api.get_all_tickets(customer_id)
    
    for ticket_data in tickets_data:
        cust_name = get_ticket_from_api.get_customer_name(ticket_data['name'])
        existing_ticket_names = set(get_tickets_by_customer_id(get_id_by_author_name(cust_name)))
        # Check if the ticket name already exists
        if str(ticket_data['name']) in existing_ticket_names:
            ticket_id = get_id_by_ticket_name(ticket_data['name'])
            existing_ticket = models.execute_kw(db, uid, password, 'help.ticket', 'read', [[ticket_id]])[0]
            # Compare existing values with new values
            changes = {}
            if ticket_data['tags'] == 'New' and existing_ticket['stage_id'][0] != 1: 
                changes['stage_id'] = 1
            elif ticket_data['tags'] == 'Resolved' and existing_ticket['stage_id'][0] != 4:  
                changes['stage_id'] = 4
            elif ticket_data['tags'] != 'New' and ticket_data['tags'] != 'Resolved' and existing_ticket['stage_id'][0] != 3:
                changes['stage_id'] = 3
            
            if ticket_data['subject'] != existing_ticket['subject']:
                changes['subject'] = ticket_data['subject']
            if ticket_data['description'] != existing_ticket['description']:
                changes['description'] = ticket_data['description']
            if ticket_data['customer_name'] != existing_ticket['customer_name']:
                changes['customer_name'] = ticket_data['customer_name']
                
            if changes:
                # Update the ticket record in the database
                models.execute_kw(db, uid, password, 'help.ticket', 'write', [[ticket_id], changes])
                log_message = "Ticket Updated with ID: {} {}\n".format(ticket_id, datetime.now())
                print(log_message)
                log_file.write(log_message)
            else:
                log_message = "No changes detected for Ticket with name '{}'. Skipping update. {}\n".format(ticket_data['name'], datetime.now())
                print(log_message)
                log_file.write(log_message)
        else:
            log_message = "Ticket with name '{}' does not exist. Skipping update. {}\n".format(ticket_data['name'], datetime.now())
            print(log_message)
            log_file.write(log_message)

    log_file.flush()

#-----------GET_COMMENT_ID_FROM_MAIL_MESSAGE_DATABASE-------------
def get_comment_ids_by_res_id(res_id):
    domain = [['res_id', '=', res_id]]
    records = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [domain], {'fields': ['comment_id']})
    comment_ids = [record['comment_id'] for record in records]
    return comment_ids

#---------------GET COMMENT ID USING TICKET NUMBER-----------------
def get_comment_id_by_ticket_number(ticket_number, comment_body):
    domain = [['record_name', '=', ticket_number], ['body', '=', comment_body]]
    comment_ids = models.execute_kw(db, uid, password, 'mail.message', 'search', [domain], {'limit': 1})
    return comment_ids if comment_ids else None

#----------------GET ID USING COMMENT ID---------------
def get_id_by_comment_id(comment_id):
    domain = [['comment_id', '=', comment_id]]
    records = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [domain], {'fields': ['id']})
    return {'id': records[0]['id']}

#--------------GET COMMENT DETAILS USING COMMENT ID---------------
def get_comment_data_by_id(comment_id):
    domain = [['comment_id', '=', comment_id]]
    records = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [domain], {'fields': ['subject', 'body', 'author_id']})
    
    if records:
        author_info = records[0]['author_id']
        if isinstance(author_info, list) and len(author_info) >= 2:
            tech = author_info[1] 
        else:
            tech = author_info 
        
        return {
            'subject': records[0]['subject'],
            'body': records[0]['body'],
            'tech': tech,
            "hidden": True,
            "do_not_email": True
        }
    else:
        return None
#--------------GET ALL COMMENT DETAILS USING TICKET NUMBER---------------    
def get_all_comments_by_ticket_number(ticket_number):
    domain = [['record_name', '=', ticket_number]]
    records = models.execute_kw(db, uid, password, 'mail.message', 'search_read', [domain], {'fields': ['subject', 'body', 'author_id','record_name']})
    
    comment_data = []
    for record in records:
        author_info = record['author_id']
        if isinstance(author_info, list) and len(author_info) >= 2:
            tech = author_info[1] 
        else:
            tech = author_info 
        
        comment_info = {
            'ticket_number': record['record_name'],
            'subject': record['subject'],
            'body': record['body'],
            'tech': tech
        }
        comment_data.append(comment_info)

    return comment_data

#-----------------INSERTING COMMENTS------------------
def insert_customer_comments(ticket_number):
    try:
        comments = get_ticket_from_api.get_ticket_comments(ticket_number)
        if comments:
            sorted_comments = sorted(comments, key=itemgetter('date'))
            for comment in sorted_comments:
                # Check if comment ID already exists for the ticket
                comment_id = comment['comment_id']
                existing_comment_ids = [str(cid) for cid in get_comment_ids_by_res_id(get_id_by_ticket_name(ticket_number))]
                if str(comment_id) not in existing_comment_ids:
                    employee_list = get_all_author_names()
                    if comment['tech'] == 'customer-reply':
                         author_id = get_id_by_author_name(get_ticket_from_api.get_customer_name(ticket_number))                    
                    elif comment['tech'] in employee_list:
                         author_id = get_id_by_author_name(comment['tech'])
                    else:
                         author_id = get_id_by_author_name("Syncro System")

                    message_values = {
                        'author_id': author_id,
                        'body': comment['body'],
                        'model': 'help.ticket',
                        'subject': comment['subject'],
                        'comment_id': comment_id,
                        'res_id': get_id_by_ticket_name(ticket_number)
                    }
                    record_id = models.execute_kw(db, uid, password, 'mail.message', 'create', [message_values])
                    log_message = "Comment Created with ID: {} {}\n".format(record_id, datetime.now())
                    log_file.write(log_message)
                    print(log_message)
                else:
                    log_message = "Comment ID {} already exists for ticket number: {} {}\n".format(comment_id, ticket_number, datetime.now())
                    log_file.write(log_message)
                    print(log_message)
        else:
            log_message = "No comments found for ticket number: {} {}\n".format(ticket_number, datetime.now())
            log_file.write(log_message)
            print(log_message)
    except Exception as e:
        log_message = "Error occurred during comment insertion: {} {}\n".format(str(e), datetime.now())
        log_file.write(log_message)
        print(log_message)
insert_customer_comments('4849')
#------------------INSERT ALL THE COMMENTS----------------
def insert_all_customer_comments(customer_id):
    ticket_numbers = get_ticket_from_api.get_all_ticket_numbers(customer_id)
    for ticket_number in ticket_numbers:
        insert_customer_comments(ticket_number)

#---------------------POST COMMENT TO API-------------------------
def log(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{current_time}] {message}"
    print(log_entry)
    log_file.write(log_entry + "\n")

def post_comment(ticket_number):
    log(f"Posting comments for ticket number {ticket_number}")

    # Retrieve comment IDs from the database and Syncro API
    database_comment_ids = get_comment_ids_by_res_id(get_id_by_ticket_name(ticket_number))
    syncro_comment_ids = get_ticket_from_api.get_comment_id(ticket_number)
    syncro_comment_id_list = [str(comment['id']) for comment in syncro_comment_ids]
    # Check if there are comments to post
    comments_to_post = []
    for comment_id in database_comment_ids:
        if comment_id not in syncro_comment_id_list and comment_id is not False:
            comments_to_post.append(comment_id)
    if not comments_to_post:
        log("No new comments to post.")
        return
    
    base_url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }
    params = {
        "number": ticket_number
    }

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        tickets = data.get("tickets", [])
        if tickets:
            ticket_id = tickets[0].get("id")
            comment_url = f"{base_url}/{ticket_id}/comment"

            for comment_id in comments_to_post:
                # Retrieve comment data from the database using the comment ID
                comment_data = get_comment_data_by_id(comment_id)
                id_dict = get_id_by_comment_id(comment_id)
                id = id_dict['id']
                # Post the comment to Syncro
                comment_response = requests.post(comment_url, headers=headers, json=comment_data)
                if comment_response.status_code == 200:
                    comment_info = comment_response.json().get("comment")
                    log(f"Comment ID: {comment_info['id']} posted successfully")
                    cid = {'comment_id' : comment_info['id']}
                    models.execute_kw(db, uid, password, 'mail.message', 'write', [[id], cid])
                    log_message = "Comment Updated with ID: {} {}\n".format(comment_id, datetime.now())
                    print(log_message)
                    log_file.write(log_message)
                else:
                    log(f"Failed to post comment {comment_id}. Status code: {comment_response.status_code}")
                    log("Response text: " + comment_response.text)
        else:
            log("Ticket not found.")
    else:
        log(f"Failed to fetch ticket information. Status code: {response.status_code}")

def post_all_customer_comments(customer_id):
    ticket_numbers = get_ticket_from_api.get_all_ticket_numbers(customer_id)
    for ticket_number in ticket_numbers:
        post_comment(ticket_number)
