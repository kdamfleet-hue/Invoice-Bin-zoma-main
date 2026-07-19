import app
from app import _compute_insights

with app.app.app_context():
    try:
        insights = _compute_insights(rid=1)
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()
