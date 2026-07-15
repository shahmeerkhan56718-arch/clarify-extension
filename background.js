// 1. Create the right-click menu item when the extension is installed
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "findSynonyms",
    title: "Find Easy Synonyms for '%s'",
    contexts: ["selection"] // Only show this menu when text is highlighted
  });
});

// 2. Listen for when the user clicks our right-click option
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "findSynonyms" && info.selectionText) {
    const selectedText = info.selectionText.trim();

    // Send the highlighted text to your running Flask server
    fetch("http://127.0.0.1:5000/explain", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: selectedText })
    })
    .then(response => response.json())
    .then(data => {
      const result = data.explanation || "No synonyms found.";
      
      // Inject a script into the active web page to show a sleek browser alert with the results
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: (word, synonyms) => {
          alert(`Easy synonyms for "${word}":\n\n${synonyms}`);
        },
        args: [selectedText, result]
      });
    })
    .catch(error => {
      console.error("Error:", error);
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
          alert("Error: Make sure your Python Flask server is running in the background!");
        }
      });
    });
  }
});