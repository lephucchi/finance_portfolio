import { useState, useRef, useEffect } from "react";
import { Send, X, Eye, Minimize2, Maximize2 } from "lucide-react";
import { cn } from "@/lib/utils";

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
];

export default function ChatPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "oracle",
      content:
        "✨ Welcome! I'm the Luminary Guide. I'm here to help you discover clarity in the market data. What would you like to explore today?",
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
          context: {
            module: "lumina_oracle",
            timestamp: new Date().toISOString(),
          },
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
        content:
          "I'm having trouble processing that request. Could you try again?",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Activation Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full glass-panel border border-border/40 text-primary hover:shadow-lg transition-all duration-300 flex items-center justify-center group"
        >
          <Eye className="w-6 h-6 group-hover:scale-110 transition-transform" />
        </button>
      )}

      {/* Oracle Panel - Frosted Glass */}
      {isOpen && (
        <div
          className={cn(
            "fixed bottom-6 right-6 z-50 glass-panel border border-border/40 transition-all duration-300 flex flex-col rounded-2xl",
            isMinimized ? "w-96 h-16" : "w-96 h-[32rem]",
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border/20">
            <div className="flex items-center gap-2">
              <Eye className="w-5 h-5 text-primary" />
              <h3 className="font-semibold text-sm text-foreground">
                Luminary Guide
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1 hover:bg-secondary/50 rounded-md transition-colors"
              >
                {isMinimized ? (
                  <Maximize2 className="w-4 h-4" />
                ) : (
                  <Minimize2 className="w-4 h-4" />
                )}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 hover:bg-secondary/50 rounded-md transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages Container */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "fade-in-scale",
                      message.role === "user" ? "text-right" : "text-left",
                    )}
                  >
                    <div
                      className={cn(
                        "inline-block max-w-xs rounded-lg px-4 py-2 text-sm",
                        message.role === "user"
                          ? "bg-primary/10 text-primary"
                          : "bg-secondary/40 text-foreground",
                      )}
                    >
                      {message.content}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="text-left">
                    <div className="inline-block bg-secondary/40 rounded-lg px-4 py-2">
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
                <div className="px-4 py-3 border-t border-border/20 bg-secondary/10">
                  <p className="text-xs text-muted-foreground mb-2">
                    Try exploring:
                  </p>
                  <div className="space-y-2">
                    {DISCOVERIES.map((disc, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(disc)}
                        className="w-full text-left text-xs px-3 py-2 rounded-lg bg-background/50 hover:bg-primary/10 hover:text-primary transition-colors"
                      >
                        {disc}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input Area */}
              <div className="p-3 border-t border-border/20 flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask anything..."
                  className="flex-1 px-3 py-2 bg-secondary/30 rounded-lg text-sm outline-none focus:ring-1 focus:ring-primary/50 transition-all"
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isLoading}
                  className="px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:shadow-md transition-all disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
