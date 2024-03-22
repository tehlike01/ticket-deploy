import requests
from datetime import datetime

def get_all_tickets(customer_id):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "customer_id": customer_id
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        tickets_data = []
        for ticket in data.get("tickets", []):
            ticket_status = ticket.get('resolved_at')
            ticket_number = ticket.get("number")
            if ticket_status is None:
                ticket_id = ticket["id"]
                customer_id = ticket["customer_id"]
                ticket_subject = ticket["subject"]
                created_at = ticket["created_at"]
                created_at_datetime = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%S.%f%z')
                customer_name = ticket["customer_business_then_name"]
                due_date = ticket["due_date"]
                resolved_at = ticket["resolved_at"]
                resolved_at_datetime = None
                if resolved_at:
                    resolved_at_datetime = datetime.strptime(resolved_at, '%Y-%m-%dT%H:%M:%S.%f%z')
                problem_type = ticket["problem_type"]
                status = ticket["status"]
                updated_at = ticket["updated_at"]
                comments = ticket.get("comments", [])
                for comment in comments:
                    if comment["subject"] == "Initial Issue":
                        initial_issue_description = comment["body"]
                        break
                if status == 'New':
                    stage_id = 1
                elif status == 'Resolved':
                    stage_id = 4
                else:
                    stage_id = 3
                ticket_values = {
                    'Ticket_id' : ticket_id,
                    'customer_id': customer_id,
                    'subject': ticket_subject,
                    'description': initial_issue_description,
                    'name': ticket_number,
                    'customer_name': customer_name,
                    'stage_id' : stage_id,
                    'due_date': due_date,
                    'resolved_at': resolved_at_datetime,
                    'problem_type': problem_type,
                    'tags': status,
                    'updated_at': updated_at
                }
                tickets_data.append(ticket_values)
        return tickets_data
    else:
        print(f"Error: {response.status_code} - {response.text}")
#print(get_all_tickets(26415261))
#---------------FETCHING THE COMMENTS--------------

def get_ticket_comments(ticket_number):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "number": ticket_number
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        comments_data = []

        for ticket in data.get("tickets", []):
            comments = ticket.get("comments", [])
            for comment in comments:
                    ticket_id = comment.get("ticket_id")
                    comment_number = comment.get("id")
                    comment_subject = comment.get("subject")
                    comment_body = comment.get("body")
                    comment_tech = comment.get("tech")
                    comment_datetime = comment.get("created_at")   
                    comments_data.append({
                        "ticket_id" : ticket_id,
                        "ticket_number": ticket_number, 
                        "comment_id": comment_number,
                        "tech" :comment_tech,
                        "subject": comment_subject,
                        "date" : comment_datetime,
                        "body": comment_body,
                    })

        return comments_data
    else:
        print(f"Error: {response.status_code} - {response.text}")
print(get_ticket_comments('4849'))
#--------------FETCHING COMMENT ID FROM TICKET--------------
def get_comment_id(ticket_number):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "number": ticket_number
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        comments_id = []

        for ticket in data.get("tickets", []):
            comments = ticket.get("comments", [])
            for comment in comments:
                    comment_id = comment.get("id")   
                    comments_id.append({
                        "id": comment_id,
                    })

        return comments_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
#---------------FETCHING CUSTOMER DETAILS-------------------

def get_customer_details(customer_id):
    url = "https://itmsc.syncromsp.com/api/v1/customers"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "id": customer_id
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        customer_data = []

        for customer in data.get("customers", []):
            customer_name = customer.get("fullname")
            customer_email = customer.get("email")
            customer_phone = customer.get("phone")

            customer_data.append({
                "id": customer_id,
                "name": customer_name,
                "email": customer_email,
                "phone": customer_phone
            })

        return customer_data
    else:
        print(f"Error: {response.status_code} - {response.text}")

#----------FETCHING CUSTOMER ID----------------

def get_customer_id(ticket_number):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "number": ticket_number
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        
        if data.get("tickets"):
            return data["tickets"][0]["customer_id"]
        else:
            print("Error: Ticket number not found.")
            return None

    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

#---------------GET CUSTOMER NAME-------------------
def get_customer_name(ticket_number):
    customer_id = get_customer_id(ticket_number)
    if customer_id:
        url = "https://itmsc.syncromsp.com/api/v1/customers"
        headers = {
            "accept": "application/json",
            "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
        }

        params = {
            "id": customer_id
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
        
            for customer in data.get("customers", []):
                customer_name = customer.get("fullname")
                return customer_name
        else:
            print(f"Error: {response.status_code} - {response.text}")
    else:
        print("Error: Customer ID not found.")

#--------------GET TICKET NUMBERS USING CUSTOMER ID----------------
def get_all_ticket_numbers(customer_id):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "customer_id": customer_id
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        ticket_numbers = []
        for ticket in data.get("tickets", []):
            ticket_status = ticket.get('resolved_at')
            ticket_number = ticket.get("number")
            if ticket_status is None:
                ticket_numbers.append(ticket_number)
        return ticket_numbers
    else:
        print(f"Error: {response.status_code} - {response.text}")

#--------------------GETTING TECH FROM COMMENTS--------------------

def get_ticket_tech(ticket_number):
    url = "https://itmsc.syncromsp.com/api/v1/tickets"
    headers = {
        "accept": "application/json",
        "Authorization": "T550d8906964787416-eccd4512992739e6032c09c3b47a28f0"
    }

    params = {
        "number": ticket_number
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        comments_data = []

        for ticket in data.get("tickets", []):
            comments = ticket.get("comments", [])
            for comment in comments:
                comment_tech = comment.get("tech")
                if comment_tech:
                    comments_data.append(comment_tech)

        return comments_data
    else:
        print(f"Error: {response.status_code} - {response.text}")