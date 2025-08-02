import React, { useState, useEffect, useRef } from "react";
import { useSpring, animated, config } from "@react-spring/web";

// Config: set to true to fetch from API, false to use local JSON
const USE_API = true;
import commandsData from "./commands.json";

// Fisher-Yates shuffle
function shuffle(array) {
  const arr = array.slice();
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}


export default function VimFlashcard() {
  const [commands, setCommands] = useState([]);
  const [order, setOrder] = useState([]);
  const [orderIdx, setOrderIdx] = useState(0);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("typing"); // typing | correct | wrong
  const [showAnswer, setShowAnswer] = useState(false);
  const inputRef = useRef(null);

  // Fetch questions from API or use local JSON
  useEffect(() => {
    async function loadQuestions() {
      if (USE_API) {
        try {
          const res = await fetch("/api/quiz");
          if (!res.ok) throw new Error("API error");
          const data = await res.json();
          setCommands(data);
          setOrder(shuffle([...Array(data.length).keys()]));
        } catch (e) {
          setCommands(commandsData);
          setOrder(shuffle([...Array(commandsData.length).keys()]));
        }
      } else {
        setCommands(commandsData);
        setOrder(shuffle([...Array(commandsData.length).keys()]));
      }
    }
    loadQuestions();
  }, []);

  const current = commands.length > 0 ? commands[order[orderIdx]] : { command: "", shortcut: "" };

  // Card flip animation
  const { transform, opacity } = useSpring({
    opacity: showAnswer ? 0 : 1,
    transform: `rotateY(${showAnswer ? 180 : 0}deg)`,
    config: config.stiff,
  });

  // Bounce animation for correct
  const bounce = useSpring({
    to: status === "correct" ? { scale: 1.1 } : { scale: 1 },
    config: config.wobbly,
    reset: status !== "correct",
  });

  useEffect(() => {
    // Focus for keyboard input
    if (inputRef.current) inputRef.current.focus();
  }, [orderIdx, showAnswer, commands]);

  useEffect(() => {
    if (status === "correct") {
      const timeout = setTimeout(() => {
        nextCommand();
      }, 600);
      return () => clearTimeout(timeout);
    }
  }, [status]);

  function handleKeyDown(e) {
    if (status === "wrong" && e.key.toLowerCase() === "n") {
      nextCommand();
      return;
    }
    if (status !== "typing") return;
    if (e.key.length === 1) {
      const nextInput = input + e.key;
      if (current.shortcut.startsWith(nextInput)) {
        setInput(nextInput);
        if (nextInput === current.shortcut) {
          setStatus("correct");
        }
      } else {
        setInput(nextInput);
        setStatus("wrong");
        setTimeout(() => setShowAnswer(true), 0);
      }
    } else if (e.key === "Backspace") {
      setInput(input.slice(0, -1));
    }
  }

  function nextCommand() {
    setShowAnswer(false);
    setStatus("typing");
    setInput("");
    setOrderIdx((prev) => {
      const next = prev + 1;
      if (next >= order.length) {
        // Reshuffle for endless play
        setOrder(shuffle([...Array(commands.length).keys()]));
        return 0;
      }
      return next;
    });
  }

  // Render input with color
  function renderInput() {
    // Only show what the user has typed, no underscores for remaining letters
    return (
      <>
        {input.split("").map((ch, i) => {
          let color = "#a0aec0";
          if (status === "wrong") color = "#e53e3e";
          else if (ch === current.shortcut[i]) color = "#38a169";
          else color = "#e53e3e";
          return (
            <span key={i} style={{ color, fontWeight: "bold" }}>{ch}</span>
          );
        })}
      </>
    );
  }

  return (
    <div
      tabIndex={0}
      ref={inputRef}
      onKeyDown={handleKeyDown}
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        background: "#18181b",
        color: "#f1f5f9",
        outline: "none",
      }}
    >
      <div style={{ perspective: 1000, width: 340, height: 180, position: "relative" }}>
        <animated.div
          style={{
            width: 340,
            height: 180,
            position: "absolute",
            top: 0,
            left: 0,
            borderRadius: 16,
            boxShadow: "0 8px 32px #0006",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 28,
            fontWeight: 600,
            background: "#27272a",
            color: "#f1f5f9",
            backfaceVisibility: "hidden",
            transform: transform,
            opacity: opacity,
            zIndex: showAnswer ? 1 : 2,
          }}
        >
          {current.command}
        </animated.div>
        <animated.div
          style={{
            width: 340,
            height: 180,
            position: "absolute",
            top: 0,
            left: 0,
            borderRadius: 16,
            boxShadow: "0 8px 32px #0006",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 32,
            fontWeight: 700,
            background: "#fbbf24",
            color: "#18181b",
            backfaceVisibility: "hidden",
            transform: transform.to(t => `${t} rotateY(180deg)`),
            opacity: showAnswer ? 1 : 0,
            zIndex: showAnswer ? 2 : 1,
          }}
        >
          {current.shortcut}
        </animated.div>
      </div>
      <animated.div
        style={{
          marginTop: 48,
          fontSize: 36,
          fontFamily: "monospace",
          minHeight: 48,
          borderBottom: "2px solid #52525b",
          width: 180,
          textAlign: "center",
          ...bounce,
        }}
      >
        {renderInput()}
        <span className="blinking-cursor">|</span>
      </animated.div>
      {status === "wrong" && (
        <div style={{ color: "#e53e3e", marginTop: 24, fontWeight: 500 }}>
          Wrong! Press <kbd>n</kbd> for next.
        </div>
      )}
    </div>
  );
}
