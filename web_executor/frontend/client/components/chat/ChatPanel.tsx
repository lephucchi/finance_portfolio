import { useState, useRef, useEffect } from "react";
import { Send, X, Eye, Minimize2, Maximize2, Key, CheckCircle, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "oracle";
  content: string;
  timestamp: Date;
  sources?: Array<{
    id: number;
    text: string;
    score: number;
  }>;
}

const DISCOVERIES = [
  "Tình hình thị trường chứng khoán Việt Nam?",
  "VN-Index biến động như thế nào?",
  "Các ngành nào đang triển vọng?",
  "Phân tích cổ phiếu ngân hàng?",
  "Xu hướng đầu tư nổi bật?",
];

export default function ChatPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "oracle",
      content:
        "✨ Xin chào! Tôi là trợ lý tài chính AI. Tôi có thể giúp bạn phân tích thị trường Việt Nam. Bạn cần tư vấn gì?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [apiKeyValid, setApiKeyValid] = useState<boolean | null>(null);
  const [showKeyInput, setShowKeyInput] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const validateApiKey = async (keyToValidate?: string) => {
    const key = keyToValidate || apiKey;
    if (!key.trim()) return;

    try {
      const response = await fetch("/api/v1/rag/validate-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key }),
      });

      const data = await response.json();
      setApiKeyValid(data.valid);

      if (data.valid) {
        localStorage.setItem("gemini_api_key", key);
        setShowKeyInput(false);
      }
    } catch (error) {
      console.error("Validation failed:", error);
      setApiKeyValid(false);
    }
  };

  // Load API key from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) {
      setApiKey(savedKey);
      validateApiKey(savedKey);
    }
  }, []);

  const handleSendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText) return;

    // Check API key
    if (!apiKey || apiKeyValid !== true) {
      setShowKeyInput(true);
      return;
    }

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
      const response = await fetch("/api/v1/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: messageText,
          api_key: apiKey,
          top_k: 3,
          use_cache: true,
          conversation_history: messages
            .filter((m) => m.role !== "oracle" || m.content !== messages[0].content)
            .map((m) => ({
              role: m.role === "user" ? "user" : "assistant",
              content: m.content,
              timestamp: m.timestamp.toISOString(),
            })),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.success) {
          const oracleMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "oracle",
            content: data.answer || "Đang xử lý...",
            timestamp: new Date(data.timestamp),
            sources: data.sources,
          };
          setMessages((prev) => [...prev, oracleMessage]);
        } else {
          throw new Error(data.error || "Query failed");
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "oracle",
        content: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.",
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
                Trợ lý AI
              </h3>
              {apiKeyValid === true && (
                <CheckCircle className="w-3 h-3 text-green-600" />
              )}
              {apiKeyValid === false && (
                <XCircle className="w-3 h-3 text-red-600" />
              )}
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowKeyInput(!showKeyInput)}
                className="p-1 hover:bg-secondary/50 rounded-md transition-colors"
                title="API Settings"
              >
                <Key className="w-4 h-4" />
              </button>
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
              {/* API Key Input */}
              {showKeyInput && (
                <div className="p-3 border-b border-border/20 bg-secondary/10 space-y-2">
                  <div className="text-xs text-muted-foreground">
                    <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                      Get free API key
                    </a>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="AIzaSy..."
                      className="flex-1 px-2 py-1 bg-background/50 rounded text-xs outline-none focus:ring-1 focus:ring-primary/50"
                    />
                    <button
                      onClick={() => validateApiKey()}
                      className="px-2 py-1 bg-primary text-primary-foreground rounded text-xs"
                    >
                      Save
                    </button>
                  </div>
                </div>
              )}
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
              {messages.length === 1 && !isLoading && apiKeyValid === true && (
                <div className="px-4 py-3 border-t border-border/20 bg-secondary/10">
                  <p className="text-xs text-muted-foreground mb-2">
                    Câu hỏi gợi ý:
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
                  onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
                  placeholder={apiKeyValid === true ? "Nhập câu hỏi..." : "⚠️ Cấu hình API key"}
                  className="flex-1 px-3 py-2 bg-secondary/30 rounded-lg text-sm outline-none focus:ring-1 focus:ring-primary/50 transition-all"
                  disabled={isLoading || apiKeyValid !== true}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isLoading || apiKeyValid !== true}
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
