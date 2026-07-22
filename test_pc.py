from app import app
from models.schema import PettyCash, Driver, db
with app.app_context():
    try:
        # insert a dummy petty cash
        pc = PettyCash(branch_id=1, amount=100.0, expense_type='Test', date='2026-07-22')
        db.session.add(pc)
        db.session.commit()
        print('Dummy PC inserted.')
    except Exception as e:
        print(f'DB error: {e}')
