
/**
 * @fileoverview Blocks for library.
 *
 */

'use strict';

goog.provide('Blockly.Blocks.zumobuttons');

goog.require('Blockly.Blocks');
goog.require('Blockly.Types');

Blockly.Blocks.zumobuttons.HUE = 80;

/** Strings for easy reference. */
Blockly.Blocks.zumobuttons.noInstance = 'No_Instances';
Blockly.Blocks.zumobuttons.noName = 'Empty_input_name';

/**
 * Finds all user-created instances of the Button block config.
 * @return {!Array.<string>} Array of instance names.
 */
Blockly.Blocks.zumobuttons.ButtonInstances = function() {
  var buttonList = [];
  var blocks = Blockly.mainWorkspace.getTopBlocks();
  for (var x = 0; x < blocks.length; x++) {
    var getButtonSetupInstance = blocks[x].getButtonSetupInstance;
    if (getButtonSetupInstance) {
      var ButtonInstance = getButtonSetupInstance.call(blocks[x]);
        if (ButtonInstance) {
          buttonList.push(ButtonInstance);
        }
    }
  }
  return buttonList;
};

/**
 * Return a sorted list of instances names for set dropdown menu.
 * @return {!Array.<string>} Array of Button instances names.
 */
Blockly.Blocks.zumobuttons.ButtonDropdownList = function() {
  var ButtonList = Blockly.Blocks.zumobuttons.ButtonInstances();
  var options = [];
  if (ButtonList.length > 0) {
    ButtonList.sort(goog.string.caseInsensitiveCompare);
    // Variables are not language-specific, use the name as both the
    // user-facing text and the internal representation.
    for (var x = 0; x < ButtonList.length; x++) {
      options[x] = [ButtonList[x], ButtonList[x]];
    }
  } else {
    // There are no config blocks in the work area
    options[0] = [Blockly.Blocks.zumobuttons.noInstance,
                  Blockly.Blocks.zumobuttons.noInstance];
  }
  return options;
};

/**
 * Class for a variable's dropdown field.
 * @extends {Blockly.FieldDropdown}
 * @constructor
 */
Blockly.Blocks.zumobuttons.FieldButtonInstance = function() {
  Blockly.Blocks.zumobuttons.FieldButtonInstance.superClass_.constructor
      .call(this, Blockly.Blocks.zumobuttons.ButtonDropdownList);
};
goog.inherits(
    Blockly.Blocks.zumobuttons.FieldButtonInstance, Blockly.FieldDropdown);


Blockly.Blocks['Button_config'] = {
  /**
   * Block for for the Button generator configuration including creating
   * an object instance and setting up the speed. Info in the setHelpUrl link.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl('https://github.com/pololu/pushbutton-arduino');
    this.setColour(Blockly.Blocks.zumobuttons.HUE);
    this.appendDummyInput()
        .appendField("Button")
        .appendField(new Blockly.FieldDropdown([["A", "ButtonA"], ["B", "ButtonB"], ["C", "ButtonC"]]), "BUTTONS")
        .appendField("as")
        .appendField(new Blockly.FieldTextInput('MyButton'), 'BUTTON_NAME');
    this.setTooltip("Block for initializating buttons");
  },
  /**
   * Returns the Button instance name, defined in the 'Button_NAME' input
   * String block attached to this block.
   * @return {!string} List with the instance name.
   * @this Blockly.Block
   */
  getButtonSetupInstance: function() {
    var InstanceName = this.getFieldValue('BUTTON_NAME');
    if (!InstanceName) {
      InstanceName = Blockly.Blocks.zumobuttons.noName;
    }
    // Replace all spaces with underscores
    return InstanceName.replace(/ /g, '_');
  },
  getRobotButton: function() {
    var InstanceName = this.getFieldValue('BUTTONS');

    // Replace all spaces with underscores
    return InstanceName.replace(/ /g, '_');
  }
};

Blockly.Blocks['Button_isPressed'] = {
  /**
   * Block for for the Button 'step()' function.
   * @this Blockly.Block
   */
  init: function() {
    this.setColour(Blockly.Blocks.zumobuttons.HUE);
    this.appendDummyInput()
        .appendField(new Blockly.Blocks.zumobuttons.FieldButtonInstance(),
            'BUTTON_NAME')
        .appendField("is pressed");

    this.setTooltip('Check if a button is pressed');
    this.setHelpUrl('https://github.com/pololu/pushbutton-arduino');
    this.setOutput(true);
  },
  /**
   * Called whenever anything on the workspace changes.
   * It checks the instances of Button_config and attaches a warning to this
   * block if not valid data is found.
   * @this Blockly.Block
   */
  onchange: function() {
    if (!this.workspace) { return; }  // Block has been deleted.

    var currentDropdown = this.getFieldValue('BUTTON_NAME');
    var instances = Blockly.Blocks.zumobuttons.ButtonDropdownList();

    // Check for configuration block presence
    if (instances[0][0] === Blockly.Blocks.zumobuttons.noInstance) {
      // Ensure dropdown menu says there is no config block
      if (currentDropdown !== Blockly.Blocks.zumobuttons.noInstance) {
        this.setFieldValue(Blockly.Blocks.zumobuttons.noInstance, 'BUTTON_NAME');
      }
      this.setWarningText("Buttons must be initializated");
    } else {
      // Configuration blocks present, check if any selected and contains name
      var existingConfigSelected = false;
      for (var x = 0; x < instances.length; x++) {
        // Check if any of the config blocks does not have a name
        if (instances[x][0] === Blockly.Blocks.zumobuttons.noName) {
          // If selected config has no name either, set warning and exit func
          if (currentDropdown === Blockly.Blocks.zumobuttons.noName) {
            //TODO:Change this warning
            this.setWarningText("Unknown warning");
            return;
          }
        } else if (instances[x][0] === currentDropdown) {
          existingConfigSelected = true;
        }
      }

      // At this point select config has a name, check if it exist
      if (existingConfigSelected) {
        // All good, just remove any warnings and exit the function
        this.setWarningText(null);
      } else {
        if ((currentDropdown === Blockly.Blocks.zumobuttons.noName) ||
            (currentDropdown === Blockly.Blocks.zumobuttons.noInstance)) {
          // Just pick the first config block
          this.setFieldValue(instances[0][0], 'BUTTON_NAME');
          this.setWarningText(null);
        } else {
          // Al this point just set a warning to select a valid Button config
          this.setWarningText("Not valid block configuration");
        }
      }
    }
  }
};

Blockly.Blocks['Button_waitFor'] = {
  /**
   * Block for for the Button 'step()' function.
   * @this Blockly.Block
   */
  init: function() {
      this.appendDummyInput()
        .appendField("Wait for")
        .appendField(new Blockly.Blocks.zumobuttons.FieldButtonInstance(),
            'BUTTON_NAME');

    this.setTooltip('Check if a button is pressed');
    this.setHelpUrl('https://github.com/pololu/pushbutton-arduino');
    this.setColour(Blockly.Blocks.zumobuttons.HUE);

    this.setOutput(false);
  },
  /**
   * Called whenever anything on the workspace changes.
   * It checks the instances of Button_config and attaches a warning to this
   * block if not valid data is found.
   * @this Blockly.Block
   */
  onchange: function() {
    if (!this.workspace) { return; }  // Block has been deleted.

    var currentDropdown = this.getFieldValue('BUTTON_NAME');
    var instances = Blockly.Blocks.zumobuttons.ButtonDropdownList();

    // Check for configuration block presence
    if (instances[0][0] === Blockly.Blocks.zumobuttons.noInstance) {
      // Ensure dropdown menu says there is no config block
      if (currentDropdown !== Blockly.Blocks.zumobuttons.noInstance) {
        this.setFieldValue(Blockly.Blocks.zumobuttons.noInstance, 'BUTTON_NAME');
      }
      this.setWarningText("Buttons must be initializated");
    } else {
      // Configuration blocks present, check if any selected and contains name
      var existingConfigSelected = false;
      for (var x = 0; x < instances.length; x++) {
        // Check if any of the config blocks does not have a name
        if (instances[x][0] === Blockly.Blocks.zumobuttons.noName) {
          // If selected config has no name either, set warning and exit func
          if (currentDropdown === Blockly.Blocks.zumobuttons.noName) {
            //TODO:Change this warning
            this.setWarningText("Unknown warning");
            return;
          }
        } else if (instances[x][0] === currentDropdown) {
          existingConfigSelected = true;
        }
      }

      // At this point select config has a name, check if it exist
      if (existingConfigSelected) {
        // All good, just remove any warnings and exit the function
        this.setWarningText(null);
      } else {
        if ((currentDropdown === Blockly.Blocks.zumobuttons.noName) ||
            (currentDropdown === Blockly.Blocks.zumobuttons.noInstance)) {
          // Just pick the first config block
          this.setFieldValue(instances[0][0], 'BUTTON_NAME');
          this.setWarningText(null);
        } else {
          // Al this point just set a warning to select a valid Button config
          this.setWarningText("Not valid block configuration");
        }
      }
    }
  }
};

Blockly.Blocks['Button_singlePressed'] = {
  /**
   * Block for for the Button 'step()' function.
   * @this Blockly.Block
   */
  init: function() {
    this.setHelpUrl('https://github.com/pololu/pushbutton-arduino');
    this.setTooltip('Check if button has been signle pressed');
    this.setColour(Blockly.Blocks.zumobuttons.HUE);
    this.appendDummyInput()
        .appendField(new Blockly.Blocks.zumobuttons.FieldButtonInstance(),
            'BUTTON_NAME')
        .appendField("single press");
    this.setOutput(true);
  },
  /**
   * Called whenever anything on the workspace changes.
   * It checks the instances of Button_config and attaches a warning to this
   * block if not valid data is found.
   * @this Blockly.Block
   */
  onchange: function() {
    if (!this.workspace) { return; }  // Block has been deleted.

    var currentDropdown = this.getFieldValue('BUTTON_NAME');
    var instances = Blockly.Blocks.zumobuttons.ButtonDropdownList();

    // Check for configuration block presence
    if (instances[0][0] === Blockly.Blocks.zumobuttons.noInstance) {
      // Ensure dropdown menu says there is no config block
      if (currentDropdown !== Blockly.Blocks.zumobuttons.noInstance) {
        this.setFieldValue(Blockly.Blocks.zumobuttons.noInstance, 'BUTTON_NAME');
      }
      this.setWarningText("Buttons must be initializated");
    } else {
      // Configuration blocks present, check if any selected and contains name
      var existingConfigSelected = false;
      for (var x = 0; x < instances.length; x++) {
        // Check if any of the config blocks does not have a name
        if (instances[x][0] === Blockly.Blocks.zumobuttons.noName) {
          // If selected config has no name either, set warning and exit func
          if (currentDropdown === Blockly.Blocks.zumobuttons.noName) {
            //TODO:Change this warning
            this.setWarningText("Unknown warning");
            return;
          }
        } else if (instances[x][0] === currentDropdown) {
          existingConfigSelected = true;
        }
      }

      // At this point select config has a name, check if it exist
      if (existingConfigSelected) {
        // All good, just remove any warnings and exit the function
        this.setWarningText(null);
      } else {
        if ((currentDropdown === Blockly.Blocks.zumobuttons.noName) ||
            (currentDropdown === Blockly.Blocks.zumobuttons.noInstance)) {
          // Just pick the first config block
          this.setFieldValue(instances[0][0], 'BUTTON_NAME');
          this.setWarningText(null);
        } else {
          // Al this point just set a warning to select a valid Button config
          this.setWarningText("Not valid block configuration");
        }
      }
    }
  }
};


