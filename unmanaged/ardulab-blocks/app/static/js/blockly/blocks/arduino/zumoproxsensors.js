/**
 * Created by gabi on 22/04/16.
 */
'use strict';

goog.provide('Blockly.Blocks.zumoproxsensors');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumoproxsensors.HUE = 130;

Blockly.Blocks['readProximity'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read proximity sensors");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  }
};

Blockly.Blocks['countsGeneric'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["left", "LEFT"], ["center", "CENTER"], ["right", "RIGHT"]]), "SENSOR_LIST")
        .appendField("sensor");
    this.appendDummyInput()
        .appendField("detect on his")
        .appendField(new Blockly.FieldDropdown([["left", "LEFT"], ["right", "RIGHT"]]), "DETECT_LIST");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setOutput(true, "Number");
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  },
  getBlockType: function() {
    return Blockly.Types.NUMBER;
  }
};


Blockly.Blocks['readBasicLeft'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read left sensor");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setOutput(true, "Boolean");
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  },
  getBlockType: function() {
    return Blockly.Types.BOOLEAN;
  }
};

Blockly.Blocks['readBasicCenter'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read center sensor");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setOutput(true, "Boolean");
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  },
  getBlockType: function() {
    return Blockly.Types.BOOLEAN;
  }
};

Blockly.Blocks['readBasicRight'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read right sensor");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setOutput(true, "Boolean");
    this.setTooltip('');
    this.setHelpUrl('http://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_motors.html');
  },
  getBlockType: function() {
    return Blockly.Types.BOOLEAN;
  }
};