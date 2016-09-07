/**
 * Created by gabi on 7/09/16.
 */
'use strict';

goog.provide('Blockly.Blocks.zumoleds');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumoleds.HUE = 170;

Blockly.Blocks['setLedValue'] = {
    init: function() {
      this.appendDummyInput()
          .appendField(Blockly.Msg.ZUM_SET)
          .appendField(new Blockly.FieldDropdown([[Blockly.Msg.ZUM_BLUE, "Blue"], [Blockly.Msg.ZUM_RED, "Red"]]), "LED_LIST")
          .appendField(Blockly.Msg.ZUM_LED)
          .appendField(Blockly.Msg.ZUM_TO)
          .appendField(new Blockly.FieldDropdown([[Blockly.Msg.HIGH, "0"], [Blockly.Msg.LOW, "1"]]), "LED_STATUS");
      this.setColour(Blockly.Blocks.zumoleds.HUE);
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setTooltip(Blockly.Msg.ZUM_LEDS_TIP);
      this.setHelpUrl(Blockly.Msg.ZUM_LEDS_HELP);
    }
};

//Create a block for allow logic operators as input

Blockly.Blocks['readProximity2'] = {
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