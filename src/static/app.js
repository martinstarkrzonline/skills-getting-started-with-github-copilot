document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const participants = Array.isArray(details.participants) ? details.participants : [];
        const spotsLeft = details.max_participants - participants.length;

        const title = document.createElement("h4");
        title.textContent = name;

        const desc = document.createElement("p");
        desc.textContent = details.description;

        const schedule = document.createElement("p");
        schedule.innerHTML = `<strong>Schedule:</strong> ${details.schedule}`;

        const availability = document.createElement("p");
        availability.innerHTML = `<strong>Availability:</strong> ${spotsLeft} spots left`;

        const participantsBlock = document.createElement("div");
        participantsBlock.className = "participants";

        const participantsHeading = document.createElement("strong");
        participantsHeading.textContent = "Participants:";
        participantsBlock.appendChild(participantsHeading);

        console.log(`Rendering activity card for ${name}. participants=`, participants);
        console.log(`Rendering activity card for ${name}. participants=`, participants);
        if (participants.length > 0) {
          const list = document.createElement("ul");
          list.className = "participants-list";
          participants.forEach(p => {
            const li = document.createElement("li");
            const emailSpan = document.createElement("span");
            emailSpan.textContent = p;
            const deleteIcon = document.createElement("span");
            deleteIcon.textContent = " ×";
            deleteIcon.className = "delete-icon";
            deleteIcon.style.cursor = "pointer";
            deleteIcon.style.color = "#c62828";
            deleteIcon.style.marginLeft = "10px";
            deleteIcon.addEventListener("click", async () => {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(p)}`,
                  {
                    method: "DELETE",
                  }
                );
                const result = await response.json();
                if (response.ok) {
                  await fetchActivities();
                } else {
                  alert(result.detail || "An error occurred");
                }
              } catch (error) {
                alert("Failed to unregister. Please try again.");
                console.error("Error unregistering:", error);
              }
            });
            li.appendChild(emailSpan);
            li.appendChild(deleteIcon);
            list.appendChild(li);
          });
          participantsBlock.appendChild(list);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants signed up yet.";
          participantsBlock.appendChild(noParticipants);
        }

        activityCard.appendChild(title);
        activityCard.appendChild(desc);
        activityCard.appendChild(schedule);
        activityCard.appendChild(availability);
        activityCard.appendChild(participantsBlock);

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
