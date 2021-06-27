let image1;
let image2;
showPopup();

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
            try {
                if (e.target.files[0].size > 20 * 1024 * 1024) {
                    throw new RangeError("ファイルサイズが大きすぎます。20MB以下の画像を使用してください。");
                }
                previewImg(e, previewSpace);
                if (previewSpace == document.getElementById("new_img_wrapper_1")) {
                    imgLabel1.classList.add("hidden_class");
                    imgLabel2.classList.remove("hidden_class");
                } else {
                    imgLabel1.classList.remove("hidden_class");
                    imgLabel2.classList.add("hidden_class");
                }
            } catch (e) {
                window.alert(e.message);
            }
        }
    })
};

function previewImg(e, previewSpace) {
    const fileReader = new FileReader();
    fileReader.addEventListener('load', {
        previewSpace: previewSpace,
        handleEvent: createPopup,
    });
    document.getElementById("id_content").classList.add("add_preview_space");
    document.getElementById("preview").classList.add("preview_space");
    const imageIcon = document.getElementsByClassName("article_image_icon");
    Array.prototype.forEach.call(imageIcon, function (icon) {
        icon.classList.add("icon_with_preview");
    });
    fileReader.readAsDataURL(e.target.files[0]);
    addDeleteBtn(previewSpace);
};

// プレビュー設置、ポップアップ表示を用意
function createPopup(e) {
    const newImg = e.currentTarget.result;
    if (this.previewSpace == previewSpaceFor2) {
        this.previewSpace.insertAdjacentHTML("beforeend", "<label>"
            + "<img src=" + newImg + ">"
            + "<input type='checkbox' id='show_popup_2'>"
            + "<div id='popup_2'>"
            + "<input type='image' src='" + toNextIconSource + "' id='to_next_img_2'>"
            + "<img src=" + newImg + ">"
            + "<input type='image' src='" + toPrevIconSource + "' id='to_prev_img_2'>"
            + "</div>"
        );

    } else {
        this.previewSpace.insertAdjacentHTML("beforeend", "<label>"
            + "<img src=" + newImg + ">"
            + "<input type='checkbox' id='show_popup_1'>"
            + "<div id='popup_1'>"
            + "<input type='image' src='" + toNextIconSource + "' id='to_next_img_1'>"
            + "<img src=" + newImg + ">"
            + "<input type='image' src='" + toPrevIconSource + "' id='to_prev_img_1'>"
            + "</div>");
    }
    showPopup();
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

        // プレビュー画像がなくなったらプレビュー用スペースを削除、合わせて画像選択アイコンを上に移動
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

        // 保存済み画像の削除と追加は同時にできないので、画像選択アイコンを削除
        if (deleteBtn == deleteBtn1) {
            imgLabel1.classList.add("hidden_class");
        } else {
            imgLabel2.classList.add("hidden_class");
        }

    });
};

// 画像ポップアップ表示
function showPopup() {
    const showFirstPopup = document.getElementById("show_popup_1");
    const showSecondPopup = document.getElementById("show_popup_2");


    for (let i = 1; i < 3; i++) {
        const idNext = "to_next_img_" + i;
        const idPrev = "to_prev_img_" + i;
        if ((toNextImg = document.getElementById(idNext))) {
            toNextImg.addEventListener('click', function (e) {
                e.preventDefault();
                showFirstPopup.checked = false;
                showSecondPopup.checked = true;
            })
        };
        if ((toPrevImg = document.getElementById(idPrev))) {
            toPrevImg.addEventListener('click', function (e) {
                e.preventDefault();
                showFirstPopup.checked = true;
                showSecondPopup.checked = false;
            })
        };
    }
};
