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
        .appendField(Blockly.Msg.ZUM_PROX_READ);
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip(Blockly.Msg.ZUM_PROX_READ_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_PROX_HELP);
  }
};

Blockly.Blocks['countsGeneric'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(Blockly.Msg.ZUM_SENSOR_1)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.ZUM_LEFT_M, "LEFT"], [Blockly.Msg.ZUM_CENTER, "CENTER"], [Blockly.Msg.ZUM_RIGHT_M, "RIGHT"]]), "SENSOR_LIST")
        .appendField(Blockly.Msg.ZUM_SENSOR_2);
    this.appendDummyInput()
        .appendField(Blockly.Msg.ZUM_PROX_GET)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.ZUM_LEFT, "LEFT"], [Blockly.Msg.ZUM_RIGHT, "RIGHT"]]), "DETECT_LIST");
    this.setColour(Blockly.Blocks.zumoproxsensors.HUE);
    this.setOutput(true, "Number");
    this.setTooltip(Blockly.Msg.ZUM_PROX_GET_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_PROX_HELP);
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