/**
 * Created by gabi on 7/09/16.
 */

'use strict';

goog.provide('Blockly.Arduino.zumoleds');

goog.require('Blockly.Arduino');

Blockly.Arduino['setLedValue'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var led = block.getFieldValue('LED_LIST');
    var value = block.getFieldValue('LED_STATUS');

    var code = "led"+ led +"("+value+");";

    return code;
};

Blockly.Arduino['readProximity2'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.read();\n';
    return code;
};