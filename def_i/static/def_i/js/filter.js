const categorySelect = document.getElementById("id_category");
const courseSelect = document.getElementById("id_course");
const lessonSelect = document.getElementById("id_lesson");

function filterCourse() {
    while (courseSelect.lastChild) {
        courseSelect.removeChild(courseSelect.lastChild);
    }
    const categoryId = categorySelect.value;
    const newCourseSelect = courses[categoryId];
    console.log('newCourseSelect:' + newCourseSelect);

    for (const course of newCourseSelect) {
        const option = document.createElement("option");
        option.text = course.title;
        option.value = course.pk;
        courseSelect.appendChild(option);
        console.log('8');
    }
    console.log('10');
};

function filterLesson() {
    while (lessonSelect.lastChild) {
        lessonSelect.removeChild(lessonSelect.lastChild);
    }
    const courseId = courseSelect.value;
    const newlessonSelect = lessons[courseId];
    console.log('newlessonSelect:' + newlessonSelect);

    for (const lesson of newlessonSelect) {
        const option = document.createElement("option");
        option.text = lesson.title;
        option.value = lesson.pk;
        lessonSelect.appendChild(option);
    }
};

document.getElementById("id_category").onchange = function () {
    filterCourse();
};

document.getElementById("id_course").onchange = function () {
    filterLesson();
}
