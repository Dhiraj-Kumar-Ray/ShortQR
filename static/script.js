// Step 1: find the elements we need on the page (the DOM)
const form = document.getElementById("shorten-form");
const urlInput = document.getElementById("url-input");
const shortenButton = document.getElementById("shorten-button");
const messageBox = document.getElementById("message");
const resultBox = document.getElementById("result");
const shortLink = document.getElementById("short-link");
const copyButton = document.getElementById("copy-button");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");


// Show a message. type is "loading", "success" or "error".
function showMessage(text, type) {
    messageBox.textContent = text;
    messageBox.className = "message " + type;
}

function hideMessage() {
    messageBox.className = "message hidden";
}


// Step 2: run this code when the form is submitted
form.addEventListener("submit", async function (event) {
    // Stop the browser from reloading the page
    event.preventDefault();

    // Reset the screen and show the loading state
    resultBox.classList.add("hidden");
    showMessage("Shortening...", "loading");
    shortenButton.disabled = true;

    try {
        // Send the form data to our Flask route in the background
        const response = await fetch("/shorten", {
            method: "POST",
            body: new FormData(form),
        });

        // Turn the JSON reply into a JavaScript object
        const data = await response.json();

        if (response.ok) {
            // Success: show the short link
            shortLink.textContent = data.short_url;
            shortLink.href = data.short_url;
            resultBox.classList.remove("hidden");
            showMessage("Your short link is ready!", "success");
             loadHistory();
        } else {
            // The server said no (for example status 400)
            showMessage(data.error, "error");
        }
    } catch (error) {
        // The request itself failed (server off, no internet...)
        showMessage("Something went wrong. Please try again.", "error");
    }

    // Always re-enable the button, whether it worked or not
    shortenButton.disabled = false;
});


// Step 3: copy the short link when the Copy button is clicked
copyButton.addEventListener("click", async function () {
    try {
        await navigator.clipboard.writeText(shortLink.textContent);
        copyButton.textContent = "Copied!";

        // After 2 seconds, change the label back
        setTimeout(function () {
            copyButton.textContent = "Copy";
        }, 2000);
    } catch (error) {
        showMessage("Could not copy. Please copy it by hand.", "error");
    }
});

// Ask the server for recent links and draw them on the page
async function loadHistory() {
    try {
        const response = await fetch("/api/recent");
        const links = await response.json();

        // Clear the old list before drawing the new one
        historyList.innerHTML = "";

        // Show or hide the "No links yet." text
        if (links.length === 0) {
            historyEmpty.classList.remove("hidden");
        } else {
            historyEmpty.classList.add("hidden");
        }

        for (const link of links) {
            const item = document.createElement("li");

            const shortPart = document.createElement("a");
            shortPart.className = "history-short";
            shortPart.href = link.short_url;
            shortPart.target = "_blank";
            shortPart.textContent = link.short_url;

            const originalPart = document.createElement("div");
            originalPart.className = "history-original";
            originalPart.textContent = link.original_url;

            const clicksPart = document.createElement("div");
            clicksPart.className = "history-clicks";
            clicksPart.textContent = link.clicks + " clicks";

            item.appendChild(shortPart);
            item.appendChild(originalPart);
            item.appendChild(clicksPart);
            historyList.appendChild(item);
        }
    } catch (error) {
        // If history fails to load, the rest of the page still works
        console.error("Could not load history:", error);
    }
}

// Load the history once when the page first opens
loadHistory();

// ---------- Dark mode toggle ----------
const themeToggle = document.getElementById("theme-toggle");

// Show a sun in dark mode (click for light) and a moon in light mode
function updateThemeIcon() {
    const current = document.documentElement.getAttribute("data-theme");
    themeToggle.textContent = current === "dark" ? "☀️" : "🌙";
}

themeToggle.addEventListener("click", function () {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";

    document.documentElement.setAttribute("data-theme", next);

    // Remember the choice for next time
    try {
        localStorage.setItem("theme", next);
    } catch (error) {
        console.error("Could not save theme:", error);
    }

    updateThemeIcon();
});

// Set the correct icon when the page first loads
updateThemeIcon();