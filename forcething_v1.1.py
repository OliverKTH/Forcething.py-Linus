import dearpygui.dearpygui as dpg


import odrive
from odrive.enums import *
import time
import math
import numpy as np

##############################
# Might have to change "axis1" to "axis0" depending on how many motor interfaces the odrive card has
##############################

class SineModulation:
    frequency = 0.0
    amplitude = 0.0
    def __init__(self, frequency, amplitude):
        self.amplitude = amplitude
        self.frequency = frequency

    def modulate(self, time, set_point):
        return set_point + (np.sin(time*(2*np.pi*self.frequency))*self.amplitude)

kg_to_current = 1.0/1.8

# global logging
logging = False

current_position = 0

reference_time = time.time()

graph_update_rate = 1.0/60.0
sample_update_rate = 1.0/1000.0

position_data = [0.0]
applied_weight_data = [1.0]
speed_data = [0.0]

#dpg.set_viewport_vsync(False)
dpg.create_context()
motor = None
print("finding an odrive...")
try:
    motor = odrive.find_any(timeout = 0.1)
except:
    pass

def calibrate():
    motor.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE

def turn_on():

    if(motor.axis1.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL):
        print("AXIS_STATE -> CLOSED_LOOP_CONTROL")
        motor.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    else:
        print("AXIS_STATE -> IDLE")
        motor.axis1.requested_state = AXIS_STATE_IDLE

def clear_errors():
    motor.clear_errors()

def set_force_kg(kg):
    motor.axis1.motor.config.current_lim = kg*kg_to_current

def move_to(position):
    motor.axis1.controller.input_pos = position

def get_input_position():
    return motor.axis1.controller.input_pos

def get_current_position():
    return motor.axis1.encoder.pos_estimate

def get_max_force():
    return motor.axis1.motor.config.current_lim / kg_to_current

def get_current_force():
    return motor.axis1.motor.current_control.Iq_measured / kg_to_current

def get_set_force():
    return motor.axis1.motor.config.current_lim / kg_to_current

def get_current_speed():
    vel = (motor.axis1.encoder.vel_estimate)*(0.03*np.pi*(85.0/16.0))
    return vel

def set_force_button():
    set_force_kg(dpg.get_value("kg_input_double"))

def update_graphs(time):
    position_data.append(get_current_position())
    applied_weight_data.append(get_current_force())
    speed_data.append(get_current_speed())
    
    if len(position_data) > 500:
        position_slice = position_data[-500:]
    else:
        position_slice = position_data

    if len(applied_weight_data) > 500:
        applied_weight_slice = applied_weight_data[-500:]
    else:
        applied_weight_slice = applied_weight_data
    
    if len(speed_data) > 500:
        speed_slice = speed_data[-500:]
    else:
        speed_slice = speed_data

    applied_weight_slice = applied_weight_data[-500:]
    dpg.set_value("position_series", [np.arange(0.0,len(position_slice)),position_slice])
    dpg.set_value("weight_series", [np.arange(0.0,len(applied_weight_slice)),applied_weight_slice])
    dpg.set_value("velocity_series", [np.arange(0.0,len(speed_slice)),speed_slice])
    dpg.fit_axis_data("y_axis")
    dpg.set_axis_limits_auto("y_axis")
    dpg.fit_axis_data("x_axis")
    dpg.set_axis_limits_auto("x_axis")

def start_recording():
    global logging
    if(logging == False):
        print("Start recording...")
        logging = bool(True)
    else:
        print("...stop recording")
        logging = bool(False)


logfile = open("data.csv", "a")
logfile.write("TIME;POSITION;WEIGHT;SPEED\n")

def log_data():
    current_time = (time.time()) - reference_time
    pos = get_current_position()
    current_weight = get_current_force()
    speed = get_current_speed()
    logfile.write(f"{current_time};{pos};{current_weight};{speed}\n")
    logfile.flush()

def move_increment_positive():
    increment = dpg.get_value("move_increment")
    move_increment(increment)

def move_increment_negative():
    increment = dpg.get_value("move_increment")
    move_increment(-increment)

def move_increment(increment):
    motor.axis1.controller.input_pos = motor.axis1.controller.input_pos + (increment/(3*np.pi*(16.0/85.0)))

def update_info(time):
    pos = get_current_position()
    set_weight = get_set_force()
    current_weight = get_current_force()
    vel = get_current_speed()

    dpg.set_value("position_no", "{:.2f}cm".format(pos*3*np.pi*(16.0/85.0)))
    dpg.set_value("set_weight_no", "{:.2f}kg".format(set_weight))
    dpg.set_value("current_weight_no", "{:.2f}kg".format(current_weight))
    dpg.set_value("velocity_no", "{:.2f}m/s".format(vel))

with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    big_font = dpg.add_font("NotoSerifCJKjp-Medium.otf", 50)
    medium_font = dpg.add_font("NotoSerifCJKjp-Medium.otf", 30)
    small_font = dpg.add_font("NotoSerifCJKjp-Medium.otf", 10)

with dpg.value_registry():
    dpg.add_bool_value(default_value=False, tag="record_position_bool")
    dpg.add_bool_value(default_value=False, tag="record_set_weight_bool")
    dpg.add_bool_value(default_value=False, tag="record_current_weight_bool")
    dpg.add_bool_value(default_value=False, tag="sine_modulation_time_bool")
    dpg.add_bool_value(default_value=False, tag="sine_modulation_distance_bool")

with dpg.window(label="Reel", tag="reel_window"):
    dpg.add_button(label="+", tag="reel_out_button", callback=move_increment_positive)
    dpg.add_button(label="-", tag="reel_in_button", callback=move_increment_negative)
    dpg.add_input_double(label="(cm)", tag="move_increment", default_value=10.0)

with dpg.window(label="Info", tag="info_window"):
    dpg.add_text(label="Set Weight", tag="set_weight_text")
    dpg.set_value("set_weight_text", "Set Weight")

    set_weight_no = dpg.add_text(label="Set Weight Number", tag="set_weight_no")
    dpg.set_value("set_weight_no", "!!!!")
    dpg.bind_item_font(set_weight_no, medium_font)

    dpg.add_text(label="Current weight", tag="current_weight_text")
    dpg.set_value("current_weight_text", "Current Weight")

    current_weight_no = dpg.add_text(label="Current weight Number", tag="current_weight_no")
    dpg.set_value("current_weight_no", "!!!!")
    dpg.bind_item_font(current_weight_no, medium_font)

    dpg.add_text(label="Position", tag="position_text")
    dpg.set_value("position_text", "Position")

    position_no = dpg.add_text(label="Position Number", tag="position_no")
    dpg.set_value("position_no", "!!!!")
    dpg.bind_item_font(position_no, medium_font)

    dpg.add_text(label="Current Velocity", tag="velocity_text")
    dpg.set_value("velocity_text", "Current Velocity")

    velocity_no = dpg.add_text(label="velocity Number", tag="velocity_no")
    dpg.set_value("velocity_no", "!!!!")
    dpg.bind_item_font(velocity_no, medium_font)

with dpg.window(label="Record", tag="record_window"):
    dpg.add_checkbox(label="Position", tag="record_position", source="record_position_bool")
    dpg.add_checkbox(label="Set Weight", tag="record_set_weight", source="record_set_weight_bool")
    dpg.add_checkbox(label="Current Weight", tag="record_current_weight", source="record_current_weight_bool")
    dpg.add_text(label="Sample Rate (Hz)", tag="record_sample_rate_text", default_value=1000.0)
    dpg.set_value("record_sample_rate_text","Sample Rate (Hz)")

    dpg.add_input_double(label="", tag="record_sample_rate", default_value=1000.0)
    dpg.add_button(label="Start Recording", tag="start_recording_button", callback=start_recording)

with dpg.window(label="Modulation", tag="modulation_window"):
    dpg.add_checkbox(label="Time Sine", tag="sine_modulation_time", source="sine_modulation_time_bool")
    dpg.add_checkbox(label="Position Sine", tag="sine_modulation_distance", source="sine_modulation_distance_bool")
    dpg.add_input_double(label="Freq", tag="sine_frequency", default_value=1.0)
    dpg.add_input_double(label="Min", tag="sine_min", default_value=10.0)
    dpg.add_input_double(label="Max", tag="sine_max", default_value=20.0)

dpg.set_item_pos("info_window", [435, 10])
dpg.set_item_pos("record_window", [600, 10])
dpg.set_item_pos("reel_window", [600, 190])
dpg.set_item_pos("modulation_window", [600, 300])
dpg.set_item_width("info_window", 150)
dpg.set_item_width("record_window", 150)
dpg.set_item_width("reel_window", 150)
dpg.set_item_width("modulation_window", 150)

with dpg.window(label="Status", tag="win"):

    with dpg.group(horizontal=True):
        dpg.add_button(label="calibrate", callback=calibrate, tag="calibrate_button")
        dpg.add_button(label="turn on/off", callback=turn_on, tag="turn_on_button")
        dpg.add_button(label="Clear Errors", callback=clear_errors, tag="clear_errors_button")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Set Weight", callback=set_force_button, tag="set_weigth_button")
        dpg.add_input_double(label="Weight (kg)", tag="kg_input_double")

    # create plot
    with dpg.plot(label="Line Series", height=400, width=400):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="x_axis")
        dpg.fit_axis_data("x_axis")
        dpg.set_axis_limits_auto("x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")
        dpg.fit_axis_data("y_axis")
        dpg.set_axis_limits_auto("y_axis")

        # series belong to a y axis
        dpg.add_line_series(np.arange(0.0,len(applied_weight_data)),applied_weight_data, label="Applied Weight", parent="y_axis", tag="weight_series")
        dpg.add_line_series(np.arange(0.0,len(position_data)),position_data, label="Position", parent="y_axis", tag="position_series")
        dpg.add_line_series(np.arange(0.0,len(speed_data)),speed_data, label="current velocity", parent="y_axis", tag="velocity_series")


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()

last_time1 = 0.0
last_time2 = 0.0
while(dpg.is_dearpygui_running()):

    current_time = time.time()
    if(current_time > last_time1 + graph_update_rate) and motor != None:
        update_graphs(current_time)
        update_info(current_time)
        last_time1 = current_time
        
        sine_frequency = dpg.get_value("sine_frequency")
        sine_amplitude = (dpg.get_value("sine_max") - dpg.get_value("sine_min"))/2.0
        sine_offset = dpg.get_value("sine_min") + (sine_amplitude)
        
        if dpg.get_value("sine_modulation_time") and motor != None and sine_frequency > 0.00001:
            sine = SineModulation(sine_frequency, sine_amplitude)
            set_force_kg(sine.modulate(current_time, sine_offset))

        if dpg.get_value("sine_modulation_distance") and motor != None and sine_frequency > 0.00001:
            sine = SineModulation(sine_frequency, sine_amplitude)
            set_force_kg(sine.modulate(get_current_position(), sine_offset))
        
   
    if(dpg.get_value("record_sample_rate") and motor != None and sample_update_rate < 1.0):
        sample_update_rate= 1.0/(dpg.get_value("record_sample_rate"))
    else :
        sample_update_rate= 1.0/10.0
    
    current_time = time.time()
    if(current_time > last_time2 + sample_update_rate) and motor != None: 
        last_time2 = current_time
        if logging:
            log_data()
            speed_data.append(get_current_speed())
        

    if(motor == None):
        try:
            motor = odrive.find_any(timeout = 0.1)
        except:
            pass
    dpg.render_dearpygui_frame()   
dpg.destroy_context()
logfile.close()
