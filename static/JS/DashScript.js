var element = document.querySelector("#itemCount");
var messageBox = document.querySelector("#emptyMessage");
var imageBtn = document.querySelector("#inputActivator");
var input = document.querySelector("#imageInput");
var modal_1 = $("#createModal");
var btn_1 = document.getElementById("createBtn");
var span_1 = document.getElementById("createClose");
var logoutBtn = document.querySelector("#emptyButton");
var displayModal = $("#displayModal");
var closeModal = document.querySelector("#displayClose");
var submitBucket = document.querySelector("#submitBucket");
var hiddenTags = document.querySelector('#hiddenTags');
var container = $("#container");

var name = null;
var imageSrc = null;
var tags = null;
var dateReq = null;

if (parseInt(element.innerHTML) === 0) {
    messageBox.style.display = "block";
}
if (submitBucket.innerHTML.trim() !== ""){
    editBucket(false);
    modal_1.fadeIn();
}

$(document).ready(function () {
    setTimeout(setPadding, 501);
});
$(window).resize(function () {
    setTimeout(setPadding, 501);
});


function setPadding() {
    var padding = $("nav.w3-navbar").outerHeight(true);
    container.css("padding-top", padding + "px");
    $('.matchheight').matchHeight();
}

btn_1.onclick = function () {
    editBucket(false);
    modal_1.fadeIn();
}
span_1.onclick = function () {
    modal_1.fadeOut();
}
closeModal.onclick = function () {
    console.log("Function Called");
    displayModal.fadeOut();
}
window.onclick = function (event) {
    if (event.target.id === "createModal")
        modal_1.fadeOut();
    else if (event.target.id === "displayModal")
        displayModal.fadeOut();
}



function openCreate() {
    document.querySelector("#createBtn").click();
}
function displayName(files) {
    imageBtn.innerHTML = files[0].name;
}
function inputClick() {
    input.click();
}
function invisibleClick() {
    logoutBtn.click();
}

function displayAll(event) {
    var child = null;
    if (event.target.tagName === "DIV")
        child = event.target.childNodes;
    else
        child = event.target.parentNode.childNodes;

    name = child[2].data.trim();
    imageSrc = child[1].src;
    dateReq = child[3].innerHTML.trim();
    tags = child[5].innerHTML.trim();
    var dateDiff = child[7].innerHTML.trim();

    var image = document.querySelector("#displayModal > form > div > div > img");
    image.src = imageSrc;
    document.querySelector("#Name").innerHTML = name;
    document.querySelector("#Date").innerHTML = dateReq;
    var result = null;
    if (parseInt(dateDiff) > 0)
        result = dateDiff + " day(s) till exipry.";
    else if (parseInt(dateDiff) < 0)
        result = "Expired " + Math.abs(dateDiff) + " days ago.";
    else
        result = "Expires Today.";

    document.querySelector("#DateDiff").innerHTML = result;
    displayModal.fadeIn();
}

function submitForm() {
    var submit = true;
    var bucketName = document.querySelector("#bucketName").value.trim();
    var tagsName = hiddenTags.value.trim();
    var bucketDate = document.querySelector("#bucketDate").value.trim();
    var bucketImage = imageBtn.innerHTML.trim();
    if (bucketName === "" || tagsName === "" || bucketDate === "" || bucketImage === "Click here to select image...")
        submit = false;
    if (submit)
        document.querySelector("#bucketForm").submit();
    else
        submitBucket.innerHTML = "Please fill all the fields...";
}

function editBucket(value) {
    if (value) {
        document.querySelector("#submitBUtton").innerHTML = "Save Bucket";
        document.querySelector("#bucketName").value = name;
        document.getElementsByName('update')[0].value = "1";
        document.getElementsByName('oldValue')[0].value = name;

        var imageName = imageSrc.split('/');
        document.querySelector("#bucketImage").innerHTML = imageName[4];
        document.querySelector("#bucketImage").removeAttribute("onclick");
        document.querySelector("#bucketImage").className = "w3-btn w3-ripple w3-round w3-hover-red w3-orange w3-disabled";

        document.querySelector("#imageInput").removeAttribute("required");

        
        var tagsArray = tags.replace(/ u'/g, '');
        tagsArray = tagsArray.replace(/'/g, '');
        tagsArray = tagsArray.replace(/u/i, '');
        tagsArray = tagsArray.replace(/]/i, '');
        tagsArray = tagsArray.replace(/\[/i, '');
        tagsArray = tagsArray.split(',');
        var resultString = "";
        for (var i = 0; i < tagsArray.length; i++) {
            $("#tags").addTag(tagsArray[i]);
            resultString += tagsArray[i];
            if (i !== tags.length - 1)
                resultString += "    ;";
        }

        document.querySelector("#bucketDate").value = dateReq;
        modal_1.fadeIn();
    }
    else{
        document.querySelector("#submitBUtton").innerHTML = "Add Bucket";
        document.querySelector("#bucketName").value = "";
        document.querySelector("#bucketDate").value = "";
        document.querySelector("#bucketImage").innerHTML = "Click here to select image...";
        document.querySelector("#bucketImage").setAttribute("onclick", "inputClick()");
        document.querySelector("#bucketImage").className = "w3-btn w3-ripple w3-round w3-hover-red w3-orange";
        document.querySelector("#imageInput").setAttribute("required", "required");
        document.getElementsByName('update')[0].value = "0";

        $("#tags").importTags('');
    }

}

$(function () {
    $("#tags_tag").keydown(function (e) {
        if (e.keyCode == 13 || e.keyCode == 8)
            setTimeout(addToInput, 100);
    });
});

function addToInput() {
    var tags = document.querySelectorAll("span.tag > span");
    var resultString = "";
    for (var i = 0; i < tags.length; i++) {
        resultString += tags[i].childNodes[0].data;
        if (i !== tags.length - 1)
            resultString += "    ;";
    }
    hiddenTags.value = resultString;
}
