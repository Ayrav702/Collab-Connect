function like(postId) {
  const likeCount = document.getElementById(`likes-count-${postId}`);
  const likeButton = document.getElementById(`like-button-${postId}`);

  fetch(`/like-post/${postId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
          console.log("Server response:", data);

          // Update like count and button appearance
          likeCount.innerHTML = data["likes"];
          likeButton.className = data["liked"] ? "fas fa-thumbs-up like-button" : "far fa-thumbs-up like-button";

          if (data["liked"]) {
              // If the post is liked, add the bounce-on-click class
              likeButton.classList.add('bounce-on-click');

              // Schedule removal of the bounce-on-click class after a short delay
              setTimeout(() => {
                  likeButton.classList.remove('bounce-on-click');
              }, 500);
          }
      })
      .catch((e) => console.error("Error during like request:", e));
}
