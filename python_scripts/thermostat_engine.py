#-----------------------------------------------------------------------------
# Changes thermostat based on external and internal temps
#-----------------------------------------------------------------------------

# Thermostat thresholds
THRESHOLD_FOR_HEAT = 55
THRESHOLD_FOR_AC   = 77
AC   = {'home': 78, 'away': 80, 'sleep': 75, 'brandon': 75}
HEAT = {'home': 68, 'away': 60, 'sleep': 65}

SLEEP_TIME = [6, 22]

# Get current temperatures
#temp2 = hass.states.get('sensor.pws_temp_f').state
temp1 = hass.states.get('sensor.dark_sky_temperature').state

#AC['home'] = hass.states.get('input_number.ac_home').state
#AC['away'] = hass.states.get('input_number.ac_away').state
#AC['sleep'] = hass.states.get('input_number.ac_sleep').state

try:
    outside_temp = float(temp1)
#except TypeError:
#    outside_temp = float(temp2)
except:
    logger.warning("Unable to read outside_temp")

downstairs_temp = float(hass.states.get('sensor.ct101_thermostat_downstairs_temperature').state)
upstairs_temp = float(hass.states.get('sensor.ct101_thermostat_upstairs_temperature').state)

#try:
#    bedroom_temp = float(hass.states.get('sensor.bedroom_temperature').state)
#except ValueError:
#    bedroom_temp = living_room_temp

#living_room_humidity = float(hass.states.get('sensor.living_room_humidity').state)

# Get various system stats
thermostat_enable = (hass.states.get('input_boolean.thermostat_enable').state == 'on')
someone_home = (hass.states.get('sensor.occupancy').state == 'home' or hass.states.get('input_boolean.guest_mode').state == 'on')
brandon_home = (hass.states.get('group.brandon_presence').state == 'home')
on_the_way_home = (hass.states.get('input_boolean.on_the_way_home').state == 'on')
current_time = datetime.datetime.now()
current_hour = current_time.hour

downstairs_current_mode = hass.states.get('climate.ct101_thermostat_downstairs_cooling_1').state
upstairs_current_mode = hass.states.get('climate.ct101_thermostat_upstairs_cooling_1').state

# Determine home, away, or sleep
if someone_home or on_the_way_home:
    state_key = 'home'
    if current_hour <= SLEEP_TIME[0] or current_hour >= SLEEP_TIME[1]:
        state_key = 'sleep'
else:
    state_key = 'away'

# Some logic for high humidity or high indoor temp
#too_humid = living_room_humidity > 59
too_hot_inside = (outside_temp > 74 and ( (downstairs_temp >= (outside_temp + 1)) or (upstairs_temp >= (outside_temp + 1)) ))

logger.warning("Outside: {}, Downstairs: {}, Upstairs: {}, Home: {}, Time: {}, State: {}".format(outside_temp, downstairs_temp, upstairs_temp, someone_home, current_time, state_key))

# Only fire if thermostat is enabled

if thermostat_enable:
    target_high = 82
    target_low = 58
    nominal_temp = 70
    mode = 'off'
    if outside_temp > THRESHOLD_FOR_AC:
        mode = 'cool'
        target_high = AC[state_key]
        nominal_temp = AC[state_key]
    elif outside_temp < THRESHOLD_FOR_HEAT:
        mode = 'heat'
        target_low = HEAT[state_key]
        nominal_temp = HEAT[state_key]
#    elif state_key != 'sleep' and (too_hot_inside or too_humid):
#        mode = 'auto'
#        target_high = living_room_temp - 1
#        nominal_temp = living_room_temp - 1
    # Now make service call
    logger.warning('Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
    if downstairs_current_mode != mode:
        data_mode = {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'operation_mode': mode}
        hass.services.call('climate', 'set_operation_mode', data_mode)
    if upstairs_current_mode != mode:
        data_mode = {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'operation_mode': mode}
        hass.services.call('climate', 'set_operation_mode', data_mode)
    if mode != 'off':
        if mode == 'cool':
            data_temps = {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
            if brandon_home:
                state_key = 'brandon'
                nominal_temp = AC[state_key]
            data_temps = {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
        if mode == 'heat':
            data_temps = {'entity_id': 'climate.ct101_thermostat_downstairs_heating_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
            data_temps = {'entity_id': 'climate.ct101_thermostat_upstairs_heating_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
else:
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'operation_mode': 'off'})
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'operation_mode': 'off'})

if on_the_way_home:
    hass.services.call('input_boolean', 'turn_off', {'entity_id': 'input_boolean.on_the_way_home'})
