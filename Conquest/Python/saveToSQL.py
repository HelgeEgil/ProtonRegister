import sys
import pynetdicom
import pydicom
import pyodbc
from dicompylercore import dicomparser, dvh, dvhcalc
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, build_role, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelGet, CTImageStorage, RTDoseStorage, RTIonPlanStorage, RTStructureSetStorage
from time import time

connectionString = "Driver={SQL Server};SERVER={VIR-APP6666\SQLEXPRESS};database=testregister;"

last_id = -1
global_rd = None
global_rs = None

def to_sql(ds):
	global last_id
	global global_rd
	global global_rs

	print("Patient Name: ", ds.PatientName)
	print("Study description: ", ds.StudyDescription)
	print("Modality: ", ds.Modality)
	print("Manufacturer: ", ds.Manufacturer)
	print("Last id: ", last_id)

	if ds.Modality == "RTSTRUCT":
		print("(RTSTRUCT)")
		if not "ROI" in ds.SeriesDescription: # Especially for the pancreas patient, to pick a single RTSTRUCT
			return

		global_rs = ds
		conn = pyodbc.connect(connectionString)
		cursor = conn.cursor()
		numberOfStructures = len(ds.ROIContourSequence)

		if last_id < 0:
			cursor.execute("""INSERT INTO testregister.dbo.RTImageSeries
				(NumberOfStructures) VALUES (?)""", numberOfStructures)
		else:
			cursor.execute(f"""UPDATE testregister.dbo.RTImageSeries
				SET NumberOfStructures = ? WHERE ID = ?""", numberOfStructures, last_id)

		conn.commit()
		if last_id < 0:
			cursor.execute("SELECT @@IDENTITY AS ID;")
			last_id = cursor.fetchone()[0]

	elif ds.Modality == "RTDOSE":
		print("(RTDOSE)")
		global_rd = ds

	elif ds.Modality == "RTPLAN":
		print("(RTPLAN)")
		conn = pyodbc.connect(connectionString)
		cursor = conn.cursor()

		if last_id < 0:
			cursor.execute("""INSERT INTO testregister.dbo.RTImageSeries
				(PrescriptionDose_Gy) VALUES (?)""", ds.TargetPrescriptionDose)
			conn.commit()
			cursor.execute("SELECT @@IDENTITY AS ID;")
			last_id = cursor.fetchone()[0]
		else:
			cursor.execute(f"""UPDATE testregister.dbo.RTImageSeries
				SET PrescriptionDose_Gy = ? WHERE ID = ?""", ds.TargetPrescriptionDose, last_id)

		conn.commit()
		if last_id < 0:
			cursor.execute("SELECT @@IDENTITY AS ID;")
			last_id = cursor.fetchone()[0]

	elif ds.Modality == "CT":
		print("(CT)")
		conn = pyodbc.connect(connectionString)
		cursor = conn.cursor()
		if last_id < 0:
			try:
				cursor.execute("""INSERT INTO testregister.dbo.RTImageSeries 
					(PatientName, Modality, SeriesInstanceUID, SliceThickness_mm, 
					Manufacturer, ManufacturersModelName, kVp, mAs) VALUES (?,?,?,?,?,?,?,?)""",
					str(ds.PatientName), ds.Modality, ds.SeriesInstanceUID, ds.SliceThickness, ds.Manufacturer, 
					ds.ManufacturerModelName, ds.KVP, ds.ExposureTime or 0)
			except Exception as e:
				print(f"Error: {e}")
		else:
			try:
				cursor.execute(f"""UPDATE testregister.dbo.RTImageSeries
					SET PatientName = ?, Modality = ?, SeriesInstanceUID = ?, SliceThickness_mm = ?,
					Manufacturer = ?, ManufacturersModelName = ?, kVp = ?, mAs = ? WHERE ID = ?""",
					ds.PatientName, ds.Modality, ds.SeriesInstanceUID, ds.SliceThickness, ds.Manufacturer, 
					ds.ManufacturerModelName, ds.KVP, ds.ExposureTime or 0, last_id)
			except Exception as e:
				print(f"Error: {e}")
		
		conn.commit()
		if last_id < 0:
			cursor.execute("SELECT @@IDENTITY AS ID;")
			last_id = cursor.fetchone()[0]
			print("New last_id ", last_id)

	else:
		return

	if global_rd and global_rs:
		print("(RTDOSE + RTSTRUCT)")
		conn = pyodbc.connect(connectionString)
		cursor = conn.cursor()
		print("Calculating DVHs... ", end="")
		numberOfStructures = len(global_rs.ROIContourSequence)
		print(f"({numberOfStructures}) ", end=" ")
		for n in range(numberOfStructures):
			dose_resolution = global_rd.PixelSpacing[0]
			interpolation = (dose_resolution/4)
			print(f"Calculating... ",end="")
			timebefore = time()
			dvh = dvhcalc.get_dvh(global_rs, global_rd, n+1)#, calculate_full_volume=True, use_structure_extents=True, 
				#interpolation_resolution=interpolation, interpolation_segments_between_planes=2)
			timeafter = time()
			print(f"{dvh.name} done ({timeafter-timebefore:.1f} s). ", end="")

			volume = dvh.volume
			string_dose_gy = ",".join([f"{d:.3f}" for d in dvh.bincenters])
			string_volume_percent = ",".join([f"{v:.3f}" for v in dvh.relative_volume.counts])
			name = dvh.name

			#print(f"""INSERT INTO testregister.dbo.DVH (RTImageSeriesID, StructureName, StructureVolume_cc, DVH_dose_Gy, DVH_volume_percent) VALUES ({last_id},'{name}',{round(volume,2)},'{string_dose_gy}','{string_volume_percent}')""")

			cursor.execute("""INSERT INTO testregister.dbo.DVH (RTImageSeriesID, StructureName, 
					StructureVolume_cc, DVH_dose_Gy, DVH_volume_percent) VALUES (?,?,?,?,?)""",
					last_id, name, round(volume,2), string_dose_gy, string_volume_percent)
			print("Inserted!")
		global_rd = None
		global_rs = None

		conn.commit()

def handle_store(event):
    ds = event.dataset
    ds.file_meta = event.file_meta
    to_sql(ds)
    return 0x0000

uid = sys.argv[1]

handlers = [(evt.EVT_C_STORE, handle_store)]
ae = AE(ae_title="PYSAVETOSQL")
ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
ae.add_requested_context(CTImageStorage)
ae.add_requested_context(RTDoseStorage)
ae.add_requested_context(RTIonPlanStorage)
ae.add_requested_context(RTStructureSetStorage)

role_CTImageStorage = build_role(CTImageStorage, scp_role=True)
role_RTDoseStorage = build_role(RTDoseStorage, scp_role=True)
role_RTIonPlanStorage = build_role(RTIonPlanStorage, scp_role=True)
role_RTStructureSetStorage = build_role(RTStructureSetStorage, scp_role=True)


modalities = ["CT", "RTPLAN", "RTDOSE", "RTSTRUCT"]

for modality in modalities:
	print(f"Searching for DICOM {modality} objects")

	ds = Dataset()
	ds.QueryRetrieveLevel = 'SERIES'
	ds.PatientName = uid
	ds.Modality = modality
	if modality == "CT":
		ds.InstanceNumber = 1
		ds.Manufacturer = "Philips"

	assoc = ae.associate("127.0.0.1", 104, ext_neg=[role_CTImageStorage, role_RTDoseStorage, role_RTIonPlanStorage, role_RTStructureSetStorage], evt_handlers=handlers)
	if assoc.is_established:
		for cx in assoc.accepted_contexts:
			cx._as_scp = True

		responses = assoc.send_c_get(ds, PatientRootQueryRetrieveInformationModelGet)
		for (status, identifier) in responses:
			if status:
				print('C-FIND query status: 0x{0:04X}'.format(status.Status))
				pass
			else:
				print('Connection timed out, was aborted or received invalid response')
		assoc.release()
	else:
		print("Association rejected, aborted or never connected")