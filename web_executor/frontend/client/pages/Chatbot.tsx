import { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Send, Key, CheckCircle, XCircle, Info, ExternalLink } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Array<{
    id: number;
    text: string;
    score: number;
  }>;
}

interface RAGStats {
  enabled: boolean;
  model: string;
  total_documents: number;
  vector_dimension: number;
}

export default function ChatbotPage() {
  const [apiKey, setApiKey] = useState('');
  const [apiKeyValid, setApiKeyValid] = useState<boolean | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [stats, setStats] = useState<RAGStats | null>(null);
  const [showSources, setShowSources] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load API key from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
      setApiKey(savedKey);
    }
  }, []);

  // Fetch RAG stats on mount
  useEffect(() => {
    fetchStats();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v1/rag/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const validateApiKey = async () => {
    if (!apiKey.trim()) {
      return;
    }

    setIsValidating(true);
    try {
      const response = await fetch('/api/v1/rag/validate-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey }),
      });

      const data = await response.json();
      setApiKeyValid(data.valid);

      if (data.valid) {
        localStorage.setItem('gemini_api_key', apiKey);
      }
    } catch (error) {
      console.error('Validation failed:', error);
      setApiKeyValid(false);
    } finally {
      setIsValidating(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !apiKey || apiKeyValid === false) {
      return;
    }

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsSending(true);

    try {
      const response = await fetch('/api/v1/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputMessage,
          api_key: apiKey,
          top_k: 5,
          use_cache: true,
          conversation_history: messages.map((m) => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp.toISOString(),
          })),
        }),
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date(data.timestamp),
          sources: data.sources,
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          role: 'assistant',
          content: `Lỗi: ${data.error || 'Không thể xử lý câu hỏi của bạn'}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Đã xảy ra lỗi khi gửi tin nhắn. Vui lòng thử lại.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-6xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">🤖 Trợ lý Tài chính AI</h1>
        <p className="text-gray-600">
          Hỏi đáp về thị trường chứng khoán Việt Nam với công nghệ RAG + Gemini
        </p>
      </div>

      {/* Stats Banner */}
      {stats && (
        <Alert className="mb-4">
          <Info className="h-4 w-4" />
          <AlertDescription>
            <div className="flex flex-wrap gap-4 text-sm">
              <span>📊 <strong>{stats.total_documents.toLocaleString()}</strong> tin tức tài chính</span>
              <span>🧠 Model: <strong>{stats.model}</strong></span>
              <span>📐 Vector dimension: <strong>{stats.vector_dimension}</strong></span>
            </div>
          </AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* API Key Setup */}
        <div className="lg:col-span-1">
          <Card className="p-4">
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <Key className="h-4 w-4" />
                  Gemini API Key
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Để sử dụng chatbot, bạn cần cung cấp API key của Gemini.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="api-key">API Key</Label>
                <Input
                  id="api-key"
                  type="password"
                  placeholder="AIzaSy..."
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setApiKeyValid(null);
                  }}
                  disabled={isValidating}
                />
              </div>

              <Button
                onClick={validateApiKey}
                disabled={!apiKey.trim() || isValidating}
                className="w-full"
              >
                {isValidating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Đang kiểm tra...
                  </>
                ) : (
                  'Xác thực API Key'
                )}
              </Button>

              {apiKeyValid === true && (
                <Alert className="bg-green-50 border-green-200">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800">
                    API key hợp lệ! Bạn có thể bắt đầu trò chuyện.
                  </AlertDescription>
                </Alert>
              )}

              {apiKeyValid === false && (
                <Alert className="bg-red-50 border-red-200">
                  <XCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-800">
                    API key không hợp lệ. Vui lòng kiểm tra lại.
                  </AlertDescription>
                </Alert>
              )}

              <div className="text-xs text-gray-500 space-y-1">
                <p>💡 <strong>Lấy API key miễn phí:</strong></p>
                <a
                  href="https://makersuite.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline flex items-center gap-1"
                >
                  Google AI Studio
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          </Card>
        </div>

        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <Card className="flex flex-col h-[600px]">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <p className="mb-4">👋 Xin chào! Tôi có thể giúp gì cho bạn?</p>
                  <div className="text-sm space-y-2">
                    <p className="font-semibold">Câu hỏi gợi ý:</p>
                    <ul className="space-y-1">
                      <li>• Tình hình thị trường chứng khoán Việt Nam hiện tại?</li>
                      <li>• VN-Index biến động như thế nào tuần này?</li>
                      <li>• Các ngành nào đang có triển vọng tốt?</li>
                    </ul>
                  </div>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString('vi-VN')}
                    </p>

                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-300">
                        <button
                          onClick={() => setShowSources(showSources === index ? null : index)}
                          className="text-xs underline hover:no-underline"
                        >
                          {showSources === index ? 'Ẩn' : 'Xem'} {message.sources.length} nguồn
                        </button>

                        {showSources === index && (
                          <div className="mt-2 space-y-1">
                            {message.sources.map((source, i) => (
                              <div key={i} className="text-xs bg-white/50 p-2 rounded">
                                <Badge variant="outline" className="mb-1">
                                  Nguồn {i + 1} ({(source.score * 100).toFixed(1)}%)
                                </Badge>
                                <p className="line-clamp-3">{source.text}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isSending && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  placeholder={
                    apiKeyValid
                      ? 'Nhập câu hỏi của bạn...'
                      : 'Vui lòng xác thực API key trước'
                  }
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={!apiKeyValid || isSending}
                  className="flex-1"
                />
                <Button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || !apiKeyValid || isSending}
                >
                  {isSending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 Nhấn Enter để gửi, Shift+Enter để xuống dòng
              </p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
