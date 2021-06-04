function getCookie(key) {
    if (document.cookie && document.cookie !== "") {
        for (const cookie of document.cookie.split(";")) {
            const [k, v] = cookie.trim().split("=");
            if (k === key) {
                return decodeURIComponent(v);
            }
        }
    }
    return null;
}
