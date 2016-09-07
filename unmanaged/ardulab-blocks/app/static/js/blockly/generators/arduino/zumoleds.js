/**
 * Created by gabi on 22/04/16.
 */

'use strict';

goog.provide('Blockly.Arduino.zumoleds');

goog.require('Blockly.Arduino');

Blockly.Arduino['setLedValue'] = function(block) {

    Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');
    var stateOutput = Blockly.Arduino.valueToCode(
        block, 'LED_STATE', Blockly.Arduino.ORDER_ATOMIC) || 'LOW';
    var led = block.getFieldValue('LED');

    var code = "led"+led+"("+stateOutput+");";

    return code;
};
