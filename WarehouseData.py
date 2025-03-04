import pandas as pd
import re

class WarehouseData:
    def __init__(self, layout_file):
        self.layout_file = layout_file
        self.J = self.extract_stopovers()
        self.J_bar = self.extract_virtual_stopovers()
        self.S = self.extract_positions()
        self.P = self.extract_picking_station_positions()
        self.R = self.extract_racks()
        self.D = self.calc_distances()

    def extract_positions(self):
        def extract_tuples(cell):
            if isinstance(cell, str) and 'S' in cell:
                return re.search(r'\((.*?)\)', cell).group(1)
            return None
        layout_df = pd.read_excel(self.layout_file, sheet_name='Layout')
        tuples = layout_df.map(extract_tuples).stack().dropna().tolist()
        return [tuple(map(int, item.split(','))) for item in tuples]
    
    def get_S(self):
        return self.S
    
    def extract_stopovers(self):
        df = pd.read_excel(self.layout_file, sheet_name='Stopovers')
        tupel_liste = [tuple(row) for row in df.itertuples(index=False, name=None)]
        return tupel_liste
    
    def get_J(self):
        return self.J
    
    def extract_virtual_stopovers(self):
        df = pd.read_excel(self.layout_file, sheet_name='Virtual Stopovers')
        df.insert(1, 'Departure Picking Station', None) 
        df.insert(3, 'Departure Time', None) 
        tuple_list = [tuple(row) for row in df.itertuples(index=False, name=None)]
        return tuple_list
    
    def get_J_bar(self):
        return self.J_bar
    
    def extrackt_picking_stations(self):
        all_stopovers = self.J + self.J_bar
        picking_stations = list(
            set(
                tup[1] for tup in all_stopovers if tup[1] is not None
            ) | set(
                tup[2] for tup in all_stopovers if tup[2] is not None
            )
        )
        return picking_stations
        
    def get_picking_stations(self):
        return self.P

    def extract_racks(self):
        all_stopovers = self.J + self.J_bar
        racks = list(set(tuple[0] for tuple in all_stopovers))
        return racks
    
    def get_racks(self):
        return self.R
    
    def extract_picking_station_positions(self):
        layout_df = pd.read_excel(self.layout_file, sheet_name='Layout')
        
        def extract_tuple(cell, prefix):
            if isinstance(cell, str) and prefix in cell:
                match = re.search(r'\((.*?)\)', cell)
                if match:
                    return match.group(1) 
            return None
        
        picking_stations = pd.DataFrame(self.extrackt_picking_stations(), columns=["Picking Stations"])
        
        picking_stations["Position"] = picking_stations["Picking Stations"].apply(
            lambda station: layout_df.map(
                lambda cell: extract_tuple(cell, station)
            ).stack().dropna().tolist()
        )
        
        picking_station_tuples = picking_stations.apply(
            lambda row: [(row["Picking Stations"], *map(int, pos.split(','))) for pos in row["Position"]] if row["Position"] else [],
            axis=1  # Wende die Funktion auf jede Zeile an
        ).explode().dropna().tolist()
        picking_station_tuples.append(('p_dummy',0,0,0))
        return picking_station_tuples

    def calc_distances(self):
        P = self.get_picking_stations()
        S = self.get_S()
        sigma = lambda z: sum(2 * abs(i) for i in range(1, abs(z) + 1)) 
        D = {(p[0],s): 0 if p[0] == 'p_dummy' else abs(p[1] - s[0]) + abs(p[2] - s[1]) + sigma(s[2]) for p in P for s in S}
        return D
    
    def get_D(self):
        return self.D
    
    def get_E(self):
        D = self.get_D()
        J = self.get_J()
        S = self.get_S()
        E = {(j, s): D[(j[1],s)] + D[(j[2],s)] for j in J for s in S}
        return E
    
    def get_initial_storage_positions(self, J_bar):
        df = pd.read_excel(self.layout_file, sheet_name='Initial Storage Positions')
        
        storage_positions = {}
        
        for j in J_bar:
            rack = j[0]  
            
            matching_row = df[df['Rack'] == rack]
            if not matching_row.empty:
                storage_position = matching_row['Storage Position'].iloc[0]
                
                if isinstance(storage_position, str):
                    storage_position = tuple(map(int, storage_position.strip('()').split(',')))
                
                storage_positions[j] = storage_position  
            else:
                storage_positions[j] = None  
        
        return storage_positions
