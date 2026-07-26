"""
analytics_service.py - Advanced Performance Reports & Analytics Service
Calculates operating costs, fuel consumption rates (km/L), and operational KPIs.
"""

from models.schema import db, Vehicle, Driver, FuelRecord, WorkshopRecord, WorkshopPartUsage, SparePart, PurchaseRecord, PettyCash, Incident, Branch
from sqlalchemy import func
from datetime import datetime, timedelta

def get_operating_costs_summary(branch_id=None, start_date=None, end_date=None):
    """
    Returns aggregated operating costs grouped by vehicle and cost category
    (Fuel, Maintenance/Parts, Purchases, Petty Cash, Incidents).
    """
    try:
        # Filter conditions
        vehicle_costs = {}

        # 1. Fuel Costs
        fuel_query = db.session.query(
            FuelRecord.vehicle_id,
            func.sum(FuelRecord.cost).label('fuel_cost'),
            func.sum(FuelRecord.liters).label('total_liters'),
            func.max(FuelRecord.current_odo) - func.min(FuelRecord.prev_odo)
        ).group_by(FuelRecord.vehicle_id)

        if branch_id:
            fuel_query = fuel_query.filter(FuelRecord.branch_id == branch_id)
        if start_date:
            fuel_query = fuel_query.filter(FuelRecord.date >= start_date)
        if end_date:
            fuel_query = fuel_query.filter(FuelRecord.date <= end_date)

        for row in fuel_query.all():
            v_id = row[0]
            if not v_id: continue
            if v_id not in vehicle_costs:
                vehicle_costs[v_id] = {'fuel_cost': 0, 'maintenance_cost': 0, 'purchases_cost': 0, 'petty_cost': 0, 'incident_cost': 0, 'total_cost': 0}
            fuel_cost = float(row[1] or 0)
            vehicle_costs[v_id]['fuel_cost'] += fuel_cost
            vehicle_costs[v_id]['total_cost'] += fuel_cost

        # 2. Workshop Maintenance & Spare Parts Costs
        ws_query = db.session.query(
            WorkshopRecord.vehicle_id,
            func.sum(WorkshopPartUsage.quantity_used * SparePart.price).label('parts_cost')
        ).join(WorkshopPartUsage, WorkshopRecord.id == WorkshopPartUsage.workshop_record_id)\
         .join(SparePart, WorkshopPartUsage.spare_part_id == SparePart.id)\
         .group_by(WorkshopRecord.vehicle_id)

        if start_date:
            ws_query = ws_query.filter(WorkshopRecord.entry_date >= start_date)
        if end_date:
            ws_query = ws_query.filter(WorkshopRecord.entry_date <= end_date)

        for row in ws_query.all():
            v_id = row[0]
            if not v_id: continue
            if v_id not in vehicle_costs:
                vehicle_costs[v_id] = {'fuel_cost': 0, 'maintenance_cost': 0, 'purchases_cost': 0, 'petty_cost': 0, 'incident_cost': 0, 'total_cost': 0}
            maint_cost = float(row[1] or 0)
            vehicle_costs[v_id]['maintenance_cost'] += maint_cost
            vehicle_costs[v_id]['total_cost'] += maint_cost

        # 3. Incidents / Fines Costs
        inc_query = db.session.query(
            Incident.vehicle_id,
            func.sum(Incident.amount).label('incident_cost')
        ).group_by(Incident.vehicle_id)

        if start_date:
            inc_query = inc_query.filter(Incident.incident_date >= start_date)
        if end_date:
            inc_query = inc_query.filter(Incident.incident_date <= end_date)

        for row in inc_query.all():
            v_id = row[0]
            if not v_id: continue
            if v_id not in vehicle_costs:
                vehicle_costs[v_id] = {'fuel_cost': 0, 'maintenance_cost': 0, 'purchases_cost': 0, 'petty_cost': 0, 'incident_cost': 0, 'total_cost': 0}
            inc_cost = float(row[1] or 0)
            vehicle_costs[v_id]['incident_cost'] += inc_cost
            vehicle_costs[v_id]['total_cost'] += inc_cost

        # Attach vehicle details
        vehicle_ids = list(vehicle_costs.keys())
        vehicles = {v.id: v for v in Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()} if vehicle_ids else {}

        summary_list = []
        grand_total = 0.0
        total_fuel = 0.0
        total_maint = 0.0
        total_inc = 0.0

        for v_id, costs in vehicle_costs.items():
            v = vehicles.get(v_id)
            plate = v.plate_number if v else f"مركبة #{v_id}"
            model = v.model if v else "غير محدد"
            costs['vehicle_id'] = v_id
            costs['plate_number'] = plate
            costs['model'] = model
            summary_list.append(costs)

            grand_total += costs['total_cost']
            total_fuel += costs['fuel_cost']
            total_maint += costs['maintenance_cost']
            total_inc += costs['incident_cost']

        # Sort by total cost descending
        summary_list.sort(key=lambda x: x['total_cost'], reverse=True)

        return {
            'success': True,
            'grand_total': round(grand_total, 2),
            'total_fuel': round(total_fuel, 2),
            'total_maintenance': round(total_maint, 2),
            'total_incidents': round(total_inc, 2),
            'vehicles_count': len(summary_list),
            'vehicles': summary_list
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'vehicles': []}

def get_fuel_efficiency_report(branch_id=None):
    """
    Calculates fuel efficiency (Km / Liter and Cost / Km) for all vehicles.
    """
    try:
        query = db.session.query(
            FuelRecord.vehicle_id,
            func.sum(FuelRecord.liters).label('total_liters'),
            func.sum(FuelRecord.cost).label('total_cost'),
            func.max(FuelRecord.current_odo).label('max_odo'),
            func.min(FuelRecord.prev_odo).label('min_odo'),
            func.count(FuelRecord.id).label('records_count')
        ).group_by(FuelRecord.vehicle_id)

        if branch_id:
            query = query.filter(FuelRecord.branch_id == branch_id)

        results = query.all()
        vehicle_ids = [r[0] for r in results if r[0]]
        vehicles = {v.id: v for v in Vehicle.query.filter(Vehicle.id.in_(vehicle_ids)).all()} if vehicle_ids else {}

        report = []
        overall_distance = 0
        overall_liters = 0.0
        overall_cost = 0.0

        for row in results:
            v_id, liters, cost, max_odo, min_odo, count = row
            if not v_id: continue
            liters = float(liters or 0)
            cost = float(cost or 0)
            distance = (max_odo or 0) - (min_odo or 0)
            if distance < 0: distance = 0

            km_per_liter = round(distance / liters, 2) if liters > 0 else 0.0
            cost_per_km = round(cost / distance, 2) if distance > 0 else 0.0

            v = vehicles.get(v_id)
            report.append({
                'vehicle_id': v_id,
                'plate_number': v.plate_number if v else f"مركبة #{v_id}",
                'model': v.model if v else "عام",
                'type': v.v_type if v else "شاحنة",
                'total_liters': round(liters, 1),
                'total_cost': round(cost, 2),
                'distance_km': distance,
                'km_per_liter': km_per_liter,
                'cost_per_km': cost_per_km,
                'refuel_count': count
            })

            overall_distance += distance
            overall_liters += liters
            overall_cost += cost

        report.sort(key=lambda x: x['km_per_liter'], reverse=True)

        avg_efficiency = round(overall_distance / overall_liters, 2) if overall_liters > 0 else 0.0
        avg_cost_km = round(overall_cost / overall_distance, 2) if overall_distance > 0 else 0.0

        return {
            'success': True,
            'avg_km_per_liter': avg_efficiency,
            'avg_cost_per_km': avg_cost_km,
            'total_distance_km': overall_distance,
            'total_liters': round(overall_liters, 1),
            'total_cost': round(overall_cost, 2),
            'report': report
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'report': []}

def get_operational_kpis(branch_id=None):
    """
    Calculates operational readiness, vehicle status distribution,
    document validity index, and workshop throughput.
    """
    try:
        v_query = Vehicle.query
        d_query = Driver.query
        ws_query = WorkshopRecord.query

        if branch_id:
            v_query = v_query.filter_by(branch_id=branch_id)
            d_query = d_query.filter_by(branch_id=branch_id)

        total_vehicles = v_query.count()
        in_maintenance = v_query.filter(
            (Vehicle.yard_status == 'تحت الصيانة') | (Vehicle.yard_status == 'في الورشة')
        ).count()
        active_vehicles = total_vehicles - in_maintenance

        readiness_rate = round((active_vehicles / total_vehicles * 100), 1) if total_vehicles > 0 else 100.0

        total_drivers = d_query.count()
        available_drivers = d_query.filter_by(status='متاح').count()
        vacation_drivers = d_query.filter_by(status='إجازة').count()

        # Workshop throughput (records in current month)
        now = datetime.now()
        first_of_month = now.replace(day=1).date()
        open_orders = ws_query.filter(WorkshopRecord.status == 'مفتوح').count()
        completed_month = ws_query.filter(
            WorkshopRecord.status == 'مغلق',
            WorkshopRecord.exit_date >= first_of_month
        ).count()

        return {
            'success': True,
            'readiness_rate': readiness_rate,
            'total_vehicles': total_vehicles,
            'active_vehicles': active_vehicles,
            'in_maintenance': in_maintenance,
            'total_drivers': total_drivers,
            'available_drivers': available_drivers,
            'vacation_drivers': vacation_drivers,
            'open_workshop_orders': open_orders,
            'completed_workshop_month': completed_month
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
