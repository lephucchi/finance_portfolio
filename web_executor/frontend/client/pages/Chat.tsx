import { useState, useRef, useEffect } from "react";
import { Send, Trash2, Eye } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "oracle";
  content: string;
  timestamp: Date;
}

const DISCOVERIES = [
  "What insights can you share about FPT today?",
  "How are different sectors performing?",
  "Show me stocks with interesting patterns.",
  "What should I explore in the market?",
  "Any emerging trends I should know about?",
  "What about the banking sector today?",
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "oracle",
      content:
        "✨ Welcome! I'm the Luminary Guide. I'm here to help you discover clarity in market data. What would you like to explore?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: messageText,
          context: { module: "lumina", timestamp: new Date().toISOString() },
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const oracleMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "oracle",
          content: data.response || "I'm processing your request...",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, oracleMessage]);
      }
    } catch (error) {
      console.error("Oracle error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "oracle",
        content: "I'm having trouble processing that. Could you try again?",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: "1",
        role: "oracle",
        content:
          "✨ Session refreshed. Ready to explore. What catches your interest?",
        timestamp: new Date(),
      },
    ]);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="card-lumina m-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Eye className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              Luminary Guide
            </h1>
            <p className="text-xs text-muted-foreground">
              AI-powered market insights
            </p>
          </div>
        </div>
        <button
          onClick={handleClearChat}
          className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} fade-in-scale`}
          >
            <div className="max-w-2xl">
              <div
                className={`inline-block max-w-md rounded-lg px-4 py-2 ${
                  message.role === "user"
                    ? "bg-primary/10 text-primary"
                    : "card-lumina"
                }`}
              >
                <p className="text-sm">{message.content}</p>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="card-lumina px-4 py-2">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <div
                  className="w-2 h-2 bg-primary rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                />
                <div
                  className="w-2 h-2 bg-primary rounded-full animate-bounce"
                  style={{ animationDelay: "0.4s" }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Discoveries */}
      {messages.length === 1 && !isLoading && (
        <div className="px-6 pb-4">
          <p className="text-xs text-muted-foreground mb-3 font-medium">
            Explore these topics:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {DISCOVERIES.map((disc, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(disc)}
                className="text-left text-xs px-3 py-2 rounded-lg bg-secondary/30 hover:bg-primary/10 hover:text-primary transition-colors text-foreground"
              >
                {disc}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="px-6 pb-6 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
          placeholder="Ask anything..."
          className="input-lumina flex-1"
          disabled={isLoading}
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={!input.trim() || isLoading}
          className="btn-lumina-primary px-4 py-2 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
