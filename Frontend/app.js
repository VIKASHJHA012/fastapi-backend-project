const loadButton = document.getElementById("load-posts");

const postContainer = document.getElementById("post-container");

const emailInput = document.getElementById("user-email")

// loadButton.addEventListener("click",function(){
//     const email = emailInput.value;
    
// postContainer.textContent =`You entered:${email}`;
// })

loadButton.addEventListener("click",async function() {
    const email = emailInput.value.trim();
    if (!email){
        postContainer.textContent = "Please enter an email address."
        return;
    }
    const url = `http://127.0.0.1:8000/api-post-v1/Post/User/${encodeURIComponent(email)}`;
loadButton.disabled = true;
loadButton.textContent= "Loading...";
    try {
        postContainer.textContent ="Loading posts..."
        const response = await fetch(url);

        if(!response.ok){
            throw new Error(`Request failed: ${response.status}`);
        }

        const data = await response.json();
        // postContainer.textContent = JSON.stringify(data,null,2)

        postContainer.replaceChildren();
        if (data.length == 0 ){
            postContainer.textContent="No posts found for the user";
            return;
        }
        data.forEach(function(post)  {
            const card = document.createElement("div");
            card.className = "post-card";

            const title = document.createElement("h3");
            title.textContent = post.title;

            const details = document.createElement("p");
            details.textContent= `Post ID: ${post.id}| User Id : ${post.user_id}`
            card.append(title,details)
            postContainer.append(card)
        });
    }
    catch(error){

    console.error("Failed to load posts:", error);

    if (error.message.startsWith("Request failed:")) {
        postContainer.textContent =
            `The server returned an error. ${error.message}`;
    } else {
        postContainer.textContent =
            "Could not connect to the backend. Check that FastAPI is running.";
    }

    }
    finally{
        loadButton.disabled = false;
        loadButton.textContent= "Load Posts";
    }

});