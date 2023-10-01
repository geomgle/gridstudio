document.addEventListener("keydown", function (event) {
  if (event.ctrlKey) {
    switch (event.keyCode) {
      case 49: // Ctrl + 1
        event.preventDefault(); // prevent browser default action
        document.querySelector("div-sheet").focus();
        break;
      case 50: // Ctrl + 2
        event.preventDefault(); // prevent browser default action
        document.querySelector(".ace_text-input").focus();
        break;
      case 51: // Ctrl + 3
        event.preventDefault(); // prevent browser default action
        document.querySelector("textarea.xterm-helper-textarea").focus();
        break;
      default:
        break;
    }
  }
});
