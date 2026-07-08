import os
import openpyxl
from openpyxl.drawing.image import Image as XLImage
from openpyxl.cell.cell import MergedCell as MC
import logging

logger = logging.getLogger("InvoiceApp")

VALID_TABS = {"invoice", "oils", "purchase", "schedule", "workshop"}
DEFAULT_TEMPLATES = {
    "oils": "oils_template.xlsx",
    "purchase": "po_template.xlsx",
    "schedule": "schedule_base.xlsx",
    "workshop": "تقرير الورشة.xlsx",
}
LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "excel_logo.png")
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_templates")

def get_template_path(tab):
    if tab not in VALID_TABS:
        return None
    user_file = os.path.join(TEMPLATE_DIR, f"{tab}_template.xlsx")
    if os.path.exists(user_file):
        return user_file
    default_name = DEFAULT_TEMPLATES.get(tab)
    if default_name:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), default_name)
    return None

def inject_logo(ws, img_path=LOGO_PATH, cell="A1", size=(120, 80)):
    if not os.path.exists(img_path):
        return
    try:
        img = XLImage(img_path)
        img.width, img.height = size
        ws.add_image(img, cell)
    except Exception as e:
        logger.warning(f"Could not inject logo into {cell}: {e}")
