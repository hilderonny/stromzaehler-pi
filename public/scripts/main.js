setInterval(() => {
    document.querySelector("img").setAttribute("src", "api/image?" + Date.now())
}, 100)