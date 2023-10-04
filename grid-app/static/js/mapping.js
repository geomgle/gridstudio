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
        // check if the terminal tab is not the current tab
        let terminalTab = document.querySelector(
          'div.tab[data-tab="terminal"]',
        );
        if (!terminalTab.classList.contains("current")) {
          // click the terminal tab
          terminalTab.click();
        }
        // find the terminal textarea and focus it
        let terminalTextarea = document.querySelector(
          "textarea.xterm-helper-textarea",
        );
        if (terminalTextarea) {
          terminalTextarea.focus();
        }
        break;
      default:
        break;
    }
  }
});
