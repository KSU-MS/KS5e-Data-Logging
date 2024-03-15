import numpy as np
import pandas as pd

class battery:
    def __init__(self,capacity_voltage_curve_path:str) -> None:
        self.maxv = 4.2 # full capacity
        self.minv = 2.0 # no capacity
        self.voltage = 4.2 # start at full charge
        self.capacity = 2500 # milliamp-hours
        self.resistance =  4.8 / 1000 #internal resistance in ohms
        batteryData = pd.read_csv(capacity_voltage_curve_path)
        coeffs = np.polyfit(batteryData['Ah'],batteryData['Voltage'],8)
        self.voltageUpdateFunction = np.poly1d(coeffs)
        
    def updateVoltage(self):
        if self.capacity>0:
            self.voltage = self.voltageUpdateFunction(self.capacity)
        else:
            self.voltage = 2.5
        return self.voltage
    
    def discharge(self,current,time):
        # Calculate the amount of charge discharged (Q = I * t)
        current = current * 1000 # scale amps to milliamps
        time = time / 3600 # scale seconds to hour
        # print(f"current: {current} time: {time}")
        
        discharged_charge = current * time # maH
        
        # print(f"discharged_charge: {discharged_charge}mAH")
        # Calculate the power dissipated as heat (P = I^2 * R)
        heat_power = current**2 * self.resistance # milliwatts
        # print(f"i2r: {heat_power}mW")

        # Convert the power to an equivalent loss of capacity based on the cell's voltage (P = V * I)
        # Assuming average voltage during discharge is half of max voltage
        heat_loss_energy = heat_power * time #should be mah?
        # print(f"heat_loss_energy: {heat_loss_energy}mWh")
        heat_loss_capacity = heat_loss_energy / self.voltage
        # print(f"heat_loss_capacity: {heat_loss_capacity}maH")
        # Adjust the discharged charge for the heat loss
        heat_loss_capacity = 0 # fuck this
        effective_discharged_charge = discharged_charge + heat_loss_capacity
        # print(f"effective discharged: {effective_discharged_charge}")
        # Calculate the new capacity after discharge
        # print(f"capacityBefore: {self.capacity}")
        self.capacity -= effective_discharged_charge
        
        # print(f"capacity now: {self.capacity}")

        # Ensure the capacity does not go below zero
        self.capacity = max(self.capacity, 0)  
        
    def getInstantaneousVoltage(self,current):
        voltage_sag = current * self.resistance
        return self.voltage - voltage_sag
        
class batteryPack:
    def __init__(self,battery:battery,parallelCount:int,seriesCount:int) -> None:
        self.cell = battery
        self.parallelCount = parallelCount
        self.seriesCount = seriesCount
        self.cellCount = self.parallelCount * self.seriesCount
        self.voltage = battery.voltage * self.seriesCount
        self.capacity = battery.capacity *self.parallelCount
        
    def updateVoltage(self):
        self.cell.updateVoltage()
        self.voltage = self.cell.voltage * self.seriesCount
        
    def discharge(self,current,time):
        self.updateVoltage()
        # print(f"Capacity before: {self.capacity}")
        self.cell.discharge(current/self.parallelCount,time)
        self.capacity = self.cell.capacity * self.parallelCount
        # print(f"Capacity after discharging: {self.capacity}")
        return self.capacity
    
    def getInstantaneousVoltage(self,current):
        self.updateVoltage()
        sagged_cell_v = self.cell.getInstantaneousVoltage(current)
        return sagged_cell_v * self.seriesCount
    
lghe2 = battery(r'lgHE2ahCurve.csv')
ks6eacc = batteryPack(lghe2,8,72)

#some tests

lghe2.capacity