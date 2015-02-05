from moneytracker.scripts import db


def run():
    db.wipe_all()
    print('Kthxbai.')



