/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Arduino.zumoproxsensors');

goog.require('Blockly.Arduino');

Blockly.Arduino['readProximity'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.read();\n';
    return code;
};

Blockly.Arduino['countsGeneric'] = function(block) {

    var sensor = block.getFieldValue('SENSOR_LIST');
    var led = block.getFieldValue('DETECT_LIST');


    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.counts';
    if (sensor == "RIGHT"){
        code += 'RightWith';
    }
    else if(sensor == "LEFT"){
        code += 'LeftWith';
    }
    else{
        code += 'FrontWith';
    }

    if(led=='RIGHT'){
        code+='RightLeds()';
    }
    else{
         code+='LeftLeds()';
    }
    return [code, Blockly.Arduino.ORDER_ATOMIC];
};



Blockly.Arduino['readBasicLeft'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.readBasicLeft()';
    return [code, Blockly.Arduino.ORDER_ATOMIC];
};

Blockly.Arduino['readBasicCenter'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.readBasicCenter()';
    return [code, Blockly.Arduino.ORDER_ATOMIC];
};


Blockly.Arduino['readBasicRight'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

    var globalCode = 'Zumo32U4ProximitySensors proxSensors;';
    Blockly.Arduino.addDeclaration('proxSensors_', globalCode);

    var proxSetupCode = 'proxSensors.initThreeSensors();';
    Blockly.Arduino.addSetup('prox_', proxSetupCode, true);

    var code = 'proxSensors.readBasicRight()';
    return [code, Blockly.Arduino.ORDER_ATOMIC];
};