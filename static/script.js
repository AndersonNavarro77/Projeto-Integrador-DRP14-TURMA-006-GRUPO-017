document.addEventListener("DOMContentLoaded", function() {
    var windowHeight = window.innerHeight;
    var headerHeight = document.querySelector("h1").offsetHeight;
    var marginTop = (windowHeight / 2) - (headerHeight + 50); // 50px extra padding

    document.querySelector("h1").style.marginTop = marginTop + "px";
});
