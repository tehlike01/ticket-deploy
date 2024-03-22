import insert_record_into_database

""" Steps required To Run The Model To insert tickets into odoo help desk database:
1) Run devolper mode in odoo Then GoTo Setting>Technical>sequence 
2) create a new sequence with sequence code: 'mail.message', Name: CommentID, Prefix:CID , 
sequence size: 5 Step:1, Next Number: 1, Implementation: standard, Active: On and save it
3) add piece of code in the content (after line:180) of mail_message in odoo/addons/mail/models/mail_message and Rerun the code """
#-------------------------------------------------------------------------------------------------------
""" comment_id = fields.Char(string='Comment_id', default=lambda self: self._generate_comment_id(),
                             help='The name of the help ticket. By default, a new '
                                  'unique sequence number is assigned to each '
                                  'mail message, unless a name is provided.',
                             	   readonly=True)

    def _generate_comment_id(self):
        return self.env['ir.sequence'].next_by_code('mail.message') or _('New')

    def create(self, vals):
        if vals.get('comment_id', _('New')) == _('New'):
            vals['comment_id'] = self._generate_comment_id()
        return super('mail.message', self).create(vals) """
#-------------------------------------------------------------------------------------------------------

customer_id = '26415261'
insert_record_into_database.insert_customer_by_customer_id(customer_id)
insert_record_into_database.insert_tickets_by_customer_id(customer_id)
insert_record_into_database.insert_all_customer_comments(customer_id)
insert_record_into_database.post_all_customer_comments(customer_id)
insert_record_into_database.update_tickets_by_customer_id(customer_id)