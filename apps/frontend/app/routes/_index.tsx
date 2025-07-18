import { useState, useEffect, useRef, FormEvent } from "react";
import type { MetaFunction } from "@remix-run/node";
import { v4 as uuidv4 } from "uuid";

export const meta: MetaFunction = () => {
  return [
    { title: "ChitChatChot - AI Chat" },
    { name: "description", content: "A fancy chat application powered by AI." },
  ];
};

// --- TYPE DEFINITIONS ---
interface Message {
  id: string;
  type: "user" | "assistant" | "status";
  content: string;
  timestamp: string;
}

// --- SVG ICONS ---
const UserIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-8 w-8 text-gray-500"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);

const BotIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className="h-8 w-8 text-blue-500"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M12 8V4H8" />
    <rect x="4" y="12" width="16" height="8" rx="2" />
    <path d="M2 14h2" />
    <path d="M20 14h2" />
    <path d="M15 12v-2a3 3 0 0 0-3-3H9a3 3 0 0 0-3 3v2" />
  </svg>
);

const SendIcon = () => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-6 w-6"
    >
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
    </svg>
);


// --- MAIN CHAT COMPONENT ---
export default function Index() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [chatId, setChatId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // --- EFFECTS ---
  useEffect(() => {
    // Generate a unique chat ID on component mount
    const newChatId = uuidv4();
    setChatId(newChatId);
  }, []);

  useEffect(() => {
    if (!chatId) return;

    // Establish WebSocket connection
    const wsUrl = `ws://localhost:8000/ws/${chatId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log("WebSocket connected");
      setMessages([{
        id: uuidv4(),
        type: "status",
        content: "Connected to AI. Ask me anything!",
        timestamp: new Date().toISOString(),
      }]);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "user_message":
          // This is handled locally now, but could be used for multi-client sync
          break;
        case "ai_start":
          setIsStreaming(true);
          setMessages((prev) => [
            ...prev,
            { id: uuidv4(), type: "assistant", content: "", timestamp: data.timestamp },
          ]);
          break;
        case "ai_chunk":
          setMessages((prev) =>
            prev.map((msg) =>
              msg.type === "assistant" && msg.timestamp === prev[prev.length - 1].timestamp
                ? { ...msg, content: msg.content + data.chunk }
                : msg
            )
          );
          break;
        case "ai_complete":
          setIsStreaming(false);
          break;
        case "error":
          setIsStreaming(false);
           setMessages((prev) => [
            ...prev,
            { id: uuidv4(), type: "status", content: `Error: ${data.message}`, timestamp: data.timestamp },
          ]);
          break;
      }
    };

    ws.current.onclose = () => {
      console.log("WebSocket disconnected");
       setMessages((prev) => [
            ...prev,
            { id: uuidv4(), type: "status", content: "Connection lost. Please refresh.", timestamp: new Date().toISOString() },
          ]);
    };

    ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
    };

    // Cleanup on component unmount
    return () => {
      ws.current?.close();
    };
  }, [chatId]);

  useEffect(() => {
    // Auto-scroll to the latest message
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);


  // --- HANDLERS ---
  const handleSendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && ws.current?.readyState === WebSocket.OPEN && !isStreaming) {
      const userMessage: Message = {
        id: uuidv4(),
        type: "user",
        content: input,
        timestamp: new Date().toISOString(),
      };
      
      // Send to WebSocket server
      ws.current.send(JSON.stringify({ message: input }));
      
      // Update local state
      setMessages((prev) => [...prev, userMessage]);
      setInput("");
    }
  };

  // --- RENDER ---
  return (
    <div className="flex h-screen flex-col bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="flex items-center gap-3">
            <img src="/logo-light.png" alt="Logo" className="h-8 w-auto dark:hidden" />
            <img src="/logo-dark.png" alt="Logo" className="hidden h-8 w-auto dark:block" />
            <h1 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                ChitChatChot
            </h1>
        </div>
        <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm text-gray-600 dark:text-gray-300">Live</span>
        </div>
      </header>

      {/* Message Area */}
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-4xl space-y-8">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex items-start gap-4 ${msg.type === 'user' ? 'justify-end' : ''}`}>
              {msg.type === 'assistant' && <BotIcon />}
              
              {msg.type === 'status' ? (
                <div className="w-full text-center text-sm text-gray-500 dark:text-gray-400">
                  {msg.content}
                </div>
              ) : (
                <div className={`max-w-xl rounded-2xl px-5 py-3 shadow-sm ${
                    msg.type === 'user'
                      ? 'rounded-br-none bg-blue-600 text-white'
                      : 'rounded-bl-none bg-white dark:bg-gray-700 dark:text-gray-200'
                  }`}
                >
                  <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>
              )}

              {msg.type === 'user' && <UserIcon />}
            </div>
          ))}
          {isStreaming && (
             <div className="flex items-start gap-4">
                <BotIcon />
                <div className="rounded-2xl rounded-bl-none bg-white px-5 py-3 shadow-sm dark:bg-gray-700">
                    <div className="flex items-center justify-center gap-2">
                        <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500 [animation-delay:-0.3s]"></span>
                        <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500 [animation-delay:-0.15s]"></span>
                        <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500"></span>
                    </div>
                </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Form */}
      <footer className="border-t border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto max-w-4xl">
          <form onSubmit={handleSendMessage} className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isStreaming ? "Waiting for response..." : "Type your message..."}
              disabled={isStreaming}
              className="w-full rounded-full border-gray-300 bg-gray-100 px-5 py-3 text-gray-800 transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/50 disabled:cursor-not-allowed disabled:opacity-70 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="inline-flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-blue-600 text-white transition hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-blue-400 dark:focus:ring-offset-gray-800"
            >
              <SendIcon />
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
}