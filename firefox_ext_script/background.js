browser.browserAction.onClicked.addListener((tab) => {
    // console.log(tab.url);
    document.body.style.border = "5px solid red";
    // document.getElementById("wordle-app-game").querySelectorAll('button[class^="Key-module_key"]')[0].click();
});