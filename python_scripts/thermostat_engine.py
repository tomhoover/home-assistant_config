#-----------------------------------------------------------------------------
# Changes thermostat based on external and internal temps
#-----------------------------------------------------------------------------

# Thermostat thresholds
THRESHOLD_FOR_HEAT = 65
THRESHOLD_FOR_AC   = 75
AC   = {'home': 78, 'away': 80, 'sleep': 75, 'brandon': 75}
HEAT = {'home': 67, 'away': 60, 'sleep': 65}

SLEEP_TIME = [5, 22]

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
aux_heat = (hass.states.get('input_boolean.thermostat_aux_heat').state == 'on')
someone_home = (hass.states.get('sensor.occupancy').state == 'home' or hass.states.get('input_boolean.guest_mode').state == 'on')
brandon_home = (hass.states.get('group.brandon_presence').state == 'home')
on_the_way_home = (hass.states.get('input_boolean.on_the_way_home').state == 'on')
current_time = datetime.datetime.now()
current_hour = current_time.hour
sunday = current_time.weekday() == 6

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

logger.info("Outside: {}, Downstairs: {}, Upstairs: {}, Home: {}, Time: {}, State: {}".format(outside_temp, downstairs_temp, upstairs_temp, someone_home, current_time, state_key))

if aux_heat:
    logger.warning('AUX HEAT IS ON - Outside: {}, Downstairs: {}, Upstairs: {}'.format(outside_temp, downstairs_temp, upstairs_temp))
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_downstairs_heating_1', 'operation_mode': 'aux heat'})
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_upstairs_heating_1', 'operation_mode': 'aux heat'})
    hass.services.call('climate', 'set_temperature', {'entity_id': 'climate.ct101_thermostat_downstairs_heating_1', 'temperature': 55})
    hass.services.call('climate', 'set_temperature', {'entity_id': 'climate.ct101_thermostat_upstairs_heating_1', 'temperature': 55})
elif thermostat_enable:
    target_high = 80
    target_low = 64
    nominal_temp = 72
    mode = 'off'
    if outside_temp > THRESHOLD_FOR_AC or downstairs_temp >= (nominal_temp + 2):
        mode = 'cool'
        target_high = AC[state_key]
        nominal_temp = AC[state_key]
    elif outside_temp < THRESHOLD_FOR_HEAT or downstairs_temp <= (nominal_temp -2):
        mode = 'heat'
        target_low = HEAT[state_key]
        nominal_temp = HEAT[state_key]
#    elif state_key != 'sleep' and (too_hot_inside or too_humid):
#        mode = 'auto'
#        target_high = living_room_temp - 1
#        nominal_temp = living_room_temp - 1
    # Now make service call
    logger.info('Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
    if downstairs_current_mode != mode:
        data_mode = {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'operation_mode': mode}
        hass.services.call('climate', 'set_operation_mode', data_mode)
    if upstairs_current_mode != mode:
        data_mode = {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'operation_mode': mode}
        hass.services.call('climate', 'set_operation_mode', data_mode)
    if mode != 'off':
        if mode == 'cool':
            if sunday and state_key == 'home':
                nominal_temp = nominal_temp - 1
                logger.warning('Sunday - Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
            data_temps = {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
            if brandon_home:
                state_key = 'brandon'
                nominal_temp = AC[state_key]
                logger.warning('Brandon - Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
            data_temps = {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
        if mode == 'heat':
            if sunday and state_key == 'home':
                nominal_temp = nominal_temp + 1
                logger.warning('Sunday - Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
            data_temps = {'entity_id': 'climate.ct101_thermostat_downstairs_heating_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
            data_temps = {'entity_id': 'climate.ct101_thermostat_upstairs_heating_1', 'temperature': nominal_temp}
            hass.services.call('climate', 'set_temperature', data_temps)
else:
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_downstairs_cooling_1', 'operation_mode': 'off'})
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.ct101_thermostat_upstairs_cooling_1', 'operation_mode': 'off'})

if on_the_way_home:
    hass.services.call('input_boolean', 'turn_off', {'entity_id': 'input_boolean.on_the_way_home'})
