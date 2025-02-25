const eventSource = new EventSource('/sse/user');

eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.event === "update") {
        updatePositionZoom(data);
    }
}

function updatePositionZoom(data) {
    const largeImageContainer = document.getElementById("largeImageContainer");
    if (largeImageContainer) {
        // Leere den Container
        largeImageContainer.innerHTML = '';

        // Überprüfe, ob das Projekt "geschlossen" ist oder kein Projekt offen ist
        if (!data.open_project || data.open_project.name === 'geschlossen') {
            // Erstelle den Warte-Text
            const waitingText = document.createElement('div');
            waitingText.id = 'waitingText';
            waitingText.className = 'waiting-text';
            waitingText.textContent = 'Bitte warten Sie, bis der Admin ein Projekt geöffnet hat.';

            // Füge den Warte-Text in den Container ein
            largeImageContainer.appendChild(waitingText);
        } else {
            // Erstelle das große Bild-Element
            const largeImage = document.createElement('img');
            largeImage.id = 'largeImage';
            largeImage.src = data.largeImageSrc; // Stellen Sie sicher, dass der Pfad korrekt ist
            largeImage.alt = 'Großes Bild';
            largeImage.style.display = data.largeImageSrc ? 'block' : 'none';
            largeImage.style.transform = `scale(${1})`;
            largeImage.style.left = '0px';
            largeImage.style.top = '0px';
            largeImage.dataset.imageId = data.largeImageId; // Speichere die image_id im Dataset

            // Erstelle den Platzhalter-Text
            const placeholderText = document.createElement('div');
            placeholderText.id = 'placeholderText';
            placeholderText.className = 'placeholder-text';
            placeholderText.textContent = data.largeImageSrc ? '' : 'Nichts ausgewählt';

            // Füge die Elemente in den Container ein
            largeImageContainer.appendChild(largeImage);
            largeImageContainer.appendChild(placeholderText);

            // Initialisiere die Bildmanipulation
            if (data.open_project.sync) {
                largeImage.style.left = data.position.left;
                largeImage.style.top = data.position.top;
                largeImage.style.transform = `scale(${data.zoom})`;
            } else {
                initImageManipulation();
            }
        }
    }
}

setInterval(() => {
    fetch('/update_user_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'user_id': document.getElementById('userId').value // Verwende das versteckte Eingabefeld
        })
    });
}, 2000);

function initImageManipulation() {
    const largeImage = document.getElementById("largeImage");
    const container = document.getElementById("largeImageContainer");
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;
    let lastUpdateTime = 0;

    if (largeImage && container) {
        largeImage.addEventListener("mousedown", function (e) {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = parseInt(largeImage.style.left || 0, 10);
            initialTop = parseInt(largeImage.style.top || 0, 10);
            largeImage.style.cursor = "grabbing";
        });

        document.addEventListener("mousemove", function (e) {
            if (isDragging) {
                const dx = e.clientX - startX;
                const dy = e.clientY - startY;
                largeImage.style.left = initialLeft + dx + "px";
                largeImage.style.top = initialTop + dy + "px";
            }
        });

        document.addEventListener("mouseup", function () {
            isDragging = false;
            largeImage.style.cursor = "grab";
        });

        container.addEventListener("wheel", function (e) {
            e.preventDefault();
            let scale = parseFloat(largeImage.style.transform.replace("scale(", "").replace(")", "")) || 1;
            scale += e.deltaY * -0.002;
            scale = Math.min(Math.max(0.5, scale), 3);
            largeImage.style.transform = "scale(" + scale + ")";
        });
    }
}

