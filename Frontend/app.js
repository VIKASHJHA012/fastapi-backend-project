
const API_BASE = "https://fastapi-backend-project-w81e.onrender.com";

// Keep the token across page refreshes in this tab.
let accessToken = sessionStorage.getItem("accessToken");

function showMessage(container, message) {
    container.textContent = message;
}

async function readResponse(response) {
    const text = await response.text();

    let data = {};
    if (text) {
        try {
            data = JSON.parse(text);
        } catch {
            data = { detail: text };
        }
    }

    if (!response.ok) {
        if (response.status === 401) {
            accessToken = null;
            sessionStorage.removeItem("accessToken");
            throw new Error("Session expired or authentication failed. Please log in again.");
        }

        const detail = data.detail;
        const message = Array.isArray(detail)
            ? detail.map(item => item.msg).join(", ")
            : detail;

        throw new Error(message || `Request failed: ${response.status}`);
    }

    return data;
}

function authHeaders(json = false) {
    const headers = {};

    if (accessToken) {
        headers.Authorization = `Bearer ${accessToken}`;
    }

    if (json) {
        headers["Content-Type"] = "application/json";
    }

    return headers;
}

function showError(container, error) {
    console.error(error);

    showMessage(
        container,
        error.message === "Failed to fetch"
            ? "Could not connect to the backend. Check your connection."
            : error.message
    );
}


// -------------------- Registration --------------------

const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const user = {
        name: document.getElementById("register-name").value.trim(),
        email: document.getElementById("register-email").value.trim(),
        password: document.getElementById("register-password").value
    };

    showMessage(registerMessage, "Registering...");

    try {
        const response = await fetch(
            `${API_BASE}/api-registeration-v1/register`,
            {
                method: "POST",
                headers: authHeaders(true),
                body: JSON.stringify(user)
            }
        );

        await readResponse(response);

        showMessage(
            registerMessage,
            "Registration successful! You can now log in."
        );
        registerForm.reset();
    } catch (error) {
        showError(registerMessage, error);
    }
});


// -------------------- Login --------------------

const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    showMessage(loginMessage, "Logging in...");

    try {
        const response = await fetch(
            `${API_BASE}/api-registeration-v1/login`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            }
        );

        const data = await readResponse(response);

        if (!data.access_token) {
            throw new Error("Login response did not contain an access token.");
        }

        accessToken = data.access_token;
        sessionStorage.setItem("accessToken", accessToken);

        showMessage(loginMessage, "Login successful!");
        loginForm.reset();
    } catch (error) {
        showError(loginMessage, error);
    }
});


// -------------------- Create Post --------------------

const userPost = document.getElementById("user-post");
const postCreate = document.getElementById("post-create");
const createPostContainer = document.getElementById("create-post-container");

postCreate.addEventListener("click", async function () {
    const title = userPost.value.trim();

    if (!title) {
        showMessage(createPostContainer, "Please enter a title for the post.");
        return;
    }

    if (!accessToken) {
        showMessage(createPostContainer, "Please log in before creating a post.");
        return;
    }

    showMessage(createPostContainer, "Creating post...");

    try {
        const response = await fetch(`${API_BASE}/api-post-v1/Post`, {
            method: "POST",
            headers: authHeaders(true),
            body: JSON.stringify({ title })
        });

        const data = await readResponse(response);

        createPostContainer.replaceChildren();

        const message = document.createElement("p");
        message.textContent = "Post created successfully!";

        const card = document.createElement("div");
        card.className = "post-card";

        const titleElement = document.createElement("h3");
        titleElement.textContent = data.title;

        const details = document.createElement("p");
        details.textContent = `Post ID: ${data.id} | User ID: ${data.user_id}`;

        // Use titleElement, not the input variable "title".
        card.append(titleElement, details);
        createPostContainer.append(message, card);

        userPost.value = "";
    } catch (error) {
        showError(createPostContainer, error);
    }
});


// -------------------- Delete Post --------------------

const postIdInput = document.getElementById("delete-post");
const postDelete = document.getElementById("post-delete");
const deleteContainer = document.getElementById("delete-post-container");

postDelete.addEventListener("click", async function () {
    const id = postIdInput.value.trim();

    if (!id || !/^\d+$/.test(id) || Number(id) < 1) {
        showMessage(deleteContainer, "Please enter a valid post ID.");
        return;
    }

    if (!accessToken) {
        showMessage(deleteContainer, "Please log in before deleting a post.");
        return;
    }

    showMessage(deleteContainer, "Deleting post...");

    try {
        const response = await fetch(
            `${API_BASE}/api-post-v1/Post/${encodeURIComponent(id)}`,
            {
                method: "DELETE",
                headers: authHeaders()
            }
        );

        await readResponse(response);

        showMessage(deleteContainer, "Post deleted successfully.");
        postIdInput.value = "";
    } catch (error) {
        showError(deleteContainer, error);
    }
});


// -------------------- Update User --------------------

const userIdInput = document.getElementById("user-id");
const userNameInput = document.getElementById("user-name");
const userEmailInput = document.getElementById("user-email");
const userUpdate = document.getElementById("update-user");
const userUpdateContainer = document.getElementById("update-user-container");

userUpdate.addEventListener("click", async function () {
    const userId = userIdInput.value.trim();
    const userName = userNameInput.value.trim();
    const userEmail = userEmailInput.value.trim();

    if (!userId || !/^\d+$/.test(userId) || Number(userId) < 1) {
        showMessage(userUpdateContainer, "Please enter a valid user ID.");
        return;
    }

    if (!accessToken) {
        showMessage(userUpdateContainer, "Please log in before updating a user.");
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE}/api-version-v1/users/${encodeURIComponent(userId)}`,
            {
                method: "PATCH",
                headers: authHeaders(true),
                body: JSON.stringify({
                    name: userName,
                    email: userEmail
                })
            }
        );

        const data = await readResponse(response);

        userUpdateContainer.replaceChildren();

        const card = document.createElement("div");
        card.className = "post-card";

        const heading = document.createElement("h3");
        heading.textContent = "User updated successfully!";

        const details = document.createElement("p");
        details.textContent = `User ID: ${data.id}`;

        const name = document.createElement("p");
        name.textContent = `Name: ${data.name}`;

        const email = document.createElement("p");
        email.textContent = `Email: ${data.email}`;

        card.append(heading, details, name, email);
        userUpdateContainer.append(card);
    } catch (error) {
        showError(userUpdateContainer, error);
    }
});


// -------------------- Load Posts --------------------

const loadButton = document.getElementById("load-posts");
const postContainer = document.getElementById("post-container");
const emailInput = document.getElementById("load-user-email");

loadButton.addEventListener("click", async function () {
    const email = emailInput.value.trim();

    if (!email) {
        showMessage(postContainer, "Please enter an email address.");
        return;
    }

    loadButton.disabled = true;
    loadButton.textContent = "Loading...";

    showMessage(postContainer, "Loading posts...");

    try {
        const response = await fetch(
            `${API_BASE}/api-post-v1/Post/User/${encodeURIComponent(email)}`
        );

        const data = await readResponse(response);

        postContainer.replaceChildren();

        if (!Array.isArray(data) || data.length === 0) {
            showMessage(postContainer, "No posts found for this user.");
            return;
        }

        data.forEach(function (post) {
            const card = document.createElement("div");
            card.className = "post-card";

            const title = document.createElement("h3");
            title.textContent = post.title;

            const details = document.createElement("p");
            details.textContent = `Post ID: ${post.id} | User ID: ${post.user_id}`;

            card.append(title, details);
            postContainer.append(card);
        });
    } catch (error) {
        showError(postContainer, error);
    } finally {
        loadButton.disabled = false;
        loadButton.textContent = "Load Posts";
    }
});
