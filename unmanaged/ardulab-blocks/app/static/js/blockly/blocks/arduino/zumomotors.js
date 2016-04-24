/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Blocks.zumomotors');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumomotors.HUE = 190;

Blockly.Blocks['motorrightspeed'] = {
  init: function() {
    this.appendValueInput("RIGHT_SPEED")
        .setCheck(Blockly.Types.NUMBER.checkList)
        .appendField("Set right motor speed to");
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setInputsInline(true);
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  }
};

Blockly.Blocks['motorleftspeed'] = {
  init: function() {
    this.appendValueInput("LEFT_SPEED")
        .setCheck(Blockly.Types.NUMBER.checkList)
        .appendField("Set left motor speed to");
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setInputsInline(true);
    this.setNextStatement(true, null);
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  }
};

Blockly.Blocks['motorsspeed'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_CENTRE)
        .appendField("Change motors' speed");
    this.appendValueInput("LEFT")
        .setCheck("Number")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Left: ");
    this.appendValueInput("RIGHT")
        .setCheck("Number")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Right:");
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setInputsInline(false);
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  }
};