var target = document.getElemntByTagName("body");
var p = document.createElement("p");
var text = p.createTextNode("XSS was here.");
target.appendChild(text);
