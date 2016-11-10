var iframe = null;
var iframeDocument = null;

var frameContent = null;


var modal = document.getElementById('previewModal');
var btn = document.getElementById("previewButton");
var span = document.querySelector('#previewClose');
var previewBody = document.querySelector("#previewBody");


btn.onclick = function() {
    frameContent = iframeDocument.body.innerHTML;
    previewBody.innerHTML = frameContent;
    modal.style.display = "block";
}
span.onclick = function() {
    modal.style.display = "none";
}
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

$(document).ready(function(){
    
    tinymce.init({ 
        selector:'#typeText',
        browser_spellcheck: true,
        height: 325,
        max_width: 1000,
        statusbar: false,
        plugins: [
            'image charmap preview searchreplace code fullscreen media table paste spellchecker' 
        ]
    });
    setTimeout(loadIFrame, 1000);
});

function loadIFrame(){
    iframe = document.getElementById("typeText_ifr");
    iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
}

function putIntoString(){
    frameContent = iframeDocument.body.innerHTML;
}