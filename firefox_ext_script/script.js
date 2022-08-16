// // var app_game = document.getElementById("wordle-app-game");

// alert("hello");

browser.browserAction.onClicked.addListener((tab) => {
    document.body.style.border = "5px solid red";
    // console.log(tab.url);
    // document.getElementById("wordle-app-game").querySelectorAll('button[class^="Key-module_key"]')[0].click();
});

// function myFunction() {
//     document.getElementById("wordle-app-game").querySelectorAll('button[class^="Key-module_key"]')[0].click();
// }

// document.getElementById("clickMe2").onclick = myFunction;

// document.addEventListener("click", (e) => 
// {

//     if (e.target.id === "run-solver")
//     {
//         getCurrentWindow().then((currentWindow) => document.getElementById("wordle-app-game").querySelectorAll('button[class^="Key-module_key"]')[0].click());
//     }

//     e.preventDefault();
// });