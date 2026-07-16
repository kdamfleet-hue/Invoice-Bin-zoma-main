from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=True)

    users = db.relationship('User', backref='branch', lazy=True)
    drivers = db.relationship('Driver', backref='branch', lazy=True)
    vehicles = db.relationship('Vehicle', backref='branch', lazy=True)
    documents = db.relationship('Document', backref='branch', lazy=True)
    spare_parts = db.relationship('SparePart', backref='branch', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False) # admin, branch, kiosk
    
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)

class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    iqama_number = db.Column(db.String(50), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    iqama_expiry = db.Column(db.Date, nullable=True)
    license_expiry = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="متاح")
    
    custodies = db.relationship('VehicleCustody', backref='driver', lazy=True)
    incidents = db.relationship('Incident', backref='driver', lazy=True)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    plate_number = db.Column(db.String(50), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=True)
    v_type = db.Column(db.String(50), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    istimara_expiry = db.Column(db.Date, nullable=True)
    inspection_expiry = db.Column(db.Date, nullable=True)
    gps_device_id = db.Column(db.String(100), nullable=True)
    
    custodies = db.relationship('VehicleCustody', backref='vehicle', lazy=True)
    incidents = db.relationship('Incident', backref='vehicle', lazy=True)
    workshop_records = db.relationship('WorkshopRecord', backref='vehicle', lazy=True)

class VehicleCustody(db.Model):
    __tablename__ = 'vehicle_custody'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="active")

class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    incident_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)

class SparePart(db.Model):
    __tablename__ = 'spare_parts'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    part_number = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    
    usages = db.relationship('WorkshopPartUsage', backref='spare_part', lazy=True)

class WorkshopRecord(db.Model):
    __tablename__ = 'workshop_records'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    exit_date = db.Column(db.Date, nullable=True)
    issue_description = db.Column(db.Text, nullable=True)
    mechanic_name = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), default="مفتوح")
    
    part_usages = db.relationship('WorkshopPartUsage', backref='workshop_record', lazy=True)

class WorkshopPartUsage(db.Model):
    __tablename__ = 'workshop_part_usage'
    id = db.Column(db.Integer, primary_key=True)
    workshop_record_id = db.Column(db.Integer, db.ForeignKey('workshop_records.id'), nullable=False)
    spare_part_id = db.Column(db.Integer, db.ForeignKey('spare_parts.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    reference_id = db.Column(db.Integer, nullable=True) # polymorphic, could be driver or vehicle
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.Date, default=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target_table = db.Column(db.String(100), nullable=True)
    target_id = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
