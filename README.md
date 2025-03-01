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

so that Gurobi can optimize it. In the main.py file, the link to the Excel file is passed, and finally, the model is optimized.

Stellen wir kurz die einzelnen sheets der Excel vor. Das vorgestllte Beispiel befindet sich in der Datei layout.xlsx:

## 1. Layout
![Beschreibung des Bildes](/layout_sheet.png)
Storage Positions haben die Form $S(s_1,s_2,s_3)$. Die Aisle positions haben zwar auch eine spezifische Form, werden aber vom code ignoriert, dienen also nur der Darstellung in der Excel. Die picking station müssen zuerst mit ihrem jeweiligen namen angeben werden (bspw. "p1" für picking station 1, gefolgt von ihren koordniaten). Die Farben der Zellen machen keinen Unterschied, sie dienen ebenfalls nur der visualisierung (dunkle felder stehen für aisle felder)

## 2. Stopover
![Beschreibung des Bildes](/stopover_sheet.png)
Stopover $j = (r,p_1,p_2,t_1,t_2) müssen ebenfalls in das dafür vorgesehene sheet eingetragen werden. "Departure Picking Station" ist hierbei $p_1$ und "Arrival Picking Station" $p_2$. Für die Zeiten analog. Für die last stopover muss für $p_2$ "p_dummy" und für die Arrival Time das ende des gesamten zeithorizonts (in dem Beispiel 100) eingetragen werden.

## 3. Virtual Stopover
![Beschreibung des Bildes](/virtual_stopover_sheet.png)
Um Virtual Stopover extra zu behandeln, werden diese analog zu 2. in ein eigenes sheet eingetragen werden.

## 4. Initial Storage Position
![Beschreibung des Bildes](/initial_storage_position_sheet.png)
Die Initila occupied storage positions für die verwendeten racks ebenfalls in ein eigenes sheet eingetragen werden.


