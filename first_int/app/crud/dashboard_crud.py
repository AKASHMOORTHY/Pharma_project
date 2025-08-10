from app.models.production_models import ProductionBatch as BaseProductionBatch, StageLog as Stage
from app.models.dashboard_models import DashboardProductionBatch, QualityCheck, Inventory, Anomaly
from app.models.anomaly_models import DetectedAnomaly as BaseAnomaly
from app.models.qc_models import QCTest as BaseQCTest, QCTestResult as BaseQCTestResult
from app.models.inventory_models import InventoryItem as BaseInventoryItem, StockMovement as BaseStockMovement
from app.models.materials_models import RawMaterial as BaseRawMaterial
from app.database import SessionLocal
from sqlalchemy.orm import Session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
def populate_dashboard_production(db: Session):
    # Populate the dashboard production table with combined data from ProductionBatch and StageLog using a single join query.
    db.query(DashboardProductionBatch).delete()
    
    try:
        # Perform a join between ProductionBatch and StageLog
        results = (
            db.query(
                BaseProductionBatch.id,
                BaseProductionBatch.date,
                BaseProductionBatch.shift,
                Stage.start_time,
                Stage.end_time,
                Stage.status
            ).join(Stage, Stage.production_batch_id == BaseProductionBatch.id).all()
        )

        for row in results:
            duration = None
            if row.start_time and row.end_time:
                duration = (row.end_time - row.start_time).total_seconds() / 3600  # in hours

            dashboard_record = DashboardProductionBatch(
                id = row.id,  
                production_date = row.date,
                shift = row.shift,
                status = row.status,
                duration = duration
            )

            db.add(dashboard_record)

        db.commit()
        print("Dashboard production table populated successfully")

    except Exception as e:
        db.rollback()
        print(f"Error populating dashboard: {e}")


def get_dashboard_production_data(db: Session):
    #  Get all dashboard production data  #
    return db.query(DashboardProductionBatch).all()
    

def get_production_by_date(db: Session, date):
    # Get production data for a specific date  #
    return db.query(DashboardProductionBatch).filter(DashboardProductionBatch.production_date == date).all()
    

def get_production_by_shift(db: Session, shift):
    #  Get production data for a specific shift  #
    return db.query(DashboardProductionBatch).filter(DashboardProductionBatch.shift == shift).all()


def populate_dashboard_quality_check(db: Session):
    #Populate the dashboard quality check table using a single query join between QCTest and QCTestResult.
    try:
        db.query(QualityCheck).delete()

        # Join QCTest and QCTestResult
        results = (
            db.query(
                BaseQCTestResult.id,
                BaseQCTest.remarks,
                BaseQCTest.date,
                BaseQCTestResult.is_within_spec
            ).join(BaseQCTest, BaseQCTest.id == BaseQCTestResult.test_id).all()
        )

        for row in results:
            dashboard_qc = QualityCheck(
                id = row.id,
                reason = row.remarks,
                created_at = row.date,
                result = "Pass" if row.is_within_spec else "Fail"
            )
            db.add(dashboard_qc)

        db.commit()
        print("Dashboard quality check table populated successfully")

    except Exception as e:
        db.rollback()
        print(f"Error populating quality check dashboard: {e}")

def get_dashboard_quality_check_data(db:Session):
    # Get all dashboard quality check data
    return db.query(QualityCheck).all()

def get_quality_check_by_date(db:Session, date):
    # Get quality check data for a specific date 
    return db.query(QualityCheck).filter(QualityCheck.created_at == date).all()

def get_quality_check_by_result(db:Session, is_within_spec):
    # Get quality check data filtered by result (pass/fail)
    return db.query(QualityCheck).filter(QualityCheck.is_within_spec == is_within_spec).all()


def populate_dashboard_inventory(db: Session):
    # Populate the dashboard inventory table using a single query join between InventoryItem and StockMovement.
    try:
        db.query(Inventory).delete()

        # Join InventoryItem, StockMovement, and RawMaterial
        results = (
            db.query(
                BaseInventoryItem.id,
                BaseInventoryItem.quantity,
                BaseInventoryItem.location,
                BaseInventoryItem.material_id,
                BaseInventoryItem.status,
                BaseStockMovement.timestamp,

            ).join(BaseStockMovement, BaseStockMovement.item_id == BaseInventoryItem.id)\
             .join(BaseRawMaterial, BaseRawMaterial.id == BaseInventoryItem.material_id).all()
        )

        for row in results:
            dashboard_inventory = Inventory(
                id = row.id,  # Warning: Ensure ID uniqueness if multiple rows per item
                quantity = row.quantity,
                location = row.location,
                material = row.material_id,
                updated_at = row.timestamp,
                status = row.status            
                )
            db.add(dashboard_inventory)

        db.commit()
        print("Dashboard inventory table populated successfully")

    except Exception as e:
        db.rollback()
        print(f"Error populating inventory dashboard: {e}")


def get_dashboard_inventory_data(db: Session):
    # Get all dashboard inventory data 
    return db.query(Inventory).all()
    

def get_inventory_by_status(db: Session, status):
    # Get inventory data filtered by status 
    return db.query(Inventory).filter(Inventory.status == status).all()
    

def get_inventory_by_location(db: Session, location):
    # Get inventory data filtered by location #
    return db.query(Inventory).filter(Inventory.location == location).all()


def populate_dashboard_anomaly(db: Session):
    # Populate the dashboard anomaly table with data from DetectedAnomaly
    try:
        # Clear existing dashboard data
        db.query(Anomaly).delete()

        # Get all anomalies
        anomalies = db.query(BaseAnomaly).all()

        for anomaly in anomalies:
            dashboard_anomaly = Anomaly(
                id=anomaly.id,
                status=anomaly.status,
                created_at=anomaly.detected_at,
                resolved_at=anomaly.resolved_at
            )
            db.add(dashboard_anomaly)

        db.commit()
        print("Dashboard anomaly table populated successfully")
        
    except Exception as e:
        db.rollback()
        print(f"Error populating anomaly dashboard: {e}")

def get_dashboard_anomaly_data(db:Session):
    # Get all dashboard anomaly data
    return db.query(Anomaly).all()

def get_anomaly_by_status(db:Session, status):
    # Get anomaly data filtered by status
    return db.query(Anomaly).filter(Anomaly.status == status).all()
