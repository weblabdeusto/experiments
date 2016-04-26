/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Arduino.zumolinesensors');

goog.require('Blockly.Arduino');

Blockly.Arduino['basicReadLine'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4LineSensors lineSensors;';
    Blockly.Arduino.addDeclaration('lineSensors_', globalCode);

    var values = 'int values[5] = {0,0,0,0,0};';
    Blockly.Arduino.addDeclaration('values_', values);

    var lineSetupCode = 'lineSensores.initFiveSensors();';
    Blockly.Arduino.addSetup('line_', lineSetupCode, true);

    var code = 'lineSensors.read(values, QTR_EMITTERS_ON);\n';
    return code;
};

Blockly.Arduino['getLineSensorValue'] = function(block) {

    var sensor = block.getFieldValue('SENSOR_LIST');

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4LineSensors lineSensors;';
    Blockly.Arduino.addDeclaration('lineSensors_', globalCode);

    var values = 'int values[5] = {0,0,0,0,0};';
    Blockly.Arduino.addDeclaration('values_', values);

    var lineSetupCode = 'lineSensores.initFiveSensors();';
    Blockly.Arduino.addSetup('line_', lineSetupCode, true);

    var code = 'values[' + sensor + ']';
    return [code, Blockly.Arduino.ORDER_ATOMIC];
};