import React from 'react'
import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  // Fetch and display welcome message when user logs in
  useEffect(() => {
    if (loggedIn && messages.length === 0) {
      const fetchWelcomeMessage = async () => {
        try {
          const res = await fetch("http://127.0.0.1:8000/welcome");
          const data = await res.json();
          setMessages([{ role: "bot", text: data.message }]);
        } catch (err) {
          // Fallback to default message if API fails
          setMessages([{ 
            role: "bot", 
            text: "Hi, I am your banking assistant. How can I help you today?" 
          }]);
        }
      };
      fetchWelcomeMessage();
    }
  }, [loggedIn, messages.length]);

  const login = async () => {
    setError("");
    const res = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      setLoggedIn(true);
    } else {
      setError("Invalid username or password");
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: input }]);
    setInput("");

    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { role: "bot", text: data.response }]);
  };

  // ---- LOGIN PAGE ----
  if (!loggedIn) {
    return (
      <div className="login-container">
        <h2>Login</h2>

        <input
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={login}>Login</button>

        {error && <p className="error">{error}</p>}
      </div>
    );
  }

  // ---- CHAT PAGE ----
  return (
    <div className="chat-container">
      <h2>Ollama Chat</h2>

      <div className="chat-box" style={{ display: "flex", flexDirection: "column" }}>
        {messages.map((m, i) => (
          <div key={i} className={m.role}>
            {m.text}
          </div>
        ))}
      </div>

      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
