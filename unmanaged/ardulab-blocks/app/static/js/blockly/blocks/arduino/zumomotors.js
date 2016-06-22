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
        .appendField(Blockly.Msg.ZUM_MOT_SET_RS);
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setInputsInline(true);
    this.setTooltip(Blockly.Msg.ZUM_MOT_SET_RS_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_MOT_SET_RS_HELP);
  }
};

Blockly.Blocks['motorleftspeed'] = {
  init: function() {
    this.appendValueInput("LEFT_SPEED")
        .setCheck(Blockly.Types.NUMBER.checkList)
        .appendField(Blockly.Msg.ZUM_MOT_SET_LS);
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setInputsInline(true);
    this.setNextStatement(true, null);
    this.setTooltip(Blockly.Msg.ZUM_MOT_SET_LS_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_MOT_SET_LS_HELP);
  }
};

Blockly.Blocks['motorsspeed'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_CENTRE)
        .appendField(Blockly.Msg.ZUM_MOT_SET_2S);
    this.appendValueInput("LEFT")
        .setCheck("Number")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(Blockly.Msg.ZUM_LEFT_M);
    this.appendValueInput("RIGHT")
        .setCheck("Number")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(Blockly.Msg.ZUM_RIGHT_M);
    this.setColour(Blockly.Blocks.zumomotors.HUE);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setInputsInline(false);
    this.setTooltip(Blockly.Msg.ZUM_MOT_SET_2S_TIP);
    this.setHelpUrl(Blockly.Msg.ZUM_MOT_SET_2S_HELP);
  }
};