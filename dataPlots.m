close all
%% 
% Usage:
% 1. Load the data struct into the Workspace
% 2. Run individual sections of the script to plot the desired data
%% Constants
dyno_tire_diameter = 20.5; %ish inches 
normal_tire_diameter = 18;
tire_diameter = normal_tire_diameter; % set to the right tire size when plotting
gear_ratio = 10/30;

%% Torque, Vehicle Speed, Current
figure

requested_torque = S.Torque_Command;
commanded_torque = S.D1_Commanded_Torque;
feedback_torque = S.D2_Torque_Feedback;
busCurrent = S.D4_DC_Bus_Current;
busVoltage = S.D1_DC_Bus_Voltage;
motor_speed = S.D2_Motor_Speed;
vehicle_speed_mph = motor_speed;
vehicle_speed_mph(:,2) = motor_speed(:,2).*gear_ratio.*tire_diameter.*pi.*60 / 63360;
hold on
plot(motor_speed(:,1),motor_speed(:,2)./100);
plot(busCurrent(:,1),busCurrent(:,2)./2);
plot(commanded_torque(:,1),commanded_torque(:,2)./10);
plot(feedback_torque(:,1),feedback_torque(:,2)./10);
plot(requested_torque(:,1),requested_torque(:,2)./10);
legend({'Motor Speed (RPM)*0.01','Current (A)*0.5','Commanded Torque*0.1 (Nm)','Feedback Torque*0.1 (Nm)','Requested Torque*0.1 (Nm)'})
xlabel('Time (ms)')
title('Torque, Speed, Current')

%% Pedal Input Traces
figure

front_brakes_data = S.BSE1(:, 2);
front_brakes_time = S.BSE1(:, 1);

pedal_data = S.APPS1(:, 2);
pedal_time = S.APPS1(:, 1);

% Normalizing and cleaning pedal traces
front_brakes_data = front_brakes_data - mode(front_brakes_data);
front_brakes_data(front_brakes_data < 0) = 0;
front_brakes_data = front_brakes_data/max(front_brakes_data);

pedal_data = pedal_data - mode(pedal_data);
pedal_data(pedal_data < 0) = 0;
pedal_data = pedal_data/max(pedal_data);

hold on
plot(pedal_time, pedal_data, '.-');
plot(front_brakes_time, front_brakes_data, '.-');
grid on

xlabel('Time (ms)')
ylabel('Normalized Pedal Position and Brake Pressure')
title('Brake and Pedal Traces')
legend({'Accelerator Pedal Position','Brake Pressure'})

%% DC Bus Current, DC Bus Voltage, and Calculated DC Power Output
figure
voltage = S.D1_DC_Bus_Voltage; 
current = S.D4_DC_Bus_Current;

% Data uniqueness
for i = 1:length(voltage(:,1))
    voltage(i,1) = voltage(i,1) + i/100000000;
end
for i = 1:length(current(:,1))
    current(i,1) = current(i,1) + i/100000000;
end
    
time = 1:0.1:max(current(:,1)); %Seconds
current_adj = interp1(current(:,1),current(:,2),time);
voltage_adj = interp1(voltage(:,1),voltage(:,2),time);
power = current_adj.*voltage_adj./1000;

hold on
plot(S.D4_DC_Bus_Current(:,1), S.D4_DC_Bus_Current(:,2), '.-');
plot(S.D1_DC_Bus_Voltage(:,1), S.D1_DC_Bus_Voltage(:,2), '.-'); 
plot(time, power, '.-')
grid on

xlabel('Time (ms)')
ylabel('Voltage (V), Current (A), Power (kW)')
title('DC Bus Current, DC Bus Voltage, and Calculated DC Power Output')
legend({'Current','Voltage','Power'})

%% Cooling Loop: Motor and MCU Temperatures
figure

hold on
plot(S.D4_Gate_Driver_Board(:,1),S.D4_Gate_Driver_Board(:,2))
plot(S.D1_Control_Board_Temperature(:,1),S.D1_Control_Board_Temperature(:,2))
plot(S.D1_Module_A(:,1),S.D1_Module_A(:,2))
plot(S.D2_Module_B(:,1),S.D2_Module_B(:,2)) 
plot(S.D3_Module_C(:,1),S.D3_Module_C(:,2))
plot(S.D3_Motor_Temperature(:,1),S.D3_Motor_Temperature(:,2))
plot(S.D4_DC_Bus_Current(:,1),S.D4_DC_Bus_Current(:,2)./10) 
grid on

legend({'MCU Gate Driver Board Temperature','MCU Control Board Temperature','MCU Module A Temperature','MCU Module B Temperature','MCU Module C Temperature','Motor Temperature','Current/10 (A)'})
xlabel('Time (ms)')
ylabel('Temperature (C)')
title('Cooling Loop Temperature Plots')

%% Torque vs RPM 
plot_y_vs_y(S.D2_Motor_Speed,S.D2_Torque_Feedback,'Motor Speed (RPM)','Torque Feedback (Nm)','Feedback Torque vs Motor RPM')

%% Accumulator Cell Temperatures
% TODO: Add the polynomial function since the "temp" on CAN is a voltage
figure
hold on
plot(S.D4_DC_Bus_Current(:,1),S.D4_DC_Bus_Current(:,2)./10)
plot(S.Average_Temperature(:,1),S.Average_Temperature(:,2),'.')
plot(S.High_Temperature(:,1),S.High_Temperature(:,2),'.')
plot(S.Low_Temperature(:,1),S.Low_Temperature(:,2),'.') 
ylim([0,50]) % only BMS_state, BMS_total_discharge, BMS_total_charge
ylabel('Temperature (C)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures')
legend({'Current/10 (A)','BMS Average Temperature','BMS High Temperature','BMS Low Temperature'})

figure
subplot(2,3,1)
hold on
plot(S.cell1temp(:,1),S.cell1temp(:,2),'.')
plot(S.cell2temp(:,1),S.cell2temp(:,2),'.')
plot(S.cell3temp(:,1),S.cell3temp(:,2),'.')
plot(S.cell4temp(:,1),S.cell4temp(:,2),'.')
plot(S.cell5temp(:,1),S.cell5temp(:,2),'.')
plot(S.cell6temp(:,1),S.cell6temp(:,2),'.')
plot(S.cell7temp(:,1),S.cell7temp(:,2),'.')
plot(S.cell8temp(:,1),S.cell8temp(:,2),'.')
plot(S.cell9temp(:,1),S.cell9temp(:,2),'.')
plot(S.cell10temp(:,1),S.cell10temp(:,2),'.')
plot(S.cell11temp(:,1),S.cell11temp(:,2),'.')
plot(S.cell12temp(:,1),S.cell12temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 1 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12'},'Location','southeast')
subplot(2,3,2)
hold on
plot(S.cell13temp(:,1),S.cell13temp(:,2),'.')
plot(S.cell14temp(:,1),S.cell14temp(:,2),'.')
plot(S.cell15temp(:,1),S.cell15temp(:,2),'.')
plot(S.cell16temp(:,1),S.cell16temp(:,2),'.')
plot(S.cell17temp(:,1),S.cell17temp(:,2),'.')
plot(S.cell18temp(:,1),S.cell18temp(:,2),'.')
plot(S.cell19temp(:,1),S.cell19temp(:,2),'.')
plot(S.cell20temp(:,1),S.cell20temp(:,2),'.')
plot(S.cell21temp(:,1),S.cell21temp(:,2),'.')
plot(S.cell22temp(:,1),S.cell22temp(:,2),'.')
plot(S.cell23temp(:,1),S.cell23temp(:,2),'.')
plot(S.cell24temp(:,1),S.cell24temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 2 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12'},'Location','southeast')

subplot(2,3,3)
hold on
plot(S.cell25temp(:,1),S.cell25temp(:,2),'.')
plot(S.cell26temp(:,1),S.cell26temp(:,2),'.')
plot(S.cell27temp(:,1),S.cell27temp(:,2),'.')
plot(S.cell28temp(:,1),S.cell28temp(:,2),'.')
plot(S.cell29temp(:,1),S.cell29temp(:,2),'.')
plot(S.cell30temp(:,1),S.cell30temp(:,2),'.')
plot(S.cell31temp(:,1),S.cell31temp(:,2),'.')
plot(S.cell32temp(:,1),S.cell32temp(:,2),'.')
plot(S.cell33temp(:,1),S.cell33temp(:,2),'.')
plot(S.cell34temp(:,1),S.cell34temp(:,2),'.')
plot(S.cell35temp(:,1),S.cell35temp(:,2),'.')
plot(S.cell36temp(:,1),S.cell36temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 3 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12'},'Location','southeast')
subplot(2,3,4)
hold on
plot(S.cell37temp(:,1),S.cell37temp(:,2),'.')
plot(S.cell38temp(:,1),S.cell38temp(:,2),'.')
plot(S.cell39temp(:,1),S.cell39temp(:,2),'.')
plot(S.cell40temp(:,1),S.cell40temp(:,2),'.')
plot(S.cell41temp(:,1),S.cell41temp(:,2),'.')
plot(S.cell42temp(:,1),S.cell42temp(:,2),'.')
plot(S.cell43temp(:,1),S.cell43temp(:,2),'.')
plot(S.cell44temp(:,1),S.cell44temp(:,2),'.')
plot(S.cell45temp(:,1),S.cell45temp(:,2),'.')
plot(S.cell46temp(:,1),S.cell46temp(:,2),'.')
plot(S.cell47temp(:,1),S.cell47temp(:,2),'.')
plot(S.cell48temp(:,1),S.cell48temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 4 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12'},'Location','southeast')
subplot(2,3,5)
hold on
plot(S.cell49temp(:,1),S.cell49temp(:,2),'.')
plot(S.cell50temp(:,1),S.cell50temp(:,2),'.')
plot(S.cell51temp(:,1),S.cell51temp(:,2),'.')
plot(S.cell52temp(:,1),S.cell52temp(:,2),'.')
plot(S.cell53temp(:,1),S.cell53temp(:,2),'.')
plot(S.cell54temp(:,1),S.cell54temp(:,2),'.')
plot(S.cell55temp(:,1),S.cell55temp(:,2),'.')
plot(S.cell56temp(:,1),S.cell56temp(:,2),'.')
plot(S.cell57temp(:,1),S.cell57temp(:,2),'.')
plot(S.cell58temp(:,1),S.cell58temp(:,2),'.')
plot(S.cell59temp(:,1),S.cell59temp(:,2),'.')
plot(S.cell60temp(:,1),S.cell60temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 5 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12',},'Location','southeast')
subplot(2,3,6)
hold on
plot(S.cell61temp(:,1),S.cell61temp(:,2),'.')
plot(S.cell62temp(:,1),S.cell62temp(:,2),'.')
plot(S.cell63temp(:,1),S.cell63temp(:,2),'.')
plot(S.cell64temp(:,1),S.cell64temp(:,2),'.')
plot(S.cell65temp(:,1),S.cell65temp(:,2),'.')
plot(S.cell66temp(:,1),S.cell66temp(:,2),'.')
plot(S.cell67temp(:,1),S.cell67temp(:,2),'.')
plot(S.cell68temp(:,1),S.cell68temp(:,2),'.')
plot(S.cell69temp(:,1),S.cell69temp(:,2),'.')
plot(S.cell70temp(:,1),S.cell70temp(:,2),'.')
plot(S.cell71temp(:,1),S.cell71temp(:,2),'.')
plot(S.cell72temp(:,1),S.cell72temp(:,2),'.')
ylabel('Temperature (C) or Humidity (%)')
xlabel('Time (ms)')
title('Accumulator Cell Temperatures: Segment 6 Detailed View')
legend({'Temp1','Temp2','Temp3','Temp4','Temp5','Temp6','Temp7','Temp8','Temp9','Temp10','Temp11','Temp12'},'Location','southeast')


%% Accumulator Capacity Analysis
current = S.D4_DC_Bus_Current; %Amps
motorSpeed = S.D2_Motor_Speed; %RPM
voltage = S.D1_DC_Bus_Voltage; %Volts
motorSpeed(:,2) = motorSpeed(:,2)./60; %Rotations per second
consumption = cumtrapz(current(:,1),current(:,2));
consumption = [current(:,1),consumption./3600];
distance = cumtrapz(motorSpeed(:,1),motorSpeed(:,2)); %Rotations
distance = [motorSpeed(:,1),(distance./3)*pi*(tire_diameter/39.37)./1000]; %Kilometers

% Data uniqueness
for i = 1:length(distance(:,1))
    distance(i,1) = distance(i,1) + i/100000000;
end
for i = 1:length(consumption(:,1))
    consumption(i,1) = consumption(i,1) + i/100000000;
end
for i = 1:length(voltage(:,1))
    voltage(i,1) = voltage(i,1) + i/100000000;
end
for i = 1:length(current(:,1))
    current(i,1) = current(i,1) + i/100000000;
end

time = 1:0.1:max(current(:,1)); %Seconds
adjDistance = interp1(distance(:,1),distance(:,2),time);
adjConsumption = interp1(consumption(:,1),consumption(:,2),time);
adjVoltage = interp1(voltage(:,1),voltage(:,2),time);
adjCurrent = interp1(current(:,1),current(:,2),time);
adjPower = adjVoltage.*adjCurrent; %Watts
adjPower(~isfinite(adjPower)) = 0;
adjEnergy = cumtrapz(time(2:end),adjPower(2:end))./3600; %Watt Hours
adjEnergy = adjEnergy./1000; %kWh
% Plotting
figure
subplot(2,1,1)
plot(adjDistance/1000,adjConsumption/1000)
ylabel('Charge (Ah)')
xlabel('Distance Traveled (km)')
title('Accumulator Capacity Usage vs Distance Traveled (No Slip Assumption)')
subplot(2,1,2)
plot(adjDistance(2:end)/1000,adjEnergy/1000)
ylabel('Energy (kWh)')
xlabel('Distance Traveled (km)')
title('Accumulator Energy Expended vs Distance Traveled (No Slip Assumption)')

%% Accumulator Voltage Drop
figure

mask = adjCurrent>10 & adjVoltage>150; %%only use data where current > 10 and voltage >150v
adjCurrent(~mask) = [];
adjVoltage(~mask) = [];

voltageDrop = cat(1, adjCurrent, adjVoltage);
voltageDrop = round(voltageDrop, 2); % Smooth out, only use two decimal places

% Credit: https://www.mathworks.com/matlabcentral/answers/151709-how-can-i-average-points-with-just-the-same-x-coordinate
[uniqueCurrent,~,idx] = unique(voltageDrop(1,:));
averageVoltage = accumarray(idx,voltageDrop(2,:),[],@mean);

plot(uniqueCurrent, averageVoltage,'.-')
xlabel('Current')
ylabel('Voltage')
title('Accumulator Voltage Drop Analysis')
%% VectorNAV IMU data plot goes here


%% Corner Node Data Plot Goes Here

%% Plot function defs
% this can plot two Y-axis vs each other
function p = plot_y_vs_y(series1,series2,series1name,series2name,ptitle)
    for i = 1:length(series1(:,1))
        series1(i,1) = series1(i,1) + i/100000000;
    end
    for i = 1:length(series2(:,1))
        series2(i,1) = series2(i,1) + i/100000000;
    end
    time2 = series2(:,1);
    values2 = series2(:,2);
    time1 = series1(:,1);
    values1 = series1(:,2);
    % Interpolate values of the second matrix onto the time points of the first matrix
    interpolated_values2 = interp1(time2, values2, time1);
    
    % Plot the values
    figure
    hold on
    plot(values1, interpolated_values2, '.');
    xlabel(series1name);
    ylabel(series2name);
    title(ptitle);

end
%% Plot function 3d
% This does not work well lmao
function q = plot_three_series(series1,series2,series3,xyzlabel,ptitle)


    for i = 1:length(series1(:,1))
        series1(i,1) = series1(i,1) + i/100000000;
    end
    for i = 1:length(series2(:,1))
        series2(i,1) = series2(i,1) + i/100000000;
    end
    for i = 1:length(series3(:,1))
        series3(i,1) = series3(i,1) + i/100000000;
    end
   
    time1 = series1(:,1);
    values1 = series1(:,2);
    time2 = series2(:,1);
    values2 = series2(:,2);
    time3 = series3(:,1);
    values3 = series3(:,2);
    % Interpolate values of the second matrix onto the time points of the first matrix
    interpolated_values2 = interp1(time2, values2, time1);
    interpolated_values3 = interp1(time3,values3,time1);
    % Define the threshold value
    threshold = 10;

    % Find the indices where interpolated_values2 is above the threshold
    indices = interpolated_values3 >= threshold;
    filtered_values1 = values1(indices);
    filtered_interpolated_values2 = interpolated_values2(indices);
    filtered_values3 = interpolated_values3(indices);
    % Plot the values in 3D
    plot3(filtered_values1, filtered_interpolated_values2, filtered_values3, '.');
    xlabel(xyzlabel(1));
    ylabel(xyzlabel(2));
    zlabel(xyzlabel(3));
    title(ptitle);
    % Create a meshgrid for the filtered values
    [X, Y] = meshgrid(filtered_values1, filtered_interpolated_values2);
    numel(filtered_values1)
    numel(filtered_interpolated_values2)
    % Create a matrix for the Z values
    Z = repmat(filtered_values3, [numel(filtered_values1), numel(filtered_interpolated_values2)]);

    % Create the surf plot
    surf(X, Y, Z);
    xlabel('Values from Matrix 1');
    ylabel('Interpolated Values from Matrix 2');
    zlabel('Values from Matrix 3');
    title('3D Surface Plot of Three Matrices');
end