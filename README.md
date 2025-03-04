# Multi-Deep-Storage-Rack-Assignment-Problem

This code provides the framework for creating and optimizing a Multi-Deep Rack Assignment Problem (RAP). The warehouse layout (including positions, number of racks, etc.) and the definition of all stopovers must be manually entered into the designated Excel file. The code then automatically reads this file and performs linear optimization using the Gurobi optimizer.

The purpose of this codebase is to illustrate the concepts behind modeling Multi-Deep Storage RAPs and to test whether the model behaves in line with intuition. The code is not optimized for speed, and any production use will require additional safeguards before deployment.

The program consists of 3 files. In the file warehouseData.py, the layout is read from the Excel file, and an object of the WarehouseData class is created. In the MultiDeepStorageModel.py file, the model is then created according to: 

$$ \min \quad \sum_{j \in J} \sum_{s \in S} e_{js} \cdot x_{js} + 2 \sum_{j \in J\cup \bar{J}} \sum_{s \in S, s^\prime \in S_s} (b^1_{ss^\prime j} + b^2_{ss^\prime j}) \cdot \vert s_3 \vert \quad \quad \text{s.t} $$
$$ \sum_{s \in S_j} x_{js} = 1 \quad \forall j \in J $$
$$x_{js} + x_{j^\prime s} \leq 1 \quad \forall s \in S; (j,j^\prime ) \in \Theta_s$$
$$ b_{ss^\prime j}^k \geq x_{js} + x_{j^\prime s^\prime} - 1 \quad \forall j,j^\prime \in \Theta_{s,s^\prime}^k; s \in S, s^\prime \in S_s, k=1,2 $$
$$ x_{j \rho^j} = 1 \quad \forall j \in \bar{J} $$
$$ x_{js}, b^k_{ss^\prime j} \in \{ 0,1 \} \quad \forall j \in J; s \in S, s^\prime \in S_s, k=1,2 $$

so that Gurobi can optimize it. In the main.py file, the link to the Excel file is passed, and finally, the model is optimized. With the methods "to_string, "show_path_per_rack()" and "storage_position_to_string()" you have the opportunity to print out results of the opimized model.

Let’s briefly introduce the individual sheets of the Excel file. The presented example can be found in the file layout.xlsx.

## 1. Layout
![Beschreibung des Bildes](/layout_sheet.png)
Storage positions are represented in the form $S(s_1,s_2,s_3)$. While aisle positions also have a specific format, they are ignored by the code and serve only for visualization in Excel. The picking stations must first be specified with their respective names (e.g., "p1" for picking station 1), followed by their coordinates. The cell colors do not affect the functionality; they are only for visualization purposes (dark cells represent aisle fields).

## 2. Stopover
![Beschreibung des Bildes](/stopover_sheet.png)
Stopovers $j = (r,p_1,p_2,t_1,t_2)$ must be entered into the corresponding sheet.  

- **"Departure Picking Station"** corresponds to $p_1$.  
- **"Arrival Picking Station"** corresponds to $p_2$.  
- The same logic applies to the times.

For the last stopover, enter "p_dummy" for $p_2$ and the end of the entire time horizon (100 in this example) as the Arrival Time.

## 3. Virtual Stopover
![Beschreibung des Bildes](/virtual_stopover_sheet.png)
To handle Virtual Stopovers separately, they are entered into a dedicated sheet, similar to Stopovers (2.).

## 4. Initial Storage Position
![Beschreibung des Bildes](/initial_storage_position_sheet.png)
The initially occupied storage positions for the racks used must also be entered into a separate sheet.

