odoo.define("your_module.id_mask_widget", function (require) {
  "use strict";

  var AbstractField = require("web.AbstractField");
  var fieldRegistry = require("web.field_registry");

  var IdMaskWidget = AbstractField.extend({
    className: "o_field_mask",
    tagName: "input",

    events: {
      input: "_onInput",
    },

    init: function () {
      this._super.apply(this, arguments);
      this.mask = this.nodeOptions.mask || "";
    },

    _render: function () {
      this.$el.val(this.value || "");
      this.$el.attr("placeholder", this.nodeOptions.placeholder || "");
    },

    _onInput: function (event) {
      // Get only numeric characters
      var rawValue = event.target.value;
      var digits = rawValue.replace(/[^0-9]/g, "");

      // Apply the mask
      var formatted = this._applyMask(digits);

      // Update the field
      this.$el.val(formatted);
      this._setValue(formatted);
    },

    _applyMask: function (digits) {
      if (!this.mask) return digits;

      var result = "";
      var digitPos = 0;

      for (var i = 0; i < this.mask.length && digitPos < digits.length; i++) {
        if (this.mask[i] === "9") {
          result += digits[digitPos] || "";
          digitPos++;
        } else {
          result += this.mask[i];
        }
      }

      return result;
    },
  });

  fieldRegistry.add("ph_mask", IdMaskWidget);
  return IdMaskWidget;
});
