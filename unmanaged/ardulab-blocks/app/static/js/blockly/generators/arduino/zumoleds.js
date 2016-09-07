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