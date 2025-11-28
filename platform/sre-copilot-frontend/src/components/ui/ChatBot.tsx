import React, { useState, useEffect } from "react";
import { Button } from "./Button";
import { API_BASE_URL } from "../../config";

interface ChatMessage {
  id: string;
  message: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatBotProps {
  apiBaseUrl?: string;
}

export const ChatBot: React.FC<ChatBotProps> = ({
  apiBaseUrl = API_BASE_URL,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const getOrCreateConversationId = () => {
    let id = localStorage.getItem('chatbot_conversation_id');
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem('chatbot_conversation_id', id);
    }
    return id;
  };

  useEffect(() => {
    if (isOpen && !conversationId) {
      setConversationId(getOrCreateConversationId());
    }
  }, [isOpen, conversationId]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/api/chatbot/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_id: conversationId,
          reset_conversation: false,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: data.response || "Sorry, I could not process your request.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={() => setIsOpen(!isOpen)}
          className="rounded-full w-12 h-12 bg-blue-600 hover:bg-blue-700 text-white shadow-lg"
        >
          💬
        </Button>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className={`fixed bg-white border border-gray-300 shadow-xl z-50 flex flex-col ${
          isFullScreen 
            ? 'inset-0 rounded-none' 
            : 'bottom-20 right-4 w-80 h-96 rounded-lg'
        }`}>
          {/* Header */}
          <div className={`bg-blue-600 text-white p-3 flex justify-between items-center ${
            isFullScreen ? 'rounded-none' : 'rounded-t-lg'
          }`}>
            <span className="font-medium">SRE Assistant</span>
            <div className="flex space-x-2">
              <button
                onClick={() => setIsFullScreen(!isFullScreen)}
                className="text-white hover:text-gray-200"
              >
                {isFullScreen ? '⬇' : '⬆'}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white hover:text-gray-200"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.isUser ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-xs p-2 rounded-lg text-sm ${
                    msg.isUser
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {msg.message}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 p-2 rounded-lg text-sm">
                  Typing...
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-3 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                Send
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
