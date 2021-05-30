let image1;
let image2;

if (document.getElementById("id_article_image_1")) {
    image1 = document.getElementById("id_article_image_1");
    image2 = document.getElementById("id_article_image_2");
    clearBtn1 = document.getElementById("article_image_1-clear_id");
    clearBtn2 = document.getElementById("article_image_2-clear_id");
} else {
    image1 = document.getElementById("id_question_image_1");
    image2 = document.getElementById("id_question_image_2");
    clearBtn1 = document.getElementById("question_image_1-clear_id");
    clearBtn2 = document.getElementById("question_image_2-clear_id");
}

const previewSpaceFor1 = document.getElementById("new_img_wrapper_1");
const previewSpaceFor2 = document.getElementById("new_img_wrapper_2");

const imgLabel1 = document.getElementById("label_image_1");
const imgLabel2 = document.getElementById("label_image_2");

handleImage(image1, previewSpaceFor1);
handleImage(image2, previewSpaceFor2);

function handleImage(image, previewSpace) {
    image.addEventListener("change", function (e) {
        if (previewSpaceFor1.hasChildNodes() && previewSpaceFor2.hasChildNodes()) {
            window.alert("添付できる画像は2枚までです。");
        } else {
            previewImg(e, previewSpace);
            imgLabel1.classList.toggle("hidden_class");
            imgLabel2.classList.toggle("hidden_class");
        }
    })
};

function previewImg(e, previewSpace) {
    const fileReader = new FileReader();
    fileReader.addEventListener('load', function (e) {
        const newImg = document.createElement('img');
        newImg.src = e.target.result;
        previewSpace.appendChild(newImg);
    });
    document.getElementById("id_content").classList.add("add_preview_space");
    document.getElementById("preview").classList.add("preview_space");
    const imageIcon = document.getElementsByClassName("article_image_icon");
    Array.prototype.forEach.call(imageIcon, function (icon) {
        icon.classList.add("icon_with_preview");
    });
    console.log('added');
    fileReader.readAsDataURL(e.target.files[0]);
    addDeleteBtn(previewSpace);
};

// プレビュー用削除ボタン
function addDeleteBtn(previewSpace) {
    const btn = document.createElement('button');
    btn.setAttribute("class", "img_delete_btn");
    btn.innerText = "削除する";
    previewSpace.appendChild(btn);

    btn.addEventListener('click', function () {
        previewSpace.firstElementChild.value = "";
        while (previewSpace.lastChild) {
            previewSpace.removeChild(previewSpace.lastChild);
        }
        if (previewSpace == document.getElementById("new_img_wrapper_1")) {
            imgLabel1.classList.remove("hidden_class");
            imgLabel2.classList.add("hidden_class");
        } else {
            imgLabel2.classList.remove("hidden_class");
            imgLabel1.classList.add("hidden_class");
        }

        if (!previewSpaceFor1.hasChildNodes() && !previewSpaceFor2.hasChildNodes()) {
            document.getElementById("id_content").classList.remove("add_preview_space");
            document.getElementById("preview").classList.remove("preview_space");
            const imageIcon = document.getElementsByClassName("article_image_icon");
            Array.prototype.forEach.call(imageIcon, function (icon) {
                icon.classList.remove("icon_with_preview");
            });
        }
    });
};

// 編集ページ用削除ボタン
const deleteBtn1 = document.getElementById("delete_image_1");
const deleteBtn2 = document.getElementById("delete_image_2");

if (deleteBtn1) {
    deleteSavedImg(deleteBtn1, clearBtn1);
}
if (deleteBtn2) {
    deleteSavedImg(deleteBtn2, clearBtn2);
}

function deleteSavedImg(deleteBtn, clearBtn) {
    deleteBtn.addEventListener('click', function () {
        clearBtn.checked = true;
        const wrapper = deleteBtn.parentNode;

        while (wrapper.lastChild) {
            wrapper.removeChild(wrapper.lastChild);
        }

        // previewSpaceを作り直す
        if (deleteBtn == deleteBtn1) {
            imgLabel1.classList.add("hidden_class");
        } else {
            imgLabel2.classList.add("hidden_class");
        }

    });
};
