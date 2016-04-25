/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Blocks.zumolinesensors');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumolinesensors.HUE = 130;

Blockly.Blocks['basicReadLine'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read line sensors");
    this.setColour(Blockly.Blocks.zumolinesensors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  }
};

Blockly.Blocks['getLineSensorValue'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Left", "0"], ["Center-left", "1"], ["Center", "2"], ["Center-right", "3"], ["Right", "4"]]), "SENSOR_LIST")
        .appendField("line-sensor value");
    this.setColour(Blockly.Blocks.zumolinesensors.HUE);
    this.setOutput(true, "Number");
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  },
  getBlockType: function() {
    return Blockly.Types.NUMBER;
  }
};

