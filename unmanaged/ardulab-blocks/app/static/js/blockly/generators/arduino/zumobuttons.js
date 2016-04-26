/**
 * @license Licensed under the Apache License, Version 2.0 (the "License"):
 *          http://www.apache.org/licenses/LICENSE-2.0
 */

/**
 * @fileoverview Arduino code generator for the Button library blocks.
 *     The Arduino Button library docs: http://arduino.cc/en/Reference/Button
 */
'use strict';

goog.provide('Blockly.Arduino.zumobuttons');

goog.require('Blockly.Arduino');


/**
 * Code generator for the Button generator configuration. Nothing is added
 * to the 'loop()' function. Sets the pins (X and Y), steps per revolution (Z),
 * speed(A) and instance name (B).
 * Arduino code: #include <Button.h>
 *               Button B(Z, X, Y);
 *               setup() { B.setSpeed(A); }
 * @param {!Blockly.Block} block Block to generate the code from.
 * @return {string} Empty string as no code goes into 'loop()'.
 */
Blockly.Arduino['Button_config'] = function(block) {

  var ButtonName = block.getButtonSetupInstance();
  var robotButton = block.getRobotButton();


  Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

  var globalCode = 'Zumo32U4' + robotButton + ' '+ ButtonName+';';
  Blockly.Arduino.addDeclaration('Button_' + ButtonName, globalCode);


  return '';
};

/**
 * Code generator for moving the Button instance (X) a number of steps (Y).
 * Library info in the setHelpUrl link.
 * This block requires the Button_config block to be present.
 * Arduino code: loop { X.steps(Y) }
 * @param {!Blockly.Block} block Block to generate the code from.
 * @return {array} Completed code with order of operation.
 */
Blockly.Arduino['Button_isPressed'] = function(block) {

  Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

  var ButtonInstanceName = block.getFieldValue('BUTTON_NAME');
  var code = ButtonInstanceName + '.isPressed()';
  return [code, Blockly.Arduino.ORDER_ATOMIC];
};

Blockly.Arduino['Button_waitFor'] = function(block) {
  var ButtonInstanceName = block.getFieldValue('BUTTON_NAME');
  var waitForCode = block.getFieldValue('BUTTON_NAME') + '.waitForButton();\n';

  Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

  Blockly.Arduino.addSetup('serial_' + ButtonInstanceName, waitForCode, true);
  return;
};

Blockly.Arduino['Button_singlePressed'] = function(block) {
  var ButtonInstanceName = block.getFieldValue('BUTTON_NAME');

  Blockly.Arduino.addInclude('zumo', '#include <Wire.h>\n#include <Zumo32U4.h>');

  var code = ButtonInstanceName + '.getSingleDebouncedPress()';
  return [code, Blockly.Arduino.ORDER_ATOMIC];
};