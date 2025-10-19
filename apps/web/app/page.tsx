"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { MessageBubble } from "@/components/message-bubble";
import { ThinkingBubble } from "@/components/thinking-bubble";
import { api } from "@/lib/fetch";
import { Message, Citation } from "@/types/api";
import { Send, Sparkles } from "lucide-react";

const QUICK_PROMPTS = [
  "What is the recommended starting dose of metformin?",
  "What are the contraindications for lisinopril?",
  "What adverse reactions are associated with atorvastatin?",
  "How should I take ibuprofen?",
  "What are the side effects of amoxicillin?",
];

const CHAT_STORAGE_KEY = "med-rag-chat";

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [drug, setDrug] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Load messages from sessionStorage on mount
  useEffect(() => {
    const savedMessages = sessionStorage.getItem(CHAT_STORAGE_KEY);
    if (savedMessages) {
      try {
        setMessages(JSON.parse(savedMessages));
      } catch (error) {
        console.error("Failed to parse saved messages:", error);
      }
    }
  }, []);

  // Save messages to sessionStorage whenever messages change
  useEffect(() => {
    sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      createdAt: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await api.ask({
        query: input.trim(),
        drug: drug.trim() || undefined,
        top_k: 6,
      });

      const citations: Citation[] = response.contexts?.map(ctx => ({
        url: ctx.url,
        section: ctx.section,
      })) || [];

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        citations,
        confidence: response.confidence,
        createdAt: Date.now(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error while processing your request. Please try again.",
        createdAt: Date.now(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    setInput(prompt);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="container mx-auto max-w-6xl p-4 h-[calc(100vh-8rem)]">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-full">
        {/* Main Chat Area */}
        <div className="lg:col-span-3 flex flex-col">
          <Card className="flex-1 flex flex-col">
            <div className="p-4 border-b">
              <h1 className="text-xl font-semibold">Medication Q&A Chat</h1>
              <p className="text-sm text-muted-foreground">
                Ask questions about medication information from official labels
              </p>
            </div>

            <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
              <div className="space-y-4">
                {messages.length === 0 && (
                  <div className="text-center text-muted-foreground py-8">
                    <Sparkles className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Start a conversation by asking about medication information</p>
                    <p className="text-sm mt-2">Try one of the quick prompts on the right</p>
                  </div>
                )}

                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}

                {isLoading && <ThinkingBubble />}
              </div>
            </ScrollArea>

            <div className="p-4 border-t space-y-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Optional: Specify a drug name (e.g., metformin)"
                  value={drug}
                  onChange={(e) => setDrug(e.target.value)}
                  className="flex-1"
                />
              </div>

              <div className="flex gap-2">
                <Textarea
                  placeholder="Ask about medication information... (Enter to send, Shift+Enter for new line)"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  className="flex-1 min-h-[60px] resize-none"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  size="sm"
                  className="self-end"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* Right Panel */}
        <div className="lg:col-span-1 space-y-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Quick Start</h3>
            <div className="space-y-2">
              {QUICK_PROMPTS.map((prompt, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-left h-auto p-3"
                  onClick={() => handleQuickPrompt(prompt)}
                >
                  <span className="text-sm">{prompt}</span>
                </Button>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-3">Guidelines</h3>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div>
                <strong className="text-foreground">Grounding:</strong> Answers are based on official medication labels
              </div>
              <Separator />
              <div>
                <strong className="text-foreground">Citations:</strong> Click source links to verify information
              </div>
              <Separator />
              <div>
                <strong className="text-foreground">Disclaimer:</strong> Not medical advice - consult healthcare professionals
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
