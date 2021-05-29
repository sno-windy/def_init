const categorySelect = document.getElementById("id_category");
const courseSelect = document.getElementById("id_course");
const lessonSelect = document.getElementById("id_lesson");
if (!courseSelect.value) {
    courseSelect.setAttribute("disabled", true);
}
if (!lessonSelect.value) {
    lessonSelect.setAttribute("disabled", true);
}

function filterCourse() {
    while (courseSelect.lastChild) {
        courseSelect.removeChild(courseSelect.lastChild);
    }
    const categoryId = categorySelect.value;
    const newCourseSelect = courses[categoryId];

    for (const course of newCourseSelect) {
        const option = document.createElement("option");
        option.text = course.title;
        option.value = course.pk;
        courseSelect.appendChild(option);
    }
    courseSelect.removeAttribute('disabled');
};

function filterLesson() {
    while (lessonSelect.lastChild) {
        lessonSelect.removeChild(lessonSelect.lastChild);
    }
    const courseId = courseSelect.value;
    const newlessonSelect = lessons[courseId];

    for (const lesson of newlessonSelect) {
        const option = document.createElement("option");
        option.text = lesson.title;
        option.value = lesson.pk;
        lessonSelect.appendChild(option);
    }
    lessonSelect.removeAttribute('disabled');
};

categorySelect.onchange = function () {
    filterCourse();
    filterLesson();
};

courseSelect.onchange = function () {
    filterLesson();
}
