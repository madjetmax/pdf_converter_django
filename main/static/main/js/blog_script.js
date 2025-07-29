function showMoreText(el) {
    let full_text = el.dataset.fullText;
    let text_wrap = el.parentNode.querySelector(".text");

    if (full_text == "true") {
        // change button
        el.innerText = "Prikaži več";
        el.dataset.fullText = "false";

        // change text wrapper
        text_wrap.classList.remove("full");        
    }   
    else {
        // change buttom
        el.innerText = "Prikaži manj"
        el.dataset.fullText = "true";

        // change text wrapper
        text_wrap.classList.add("full");
    } 
}