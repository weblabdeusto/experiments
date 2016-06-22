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
        .appendField(Blockly.Msg.ZUM_LINE_READ);
    this.setColour(Blockly.Blocks.zumolinesensors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip(Blockly.Msg.ZUM_LINE_READ_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_LINE_HELP);
  }
};

Blockly.Blocks['getLineSensorValue'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(Blockly.Msg.ZUM_LINE_GET_1)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.ZUM_LEFT, "0"], [Blockly.Msg.ZUM_CENTERLEFT, "1"], [Blockly.Msg.ZUM_CENTER, "2"], [Blockly.Msg.ZUM_CENTERRIGHT, "3"], [Blockly.Msg.ZUM_RIGHT, "4"]]), "SENSOR_LIST")
        .appendField(Blockly.Msg.ZUM_LINE_GET_2);
    this.setColour(Blockly.Blocks.zumolinesensors.HUE);
    this.setOutput(true, "Number");
    this.setTooltip(Blockly.Msg.ZUM_LINE_GET_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_LINE_HELP);
  },
  getBlockType: function() {
    return Blockly.Types.NUMBER;
  }
};

