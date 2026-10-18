// registeration code
const registerForm = document.getElementById("register-form");
const registerMessage = document.getElementById("register-message");

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const user = {
        name: document.getElementById("register-name").value.trim(),
        email: document.getElementById("register-email").value.trim(),
        password: document.getElementById("register-password").value
    };


    registerMessage.textContent = "Registering...";

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api-registeration-v1/register",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(user)
            }
        );
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || "Registeration failed.");
        }
        registerMessage.textContent = " Registration successful! You can now log in.;"
    }
    catch (error) {
        console.error("Registration error:", error);
        registerMessage.textContent =
            error.message === "Failed to fetch"
                ? "Could not connect to the backend."
                : error.message;
    }
});


// login code
// Keep the access token in memory while the page is open
let accessToken = null;

const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;

    loginMessage.textContent = "Logging in...";

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api-registeration-v1/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email, password })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }

        accessToken = data.access_token;

        loginMessage.textContent = "Login successful!";
        loginForm.reset();

    } catch (error) {
        console.error("Login error:", error);
        loginMessage.textContent =
            error.message === "Failed to fetch"
                ? "Could not connect to the backend."
                : error.message;
    }
});




//####################### create post
const user_post = document.getElementById("user-post");
const post_create = document.getElementById("post-create");
const createPostContainer = document.getElementById("create-post-container");



post_create.addEventListener("click", async function () {
    const title = user_post.value.trim();
    if (!title) {
        createPostContainer.textContent = 'Please enter title for post.';
        return;
    }
    if(!accessToken){
        createPostContainer.textContent='Please log in before creating a post.';
        return;
    }
    const url = 'http://127.0.0.1:8000/api-post-v1/Post'
    try {
        createPostContainer.textContent = "Creating Post..."
        const response = await fetch(url,
            {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${accessToken}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ title: title })
            }
        );
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        const data = await response.json();

        createPostContainer.replaceChildren();

        // createPostContainer.textContent = JSON.stringify(data, n
        // ull, 2);
        const message = document.createElement("p");
        message.textContent = "Post created successfully!";

        const card = document.createElement("div");
        card.className = "post-card";

        const titleElement = document.createElement("h3");
        titleElement.textContent = data.title;

        const details = document.createElement("p");
        details.textContent = `Post ID: ${data.id} | User ID: ${data.user_id}`;

        card.append(title, details);
        createPostContainer.append(message, card);

        user_post.value = "";
    }
    catch (error) {
        console.error("Create Post error:", error);
        createPostContainer.textContent =
            error.message === "Failed to fetch"
                ? "Could not connect to the backend."
                : error.message;
    }
})








//  ################################ load posts code

const loadButton = document.getElementById("load-posts");

const postContainer = document.getElementById("post-container");

const emailInput = document.getElementById("user-email")

// loadButton.addEventListener("click",function(){
//     const email = emailInput.value;

// postContainer.textContent =`You entered:${email}`;
// })

loadButton.addEventListener("click", async function () {
    const email = emailInput.value.trim();
    if (!email) {
        postContainer.textContent = "Please enter an email address."
        return;
    }
    const url = `http://127.0.0.1:8000/api-post-v1/Post/User/${encodeURIComponent(email)}`;
    loadButton.disabled = true;
    loadButton.textContent = "Loading...";
    try {
        postContainer.textContent = "Loading posts..."
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        const data = await response.json();
        // postContainer.textContent = JSON.stringify(data,null,2)

        postContainer.replaceChildren();
        if (data.length == 0) {
            postContainer.textContent = "No posts found for the user";
            return;
        }
        data.forEach(function (post) {
            const card = document.createElement("div");
            card.className = "post-card";

            const title = document.createElement("h3");
            title.textContent = post.title;

            const details = document.createElement("p");
            details.textContent = `Post ID: ${post.id}| User Id : ${post.user_id}`
            card.append(title, details)
            postContainer.append(card)
        });
    }
    catch (error) {

        console.error("Failed to load posts:", error);

        if (error.message.startsWith("Request failed:")) {
            postContainer.textContent =
                `The server returned an error. ${error.message}`;
        } else {
            postContainer.textContent =
                "Could not connect to the backend. Check that FastAPI is running.";
        }

    }
    finally {
        loadButton.disabled = false;
        loadButton.textContent = "Load Posts";
    }

});