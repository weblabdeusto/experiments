/**
 * Created by gabi on 7/09/16.
 */
'use strict';

goog.provide('Blockly.Blocks.zumoleds');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumoleds.HUE = 170;

Blockly.Blocks['setLedValue'] = {
  /**
   * Block for creating a 'set pin' to a state.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl(Blockly.Msg.ZUM_LEDS_HELP);
    this.setColour(Blockly.Blocks.zumoleds.HUE);
    this.appendValueInput('LED_STATE')
        .appendField(Blockly.Msg.ZUM_LEDS_SET)
        .appendField(new Blockly.FieldDropdown([[Blockly.Msg.ZUM_LEDS_BLUE, "Blue"], [Blockly.Msg.ZUM_LEDS_RED, "Red"]]), 'LED')
        .appendField(Blockly.Msg.ZUM_LEDS_TO)
        .setCheck(Blockly.Types.BOOLEAN.checkList);
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip(Blockly.Msg.ZUM_LEDS_TIP);
  }
};

