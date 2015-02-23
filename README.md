MoneyTracker is a simple Django app, to help keep track of communal expenses during group events (such as ski trips).

It must be noted that Excel / Google Docs spreadsheets have been more than adequate to achieve this task.
This web-app exercise if for the sole purpose of playing around with Django and a handful of other technologies! :)

=======================
Functionality outline:

- creation of an event and a group of participants
- entry of expense records, under the name of the participant who paid for the expense
- entry of balance transfer records, between two participants
- default allocation of expenses as equally split by the entire group (all participants)
- optional allocation of expenses to sub-groups within the group (exclusion of some participants)
- calculation of the running trip total (all expenses)
- calculation of each partitipant's contribution to expenses (funds paid towards an expense)
- calculation of each participant's expense allocation (participation in an an expense)
- calculation of each participant's variance (overpayment or underpayment), to establish debt payable or receivable. 
- generation of suggested fund transfers within the group, to help the participants settle the variances at the end of the event
