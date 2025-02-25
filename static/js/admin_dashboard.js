const eventSource = new EventSource("/sse/admin");

eventSource.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.event === "aktuelles_project_update") {
        updateAktProject(data);
    } else if (data.event === "user_update") {
        updateUserList(data);
    } else if (data.event === "project_update") {
        updateProjectManagement(data);
    } else if (data.event === "card_update") {
        updateCardManagement(data);
    } else if (data.event === "largeimageContainer_update") {
        updateLargeImageContainer(data);
    }
}

function updateUserList(data) {
    // Aktualisiere die Benutzerliste
    const userList = document.getElementById("userList");
    let userRows = ''
    if (userList) {
        userRows = `
            <h3>Registrierte Benutzer:</h3>
            <table border="1">
                <tr>
                    <th>Name</th>
                    <th>Status</th>
                    <th>Aktionen</th>
                </tr>
        `;
        data.users.forEach(user => {
            userRows += `
                <tr data-username="${user.username}">
                    <td>${user.username}</td>
                    <td class="status">${user.is_online ? "🟢 Online" : "🔴 Offline"}</td>
                    <td>
                        <form method="POST" action="/delete_user/${user.id}">
                            <button type="submit">Löschen</button>
                        </form>
                    </td>
                </tr>
            `;
        });
        userRows += `</table>`;
    }
    userList.innerHTML = userRows;
}

function updateAktProject(data) {
    // Aktualisiere das aktuelle Projekt
    const aktuellesProject = document.getElementById("aktuelles_project");
    if (aktuellesProject) {
        if (data.open_project) {
            aktuellesProject.innerHTML = `<p>Aktuell geöffnetes Projekt: ${data.open_project.name}</p>`;
        } else {
            aktuellesProject.innerHTML = `<p>Kein Projekt ist aktuell geöffnet.</p>`;
        }
    }
}



function updateProjectManagement(data) {
    const projectManagement = document.getElementById('projectManagement');
    let projectManagementContent = ''
    if (projectManagement) {
        projectManagementContent = `
            <h3>Projekt erstellen:</h3>
            <form id="createProjectForm" onsubmit="createProject()">
                <input type="text" name="project_name" placeholder="Projektname" required>
                <button type="submit">Projekt erstellen</button>
            </form>
            
            <h3>Projekt öffnen:</h3>
            <form method="POST" action="/open_project">
                <select name="project_id">
                    ${data.projects.map(project => `<option value="${project.id}">${project.name}</option>`).join('')}
                </select>
                <button type="submit" name="open_project">Projekt öffnen</button>
            </form>

            <h3>Projekt löschen:</h3>
            <form method="POST" action="/delete_project">
                <select name="project_id">
                    ${data.projects.filter(project => project.name !== 'geschlossen').map(project => `<option value="${project.id}">${project.name}</option>`).join('')}
                </select>
                <button type="submit" name="delete_project">Projekt löschen</button>
            </form>
        `;
    }
    projectManagement.innerHTML = projectManagementContent;
}

function updateCardManagement(data) {
    const cardManagement = document.getElementById('cardManagement');
    let cardManagementContent;
    if (cardManagement) {
        cardManagementContent = `
            <h3>Bild hochladen:</h3>
            ${data.open_project && data.open_project.name !== 'geschlossen' ? `
            <form method="POST" action="/upload_image" enctype="multipart/form-data">
                <input type="hidden" name="project_id" value="${data.open_project.id}">
                <input type="file" name="file" accept=".jpg, .jpeg, .png, .svg" required>
                <button type="submit">Bild hochladen</button>
            </form>
            <h3>Hochgeladene Bilder:</h3>
            <div class="image-container">
                ${data.images.map(image => `
                    <div class="image-item">
                        <img src="data:image/${image.extension};base64,${image.data}" alt="${image.name}" data-id="${image.id}" onclick="selectImage(${image.id}, ${data.open_project.id})">
                        <form method="POST" action="/update_image_name">
                            <input type="hidden" name="image_id" value="${image.id}">
                            <input type="text" name="new_name" value="${image.name}">
                            <button type="submit">Speichern</button>
                        </form>
                        <form method="POST" action="/delete_image/${image.id}">
                            <button type="submit">Löschen</button>
                        </form>
                    </div>
                `).join('')}
            </div>
            ` : `
            <p>Im Projekt "geschlossen" können keine Bilder hochgeladen werden.</p>
            `}
        `;
    }
    cardManagement.innerHTML = cardManagementContent;

    // Füge das Attribut data-id zu den Bild-Elementen hinzu und setze den onclick-Handler
    document.querySelectorAll('.image-item img').forEach(function (img) {
        img.setAttribute('data-id', img.dataset.id);
        img.onclick = function () {
            const imageId = img.dataset.id;
            const projectId = document.querySelector('input[name="project_id"]').value;
            selectImage(imageId, projectId);
        };
    });
}

function updateLargeImageContainer(data) {
    const largeImageContainer = document.getElementById('largeImageContainer');
    if (largeImageContainer) {
        // Leere den Container
        largeImageContainer.innerHTML = '';

        // Überprüfe, ob das Projekt "geschlossen" ist
        if (data.open_project && data.open_project.name === 'geschlossen') {
            // Erstelle den Platzhalter-Text
            const placeholderText = document.createElement('div');
            placeholderText.id = 'placeholderText';
            placeholderText.className = 'placeholder-text';
            placeholderText.textContent = 'Projekt "geschlossen" - Keine Bilder verfügbar';

            // Füge den Platzhalter-Text in den Container ein
            largeImageContainer.appendChild(placeholderText);
        } else {
            // Erstelle das große Bild-Element
            const largeImage = document.createElement('img');
            largeImage.id = 'largeImage';
            largeImage.src = data.largeImageSrc || '';
            largeImage.alt = 'Großes Bild';
            largeImage.style.display = data.largeImageSrc ? 'block' : 'none';
            largeImage.style.transform = 'scale(1)';
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
            initImageManipulation();

            if (data.largeImageId) {
                const selectedImage = document.querySelector(`.image-item img[data-id="${data.largeImageId}"]`);
                if (selectedImage) {
                    selectedImage.classList.add('selected');
                }
            }
        }
    }
}

function initImageManipulation() {
    const largeImage = document.getElementById("largeImage");
    const container = document.getElementById("largeImageContainer");
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;

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
            updateImageDetails();
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
        updateImageDetails();
    });
}

async function updateImageDetails() {
    const currentTime = Date.now();
    console.log("Image left position:", largeImage.style.left);
    await new Promise(resolve => setTimeout(resolve, 100));
    fetch('/update_image_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image_id: largeImage.dataset.imageId,
            position: {
                left: largeImage.style.left,
                top: largeImage.style.top
            },
            zoom: largeImage.style.transform
        })
    });
}

function createProject() {
    const form = document.getElementById('createProjectForm');
    const formData = new FormData(form);

    fetch('/create_project', {
        method: 'POST',
        body: formData
    })
}

function toggleUserList() {
    const userList = document.getElementById("userList");
    if (userList) {
        if (userList.style.display === "none" || userList.style.display === "") {
            userList.style.display = "block";
        } else {
            userList.style.display = "none";
        }
    }
}

function toggleProjectManagement() {
    const projectManagement = document.getElementById("projectManagement");
    if (projectManagement) {
        if (projectManagement.style.display === "none" || projectManagement.style.display === "") {
            projectManagement.style.display = "block";
        } else {
            projectManagement.style.display = "none";
        }
    }
}

function toggleCardManagement() {
    const cardManagement = document.getElementById("cardManagement");
    if (cardManagement) {
        if (cardManagement.style.display === "none" || cardManagement.style.display === "") {
            cardManagement.style.display = "block";
        } else {
            cardManagement.style.display = "none";
        }
    }
}

eventSource.onerror = function () {
    console.error("SSE-Fehler. Verbindung wird geschlossen.");
    eventSource.close();
}

setInterval(() => {
    fetch('/update_admin_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
}, 2000);


function selectImage(imageId, projectId) {
    // Entferne die Hervorhebung von allen Bildern
    const images = document.querySelectorAll('.image-item img');
    images.forEach(function (img) {
        img.classList.remove('selected');
    });

    // Hebe das ausgewählte Bild hervor
    const selectedImage = document.querySelector(`.image-item img[data-id="${imageId}"]`);
    if (selectedImage) {
        selectedImage.classList.add('selected');
    }

    // Sende die Anfrage an den Server, um das ausgewählte Bild zu speichern
    fetch('/select_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            image_id: imageId,
            project_id: projectId
        })
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const largeImage = document.getElementById("largeImage");
    const placeholderText = document.getElementById("placeholderText");

    if (largeImage && largeImage.src) {
        largeImage.style.display = "block";
        if (placeholderText) {
            placeholderText.style.display = "none";
        }
    } else {
        if (largeImage) {
            largeImage.style.display = "none";
        }
        if (placeholderText) {
            placeholderText.style.display = "block";
        }
    }
});