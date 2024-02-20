close all
%% 
% Usage:
% 1. Load the data struct into the Workspace (output.mat)
% 2. Run individual sections of the script to plot the desired data
%% RPM, IQ, and Inverter Fault Flags
figure
iq=S.D4_Iq;
id=S.D3_Id;
runfaults_lo=S.D3_Run_Fault_Lo;
rpm=S.D2_Motor_Speed;
inverter_v = S.D1_DC_Bus_Voltage;
acc_v = S.Pack_Inst_Voltage;
torque_request=S.D1_Commanded_Torque;
torque_command = S.Torque_Command;
% get daxis and qaxis current and find magnitude of their vector
% "By convention, the quadrature axis always will lead the direct axis
% electrically by 90 deg."
daxis=id(:,2);
qaxis=iq(:,2);
qaxiss = qaxis.^2;
daxiss=daxis.^2;
total_motor_current = sqrt(qaxiss+daxiss);
hold on
plot(iq(:,1)/1000,iq(:,2));
plot(id(:,1)/1000,id(:,2))
plot(runfaults_lo(:,1)/1000,runfaults_lo(:,2))
plot(rpm(:,1)/1000,rpm(:,2)/10)
plot(inverter_v(:,1)/1000,inverter_v(:,2))
plot(acc_v(:,1)/1000,acc_v(:,2))
plot(iq(:,1)/1000,total_motor_current)
plot(torque_request(:,1)/1000,torque_request(:,2))
plot(torque_command(:,1)/1000,torque_command(:,2))

ylim([-100 600]);
title('Motor Currents, RPM, Inverter Fault Code, Inverter and BMS voltage')
xlabel('Time (s)')
h = zoom;
set(h,'Motion','horizontal','Enable','on');
legend({'iq','id','faults_lo','rpm/10','inverter DC bus voltage', ...
    'BMS battery pack voltage','total motor current', ...
    'torque request','torque command'})
% everything after this point will not work due to incompatibility with DBC
% parsing, these functions were designed for the manually written parsing
%% Torque, Vehicle Speed, Current, mega plot
figure

uptime=S.D3_Power_On_Timer;
requested_torque = S.Torque_Command;
commanded_torque = S.D1_Commanded_Torque;
busVoltage = S.D1_DC_Bus_Voltage;
busCurrent = S.D4_DC_Bus_Current;
motor_speed = S.D2_Motor_Speed;
pedal_data = S.APPS1(:, 2);
pedal_time = S.APPS1(:, 1);
discharge_current_limit=S.Pack_DCL;

hold on
plot(motor_speed(:,1)/1000,motor_speed(:,2)/100);
plot(busCurrent(:,1)/1000, busCurrent(:,2)./4);
plot(commanded_torque(:,1)/1000,commanded_torque(:,2)./10);
plot(requested_torque(:,1)/1000,requested_torque(:,2)./10);
plot(uptime(:,1)/1000,uptime(:,2)/10);
plot(busVoltage(:,1)/1000,busVoltage(:,2)./10);
plot(pedal_time/1000, (pedal_data./10)-93, '.-');
plot(discharge_current_limit(:,1)/1000,discharge_current_limit(:,2));

legend({'Motor Speed (RPM)*0.01', ...
    'Current (A)*0.25',...
    'Commanded Torque*0.1 (Nm)', ...
    'Requested Torque*0.1 (Nm)', ...
    'Uptime (s)', ...
    'DC Voltage(V*0.1)', ...
    'Accel position',"DCL"})
xlabel('Time (s)')
ylim("auto")
ylim([-10 300]);
title('Torque, Speed, Current')
h = zoom;
set(h,'Motion','horizontal','Enable','on');



%% Torque, Vehicle Speed, Current
figure

requested_torque = S.Torque_Command;
commanded_torque = S.D1_Commanded_Torque;
feedback_torque = S.D2_Torque_Feedback;
max_torque=S.VCU_MAX_TORQUE;
busCurrent = S.D4_DC_Bus_Current;
busVoltage = S.D1_DC_Bus_Voltage;
motor_speed = S.D2_Motor_Speed;
vehicle_speed_mph = motor_speed;
vehicle_speed_mph(:,2) = motor_speed(:,2).*(10/29).*18.*pi.*60./63360; %%correct mph equation

hold on
plot(motor_speed(:,1)/1000,motor_speed(:,2)./100);
plot(max_torque(:,1)/1000,max_torque(:,2).*.2);
plot(busCurrent(:,1)/1000,busCurrent(:,2)./4);
plot(commanded_torque(:,1)/1000,commanded_torque(:,2)./10);
plot(vehicle_speed_mph(:,1)/1000,vehicle_speed_mph(:,2));
plot(requested_torque(:,1)/1000,requested_torque(:,2)./10);
plot(S.D1_DC_Bus_Voltage(:,1)/1000,S.D1_DC_Bus_Voltage(:,2)/4);
legend({'Motor Speed (RPM)*0.01', ...
       'Max Torque (Nm) *.2', ...
       'Current (A)*0.25', ...
       'Commanded Torque*0.1 (Nm)', ...
       'Vehicle Speed (Mph)', ...
       'Requested Torque*0.1 (Nm)', ...
       'DC voltage (v)*0.25'})
xlabel('Time (s)')
title('Torque, Speed, Current')
h = zoom;

set(h,'Motion','horizontal','Enable','on');

%% IDK what this gon be
motor_speed = S.D2_Motor_Speed;
vehicle_speed_mph = motor_speed;
vehicle_speed_mph(:,2) = motor_speed(:,2).*(10/29).*0.000284091.*pi.*60;
figure
hold on
plot(S.D4_DC_Bus_Current(:,1)/1000, S.D4_DC_Bus_Current(:,2), '.-');
plot(S.D1_DC_Bus_Voltage(:,1)/1000, S.D1_DC_Bus_Voltage(:,2), '.-'); 
plot(S.D4_Iq_Command(:,1)/1000,S.D4_Iq_Command(:,2));
plot(vehicle_speed_mph(:,1)/1000,vehicle_speed_mph(:,2)*10);
grid on
xlabel('Time (s)')
ylabel('stuff')
title('stuff')
legend({'DC current','DC voltage','iq command','mph'})
h = zoom;
set(h,'Motion','horizontal','Enable','on');
%% Pedal Input Traces
figure

front_brakes_data = S.BSE1(:, 2);
front_brakes_time = S.BSE1(:, 1);

pedal_data = S.APPS1(:, 2);
pedal_time = S.APPS1(:, 1);
% 
% % Normalizing and cleaning pedal traces
% front_brakes_data = front_brakes_data - mode(front_brakes_data);
% front_brakes_data(front_brakes_data < 0) = 0;
% front_brakes_data = front_brakes_data/max(front_brakes_data);
% 
% pedal_data = pedal_data - mode(pedal_data);
% pedal_data(pedal_data < 0) = 0;
% pedal_data = pedal_data/max(pedal_data);

hold on
plot(pedal_time, pedal_data, '.-');
plot(front_brakes_time, front_brakes_data, '.-');
grid on

xlabel('Time (s)')
ylabel('Normalized Pedal Position and Brake Pressure')
title('Brake and Pedal Traces')
legend({'Accelerator Pedal Position','Brake Pressure'})
h = zoom;
set(h,'Motion','horizontal','Enable','on');
%% DC Bus Current, DC Bus Voltage, and Calculated DC Power Output
figure
voltage = S.D1_DC_Bus_Voltage; 
current = S.D4_DC_Bus_Current;

% Data uniqueness
for i = 1:length(voltage(:,1)/1000)
    voltage(i,1) = voltage(i,1) + i/100000000;
end
for i = 1:length(current(:,1)/1000)
    current(i,1) = current(i,1) + i/100000000;
end
    
time = 1:0.1:max(current(:,1)/1000); %Seconds
current_adj = interp1(current(:,1)/1000,current(:,2),time);
voltage_adj = interp1(voltage(:,1)/1000,voltage(:,2),time);
power = current_adj.*voltage_adj/100;
pedal_data = S.APPS1(:, 2);
pedal_time = S.APPS1(:, 1);

hold on
plot(S.D4_DC_Bus_Current(:,1)/1000, S.D4_DC_Bus_Current(:,2), '.-');
plot(S.D1_DC_Bus_Voltage(:,1)/1000, S.D1_DC_Bus_Voltage(:,2), '.-'); 
% plot(S.iq_command(:,1)/1000,S.iq_command(:,2),'-');
% plot(S.id_command(:,1)/1000,S.id_command(:,2),'-');
%%plot(S.phase_b_current(:,1)/1000,abs(S.phase_b_current(:,2)));
%%plot(S.phase_c_current(:,1)/1000,abs(S.phase_c_current(:,2)));
%%plot(S.Vd_voltage(:,1)/1000,S.Vd_voltage(:,2),'m');
%%plot(S.Vq_voltage(:,1)/1000,S.Vq_voltage(:,2),'y');

plot(time, power, '.-');
plot(S.D1_Commanded_Torque(:,1)/1000,S.D1_Commanded_Torque(:,2)*10);
% plot(S.Iq_Feedback(:,1)/1000,S.Iq_Feedback(:,2));
%%plot(S.State(:,1)/1000,S.State(:,2)*50);
%%plot(pedal_time, (pedal_data./10)-93, '.-');
yyaxis right
plot(S.D2_Motor_Speed(:,1)/1000,S.D2_Motor_Speed(:,2));
grid on
%%ylim([-10 410]);

xlabel('Time (s)')
ylabel('Voltage (V), Current (A), Power (kW)')
title('DC Bus Current, DC Bus Voltage, and Calculated DC Power Output')
% legend({'Current','Voltage', ...
%     'Iq Command (A)', ...
%     'Id Command (A)',......
%     ...'Phase A current','phase b curr','phase c curr', ...
%     ...'D-axis V','Q-axis V', ...
%     ...'Power', ...
%     'Commanded Torque (Nm)/10','Iq feedback (A)','Motor speed(RPM)/10'})
legend({'Current','Voltage','Power','yeet','Motor rpm'})

h = zoom;
set(h,'Motion','horizontal','Enable','on');
%% Cooling Loop: Motor and MCU Temperatures
figure

hold on
plot(S.D4_Gate_Driver_Board(:,1)/1000,S.D4_Gate_Driver_Board(:,2))
plot(S.D1_Control_Board_Temperature(:,1)/1000,S.D1_Control_Board_Temperature(:,2))
plot(S.D1_Module_A(:,1)/1000,S.D1_Module_A(:,2))
plot(S.D2_Module_B(:,1)/1000,S.D2_Module_B(:,2)) 
plot(S.D3_Module_C(:,1)/1000,S.D3_Module_C(:,2))
plot(S.D3_Motor_Temperature(:,1)/1000,S.D3_Motor_Temperature(:,2))
plot(S.D4_DC_Bus_Current(:,1)/1000,S.D4_DC_Bus_Current(:,2)*0.25) 
plot(S.High_Temperature(:,1)/1000,S.High_Temperature(:,2))
plot(S.Low_Temperature(:,1)/1000,S.Low_Temperature(:,2))
%%plot(S.DCL(:,1)/1000,S.DCL(:,2));
grid on

legend({'MCU Gate Driver Board Temperature','MCU Control Board Temperature','MCU Module A Temperature','MCU Module B Temperature','MCU Module C Temperature','Motor Temperature','Current (A)*0.25','Pack High Cell Temp(C)','Low Pack Cell Temp(C)'})
xlabel('Time (s)')
ylabel('Temperature (C)')
title('Cooling Loop Temperature Plots')
h = zoom;
set(h,'Motion','horizontal','Enable','on');
%% BMS Acc Voltage Readings vs Inverter Readings and Current
figure

hold on
plot(S.D4_DC_Bus_Current(:,1)/1000,S.D4_DC_Bus_Current(:,2))
plot(S.Pack_Current(:,1)/1000,S.Pack_Current(:,2))
plot(S.D1_DC_Bus_Voltage(:,1)/1000,S.D1_DC_Bus_Voltage(:,2))
plot(S.Pack_Inst_Voltage(:,1)/1000,S.Pack_Inst_Voltage(:,2))
plot(S.Pack_Open_Voltage(:,1)/1000,S.Pack_Open_Voltage(:,2))
plot(S.Pack_Summed_Voltage(:,1)/1000,S.Pack_Summed_Voltage(:,2))
ylabel('yes')
xlabel('Time (s)')
title('BMS Acc Voltage Readings vs Inverter Readings and Current')
legend('Inverter DC Bus Current','Orion BMS Pack Current','Inverter DC Bus Voltage','Instant Voltage','Open Voltage','Summed Voltage')

%% Accumulator Capacity Analysis
current = S.D4_DC_Bus_Current; %Amps
motorSpeed = S.D2_Motor_Speed; %RPM
voltage = S.D1_DC_Bus_Voltage; %Volts
motorSpeed(:,2) = motorSpeed(:,2)./60; %Rotations per second
consumption = cumtrapz(current(:,1),current(:,2));
consumption = [current(:,1),consumption./3600];
distance = cumtrapz(motorSpeed(:,1),motorSpeed(:,2)); %Rotations
distance = [motorSpeed(:,1),(distance./2.9)*pi*0.4572./1000]; %Kilometers

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
h = zoom;
set(h,'Motion','horizontal','Enable','on');

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

%% IMU Accelerometer
figure
try
    lat_accel = S.lat_accel;
    long_accel = S.long_accel;
    vert_accel = S.vert_accel;
    hold on
    
    plot(lat_accel(:,1)/1000,lat_accel(:,2));
    plot(long_accel(:,1)/1000,long_accel(:,2));
    plot(vert_accel(:,1)/1000,vert_accel(:,2));
    xlabel('Time (s)');
    ylabel('m/s^2');
    legend({'Lateral Acceleration','Longitudinal Acceleration','Vertical Acceleration'})
    title('IMU Accelerometer')
    
    figure
    
    yaw = S.yaw;
    pitch = S.pitch;
    roll = S.roll;
    hold on
    
    plot(yaw(:,1)/1000,yaw(:,2));
    plot(pitch(:,1)/1000,pitch(:,2));
    plot(roll(:,1)/1000,roll(:,2));
    xlabel('Time (s)')
    ylabel('deg/s')
    legend({'Yaw','Pitch', 'Roll'})
    title('IMU Gyroscope')
catch ME
    print("lol")
end
%% SAB
tiledlayout(2,1)
rpm_fl = S.RPM_FL;
rpm_fr = S.RPM_FR;
ax1 = nexttile;
hold on

plot(rpm_fl(:,1)/1000,rpm_fl(:,2));
plot(rpm_fr(:,1)/1000,rpm_fr(:,2));
plot(S.D2_Motor_Speed(:,1)/1000,S.D2_Motor_Speed(:,2));

legend({'RPM Front left','RPM front right','Motor RPM'});
xlabel('Time (s)')
title('Front Wheel Speeds vs Motor RPM')
ylim([-10 4000]);
ax2 = nexttile;
hold on
plot(rpm_fl(:,1)/1000,rpm_fl(:,2).*18.*pi.*60./63360);
plot(rpm_fr(:,1)/1000,rpm_fr(:,2).*18.*pi.*60./63360);
vehicle_speed_mph = motor_speed;
vehicle_speed_mph(:,2) = motor_speed(:,2).*(10/29).*18.*pi.*60./63360; %%correct mph equation
plot(commanded_torque(:,1)/1000,commanded_torque(:,2)./10);
plot(vehicle_speed_mph(:,1)/1000,vehicle_speed_mph(:,2));
legend({'Front Left mph','Front Right mph','Torque Command / 10','Motor Mph'});
ylim([-10 100]);

set(gca,'XMinorTick','on')
linkaxes([ax1 ax2],'x')

%% Feedback Torque vs Requested & Commanded
tiledlayout(2,1)

ax1 = nexttile;
hold on
plot(S.D2_Torque_Feedback(:,1)/1000,S.D2_Torque_Feedback(:,2));
plot(S.D1_Commanded_Torque(:,1)/1000,S.D1_Commanded_Torque(:,2));
legend({'Torque Feedback','Torque Command','-x'});
xlabel('Time (s)')
title('Torque and Q-axis current')

ax2 = nexttile;
hold on
plot(S.D4_Iq_Command(:,1)/1000,S.D4_Iq_Command(:,2));
plot(S.D4_Iq(:,1)/1000,S.D4_Iq(:,2));
plot(S.D3_Id_Command(:,1)/1000,S.D3_Id_Command(:,2));
plot(S.D3_Id(:,1)/1000,S.D3_Id(:,2));
legend({'Iq Command','Iq Feedback','Id cmd','Id feedback','-x'});


set(gca,'XMinorTick','on')
linkaxes([ax1 ax2],'x')

% %% RPM vs Feedb
% % 
% % 
% % ack
% figure
% hold on
% plot(S.D2_Motor_Speed(:,1),S.D2_Motor_Speed(:,2));
% plot(S.Id_Feedback(:,1),S.Id_Feedback(:,2));
% plot(S.Iq_Feedback(:,1),S.Iq_Feedback(:,2));
% legend({'motor speed','Id Feedback','Iq feedback'});
% 
% %% misc
% m = max(S.Id_Feedback(:,2));
% %% tuff
% figure 
% hold on
% plot(S.TSVoltage(:,1)/1000,S.TSVoltage(:,2));
% plot(S.AccVoltage(:,1)/1000,S.AccVoltage(:,2));
% plot(S.State(:,1)/1000,S.State(:,2));
% plot(S.D2_Motor_Speed(:,1)/1000,S.D2_Motor_Speed(:,2)/100);
% legend({'TS Voltage','acc v','state'});
% %% shonk pots vs speed
% figure
% rpm_fl = S.rpm_front_left;
% rpm_fr = S.rpm_front_right;
% shonk_multiplier=0.0001875;
% hold on 
% 
% plot(S.Shonk_FL(:,1)/1000,75-S.Shonk_FL(:,2)*shonk_multiplier/5*75,'LineWidth',2);
% plot(S.Shonk_FR(:,1)/1000,75-S.Shonk_FR(:,2)*shonk_multiplier/5*75,'LineWidth',2);
% plot(S.Shonk_RL(:,1)/1000,S.Shonk_RL(:,2)*shonk_multiplier/5*100,'LineWidth',2);
% plot(S.Shonk_RR(:,1)/1000,S.Shonk_RR(:,2)*shonk_multiplier/5*100,'LineWidth',2);
% yyaxis right
% vehicle_speed_mph = S.D2_Motor_Speed;
% vehicle_speed_mph(:,2) = S.D2_Motor_Speed(:,2).*(10/29).*18.*pi.*60./63360; %%correct mph equation
% plot(vehicle_speed_mph(:,1)/1000,vehicle_speed_mph(:,2),'LineWidth',2);
% %%scatter(S.D2_Motor_Speed(:,1)/1000,1000);
% plot(S.D1_Commanded_Torque(:,1)/1000,S.D1_Commanded_Torque(:,2)/4,'.-');
% plot(rpm_fl(:,1)/1000,rpm_fl(:,2).*18.*pi.*60./63360,'LineWidth',2);
% plot(rpm_fr(:,1)/1000,rpm_fr(:,2).*18.*pi.*60./63360,'LineWidth',2);
% ylim([-10 60])
% legend({'Shonk FL mm','Shonk FR mm','Shonk RR mm','Shonk RL mm','Vehicle MPH','Torque command Nm * 0.25','FL MPH','FR MPH'});
% 
% 
