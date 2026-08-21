// your_module_name/static/src/js/button_animation.js

(function () {
  "use strict";

  // Wait for the DOM to be fully loaded
  document.addEventListener("DOMContentLoaded", function () {
    // Find all buttons with your custom class
    const buttons = document.querySelectorAll(".my_print_button");

    buttons.forEach(function (button) {
      button.addEventListener("mouseenter", function (e) {
        this.style.transition = "transform 0.3s ease-in-out";
        this.style.transform = "scale(1.3)";
        this.style.color = "#FF5733";
      });

      button.addEventListener("mouseleave", function (e) {
        this.style.transition = "transform 0.3s ease-in-out";
        this.style.transform = "scale(1)";
        this.style.color = "";
      });

      button.addEventListener("click", function (e) {
        this.style.transition = "transform 0.1s ease";
        this.style.transform = "scale(0.8)";

        setTimeout(() => {
          this.style.transition = "transform 0.2s ease-out";
          this.style.transform = "scale(1.1)";
        }, 100);

        setTimeout(() => {
          this.style.transition = "transform 0.2s ease-in-out";
          this.style.transform = "scale(1)";
        }, 300);
      });

      console.log("Animation attached to button:", button);
    });
  });
})();
