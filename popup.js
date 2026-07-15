// 1. Synonym Lookup
document.getElementById('getSynonymsBtn').addEventListener('click', () => {
  const word = document.getElementById('wordInput').value.trim();
  const outputDiv = document.getElementById('synonymOutput');
  
  if (!word) {
    outputDiv.innerText = "Please enter a word.";
    return;
  }
  
  outputDiv.innerText = "Searching...";
  
  fetch('http://127.0.0.1:5000/synonym', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: word })
  })
  .then(res => res.json())
  .then(data => {
    outputDiv.innerText = data.result || "No synonyms found.";
  })
  .catch(err => {
    outputDiv.innerText = "Error: Server is not running!";
  });
});

// 2. Pronunciation
document.getElementById('speakBtn').addEventListener('click', async () => {
  const word = document.getElementById('wordInput').value.trim();
  const outputDiv = document.getElementById('synonymOutput');
  
  if (!word) {
    outputDiv.innerText = "Please enter a word to speak.";
    return;
  }



  try {
    const response = await fetch('http://127.0.0.1:5000/pronounce', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: word })
    });
    
    const data = await response.json();
    
    if (data.audio) {
      new Audio("data:audio/mp3;base64," + data.audio).play();
    } else {
      outputDiv.innerText = "Could not generate audio.";
    }
  } catch (err) {
    outputDiv.innerText = "Error: Server is not running!";
  }
});

// 3. Paragraph Simplifier
document.getElementById('simplifyBtn').addEventListener('click', () => {
  const paragraph = document.getElementById('paragraphInput').value.trim();
  const outputDiv = document.getElementById('paragraphOutput');
  
  if (!paragraph) {
    outputDiv.innerText = "Please enter some text.";
    return;
  }
  
  outputDiv.innerText = "Simplifying...";
  
  fetch('http://127.0.0.1:5000/simplify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: paragraph })
  })
  .then(res => res.json())
  .then(data => {
    outputDiv.innerText = data.result || "Could not simplify.";
  })
  .catch(err => {
    outputDiv.innerText = "Error: Server is not running!";
  });
});