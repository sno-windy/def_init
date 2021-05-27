let firstImg;
let secondImg;

if (document.getElementById("id_article_image_1")) {
     firstImg = document.getElementById("id_article_image_1");
     secondImg = document.getElementById("id_article_image_2");
} else {
     firstImg = document.getElementById("id_question_image_1");
     secondImg = document.getElementById("id_question_image_2");
}
const imgs = [firstImg, secondImg];
const previewSpace = document.getElementById("preview");

for (let img of imgs) {
    img.addEventListener('change', function (e) {
        if (previewSpace.childElementCount == 2) {
            window.alert("添付できる画像は2枚までです。");
        } else {
            const newImgWrapper = previewImg(e);
            document.getElementById("label_image_1").classList.toggle("hidden_class");
            document.getElementById("label_image_2").classList.toggle("hidden_class");
            addDeleteBtn(newImgWrapper);
        }
    });
}

function previewImg (e){
    const fileReader = new FileReader();
    const newImgWrapper = document.createElement('div');
    newImgWrapper.setAttribute("class", "new_img_wrapper");
    fileReader.addEventListener('load', function (e) {
        const newImg = document.createElement('img');
        newImg.src = e.target.result;

        newImgWrapper.appendChild(newImg);
        previewSpace.appendChild(newImgWrapper);
    });
    fileReader.readAsDataURL(e.target.files[0]);
    return newImgWrapper;
};

function addDeleteBtn(newImgWrapper) {
    const btn = document.createElement('button');
    btn.setAttribute("class", "img_delete_btn");
    btn.innerText = "削除する";
    btn.addEventListener('click', function () {
        newImgWrapper.firstElementChild.value = '';
        while (newImgWrapper.lastChild) {
            newImgWrapper.removeChild(newImgWrapper.lastChild);
        }
        newImgWrapper.remove();
    });
    newImgWrapper.appendChild(btn);
};
