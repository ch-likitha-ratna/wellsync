// Chatbot

function toggleQuickAccess() {
  const links = document.getElementById('quickAccessLinks');
  links.classList.toggle('hidden');
}

function toggleChatbot() {
  const bot = document.getElementById('chatbot');
  bot.classList.toggle('hidden');
}

function sendMessage() {
  const input = document.getElementById('userInput');
  const chatbox = document.getElementById('chatbox');
  const message = input.value.trim();
  if (!message) return;

  const userMsg = document.createElement('div');
  userMsg.className = 'text-right text-blue-600';
  userMsg.textContent = message;
  chatbox.appendChild(userMsg);
  input.value = '';
  chatbox.scrollTop = chatbox.scrollHeight;

  const botMsg = document.createElement('div');
  botMsg.className = 'text-left text-gray-800';
  chatbox.appendChild(botMsg);

  fetch("/api/chat", {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      "Accept": "text/plain"
    },
    body: JSON.stringify({ prompt: message }),
  })
    .then(response => response.text())
    .then(text => {
      botMsg.textContent = text;
      chatbox.scrollTop = chatbox.scrollHeight;
    })
    .catch(() => {
      const errorMsg = document.createElement('div');
      errorMsg.className = 'text-left text-red-600';
      errorMsg.textContent = '⚠️ Failed to connect to server.';
      chatbox.appendChild(errorMsg);
      chatbox.scrollTop = chatbox.scrollHeight;
    });
}

// Tabs and Sections
function showTab(id) {
  document.querySelectorAll('.tab').forEach(el => el.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

function showSection(id) {
  document.querySelectorAll('.section').forEach(el => el.classList.add('hidden'));
  document.getElementById(id).classList.remove('hidden');
}

function showMainSection(id) {
  showSection(id);
}


function showTab(tabId, el) {
  const tabs = document.querySelectorAll(".tab");
  tabs.forEach(tab => tab.classList.add("hidden"));

  document.getElementById(tabId).classList.remove("hidden");

  // Remove active class from all tab buttons
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));

  // Add active class to the clicked tab
  if (el) el.classList.add("active");
}

function setActiveSidebar(linkId) {
  document.querySelectorAll(".sidebar-link").forEach(link => {
    link.classList.remove("active");
  });

  const activeLink = document.getElementById(linkId);
  if (activeLink) {
    activeLink.classList.add("active");
  }
}

// static/js/script.js

// Show/hide quick access on scroll
window.addEventListener("scroll", () => {
  const quickAccess = document.getElementById("quick-access-links");
  const scrollThreshold = 300; // px from top
  if (window.scrollY >= scrollThreshold) {
    quickAccess.classList.remove("hidden");
  } else {
    quickAccess.classList.add("hidden");
  }
});

function showTab(tabId, button) {
  // Hide all tab content
  document.querySelectorAll('.tab').forEach(tab => tab.classList.add('hidden'));

  // Show selected tab
  document.getElementById(tabId).classList.remove('hidden');

  // Reset tab button styles
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('font-bold', 'border-b-2', 'border-blue-500');
  });

  // Highlight selected button
  button.classList.add('font-bold', 'border-b-2', 'border-blue-500');
}


document.addEventListener("DOMContentLoaded", () => {
  const sections = document.querySelectorAll("section");
  const navLinks = document.querySelectorAll(".sidebar-link");

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navLinks.forEach(link => {
            link.classList.remove("text-white", "font-bold");
            link.querySelector("span")?.classList.remove("w-full");
            link.querySelector("span")?.classList.add("w-0");
          });
          const id = entry.target.getAttribute("id");
          const activeLink = document.querySelector(`.sidebar-link[href="#${id}"]`);
          if (activeLink) {
            activeLink.classList.add("text-white", "font-bold");
            activeLink.querySelector("span")?.classList.add("w-full");
            activeLink.querySelector("span")?.classList.remove("w-0");
          }
        }
      });
    },
    { threshold: 0.5 }
  );

  sections.forEach(section => observer.observe(section));
});




function showServiceTab(id, btn) {
  // Hide all content
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.add('hidden'));

  // Show the selected tab content
  document.getElementById(id).classList.remove('hidden');

  // Reset all tab buttons
  document.querySelectorAll('.s-tab-btn').forEach(button => {
    button.classList.remove('active-tab');
  });

  // Mark clicked tab as active
  btn.classList.add('active-tab');
}

// Optional: Show first tab on page load
document.addEventListener('DOMContentLoaded', () => {
  const defaultTab = document.querySelector('.s-tab-btn');
  showServiceTab('s-ai', defaultTab);
});


