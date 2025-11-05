import { useState, useRef, useEffect } from "react";
import { Send, Trash2, Eye, Key, CheckCircle, XCircle, Settings } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

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
  "Tình hình thị trường chứng khoán Việt Nam hiện tại?",
  "VN-Index biến động như thế nào tuần này?",
  "Các ngành nào đang có triển vọng tốt?",
  "Phân tích cổ phiếu ngân hàng hôm nay?",
  "Xu hướng đầu tư nào đang nổi bật?",
  "Tin tức nào đang ảnh hưởng thị trường?",
];

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "oracle",
      content:
        "✨ Xin chào! Tôi là trợ lý tài chính AI. Tôi có thể giúp bạn phân tích thị trường chứng khoán Việt Nam. Bạn muốn tìm hiểu điều gì?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState("");
  const [apiKeyValid, setApiKeyValid] = useState<boolean | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [showSources, setShowSources] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load API key from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem("gemini_api_key");
    if (savedKey) {
      setApiKey(savedKey);
      // Auto-validate saved key
      validateApiKey(savedKey);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const validateApiKey = async (keyToValidate?: string) => {
    const key = keyToValidate || apiKey;
    if (!key.trim()) return;

    setIsValidating(true);
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout
    
    try {
      console.log(`[RAG] Validating API key (length: ${key.length})...`);
      const startTime = Date.now();
      
      const response = await fetch("/api/v1/rag/validate-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: key }),
        signal: controller.signal,
      });

      const elapsed = Date.now() - startTime;
      console.log(`[RAG] Response received in ${elapsed}ms, status: ${response.status}`);

      const data = await response.json();
      console.log(`[RAG] Validation result:`, data);
      
      setApiKeyValid(data.valid);

      if (data.valid) {
        localStorage.setItem("gemini_api_key", key);
        console.log(`[RAG] API key saved to localStorage`);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.error("[RAG] Validation timeout after 15s");
        setApiKeyValid(false);
      } else {
        console.error("[RAG] Validation failed:", error);
        setApiKeyValid(false);
      }
    } finally {
      clearTimeout(timeoutId);
      setIsValidating(false);
    }
  };

  const handleSendMessage = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText) return;

    // Check if API key is valid
    if (!apiKey || apiKeyValid === false) {
      setShowSettings(true);
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
      // Use RAG endpoint instead of /api/ai/chat
      const response = await fetch("/api/v1/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: messageText,
          api_key: apiKey,
          top_k: 5,
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
            content: data.answer || "Đang xử lý yêu cầu của bạn...",
            timestamp: new Date(data.timestamp),
            sources: data.sources,
          };
          setMessages((prev) => [...prev, oracleMessage]);
        } else {
          throw new Error(data.error || "Query failed");
        }
      } else {
        throw new Error("API request failed");
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "oracle",
        content: "Xin lỗi, tôi gặp vấn đề khi xử lý câu hỏi. Vui lòng thử lại sau.",
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
          "✨ Xin chào! Tôi là trợ lý tài chính AI. Tôi có thể giúp bạn phân tích thị trường chứng khoán Việt Nam. Bạn muốn tìm hiểu điều gì?",
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
              Trợ lý Tài chính AI
            </h1>
            <p className="text-xs text-muted-foreground">
              RAG-powered Vietnamese market insights
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* API Key Status Indicator */}
          {apiKeyValid === true && (
            <div className="flex items-center gap-1 text-green-600 text-xs">
              <CheckCircle className="w-3 h-3" />
              <span>Connected</span>
            </div>
          )}
          {apiKeyValid === false && (
            <div className="flex items-center gap-1 text-red-600 text-xs">
              <XCircle className="w-3 h-3" />
              <span>No API key</span>
            </div>
          )}
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
            title="API Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
          <button
            onClick={handleClearChat}
            className="p-2 rounded-lg hover:bg-secondary/50 transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* API Key Settings Panel */}
      {showSettings && (
        <div className="mx-6 mb-4 card-lumina p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-primary" />
              <h3 className="font-semibold">Gemini API Key</h3>
            </div>
            <button
              onClick={() => setShowSettings(false)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Close
            </button>
          </div>
          
          <p className="text-xs text-muted-foreground">
            Nhập API key của bạn từ{" "}
            <a
              href="https://makersuite.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Google AI Studio
            </a>{" "}
            (miễn phí)
          </p>

          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => {
                setApiKey(e.target.value);
                setApiKeyValid(null);
              }}
              placeholder="AIzaSy..."
              className="input-lumina flex-1 text-sm"
              disabled={isValidating}
            />
            <button
              onClick={() => validateApiKey()}
              disabled={!apiKey.trim() || isValidating}
              className="btn-lumina-primary px-3 text-sm disabled:opacity-50"
            >
              {isValidating ? "Checking..." : "Validate"}
            </button>
          </div>

          {apiKeyValid === true && (
            <div className="flex items-center gap-2 text-green-600 text-xs bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded">
              <CheckCircle className="w-4 h-4" />
              <span>API key is valid! You can start chatting.</span>
            </div>
          )}

          {apiKeyValid === false && (
            <div className="flex items-center gap-2 text-red-600 text-xs bg-red-50 dark:bg-red-900/20 px-3 py-2 rounded">
              <XCircle className="w-4 h-4" />
              <span>Invalid API key. Please check and try again.</span>
            </div>
          )}
        </div>
      )}

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
                {message.role === "user" ? (
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                ) : (
                  <div className="text-sm prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                )}
                
                {/* Source Citations */}
                {message.sources && message.sources.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border/50">
                    <button
                      onClick={() => setShowSources(showSources === message.id ? null : message.id)}
                      className="text-xs text-primary hover:underline"
                    >
                      {showSources === message.id ? "Ẩn" : "Xem"} {message.sources.length} nguồn tin
                    </button>

                    {showSources === message.id && (
                      <div className="mt-2 space-y-2">
                        {message.sources.map((source, i) => (
                          <div key={i} className="text-xs bg-secondary/30 p-2 rounded">
                            <div className="font-medium text-primary mb-1">
                              Nguồn {i + 1} ({(source.score * 100).toFixed(1)}% liên quan)
                            </div>
                            <p className="line-clamp-3 text-muted-foreground">
                              {source.text}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
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
      {messages.length === 1 && !isLoading && apiKeyValid === true && (
        <div className="px-6 pb-4">
          <p className="text-xs text-muted-foreground mb-3 font-medium">
            Câu hỏi gợi ý:
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
          onKeyPress={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
          placeholder={
            apiKeyValid === true
              ? "Nhập câu hỏi của bạn..."
              : "⚠️ Vui lòng cấu hình API key trước"
          }
          className="input-lumina flex-1"
          disabled={isLoading || apiKeyValid !== true}
        />
        <button
          onClick={() => handleSendMessage()}
          disabled={!input.trim() || isLoading || apiKeyValid !== true}
          className="btn-lumina-primary px-4 py-2 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
