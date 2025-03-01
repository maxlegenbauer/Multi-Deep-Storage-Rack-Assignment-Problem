import WarehouseData as whd
import MulitDeepStorageModel as mdsm

file_path = "layout.xlsx"
wh = whd.WarehouseData(file_path)

model = mdsm.MultiDeepStorageModel(
    wh.get_J(), 
    wh.get_J_bar(), 
    wh.get_S(), 
    wh.get_D(), 
    wh.get_initial_storage_positions(wh.get_J_bar()),
    wh.get_racks()
)

model.optimize()
model.to_string()
model.show_path_per_rack()
model.storage_position_to_string()


