/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Arduino.zumomotors');

goog.require('Blockly.Arduino');


Blockly.Arduino['motorrightspeed'] = function(block) {

  Blockly.Arduino.addInclude('motors', '#include <Zumo32U4Motors.h>');

  var globalCode = 'Zumo32U4Motors motors;';
  Blockly.Arduino.addDeclaration('motors', globalCode);

  var rightSpeed = Blockly.Arduino.valueToCode(block, 'RIGHT_SPEED',Blockly.Arduino.ORDER_ATOMIC) || '0';

  var code = 'motors.setRightSpeed('+ rightSpeed +');\n';
  return code;
};

Blockly.Arduino['motorleftspeed'] = function(block) {


  Blockly.Arduino.addInclude('motors', '#include <Zumo32U4Motors.h>');

  var globalCode = 'Zumo32U4Motors motors;';
  Blockly.Arduino.addDeclaration('motors', globalCode);

  var leftSpeed = Blockly.Arduino.valueToCode(block, 'LEFT_SPEED',Blockly.Arduino.ORDER_ATOMIC) || '0';

  var code = 'motors.setLeftSpeed('+ leftSpeed +');\n';
  return code;
};

Blockly.Arduino['motorsspeed'] = function(block) {


  Blockly.Arduino.addInclude('motors', '#include <Zumo32U4Motors.h>');

  var globalCode = 'Zumo32U4Motors motors;';
  Blockly.Arduino.addDeclaration('motors', globalCode);

  var right = Blockly.Arduino.valueToCode(block, 'RIGHT',Blockly.Arduino.ORDER_ATOMIC) || '0';
  var left = Blockly.Arduino.valueToCode(block, 'LEFT',Blockly.Arduino.ORDER_ATOMIC) || '0';

  var code = 'motors.setSpeeds('+ left +','+ right +');\n';
  return code;
};