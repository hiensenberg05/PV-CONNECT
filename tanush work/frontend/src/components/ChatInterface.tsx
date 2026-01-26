
"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Send, Video, Phone, MoreVertical, Smile, Paperclip, Mic, Settings } from 'lucide-react';
import { Message, ChatState } from '../types';
import { sendMessage, healthCheck } from '../lib/api';
import MessageBubble from './MessageBubble';
import StateViewer from './StateViewer';

const INITIAL_BOT_MESSAGE: Message = {
    role: 'bot',
    content: "To get started, could you please tell me the name of the medication you're reporting about?",
    id: 'init-1',
    timestamp: new Date()
};

export default function ChatInterface() {
    const [chatState, setChatState] = useState<ChatState>({
        messages: [INITIAL_BOT_MESSAGE],
        userType: 'patient',
        language: 'en',
        caseId: '',
        graphState: null,
        isLoading: false
    });

    const [inputMessage, setInputMessage] = useState('');
    const [showStateViewer, setShowStateViewer] = useState(false);
    const [isBackendConnected, setIsBackendConnected] = useState<boolean | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatState.messages]);

    // Check backend connection on mount
    useEffect(() => {
        const checkConnection = async () => {
            const connected = await healthCheck();
            setIsBackendConnected(connected);
        };
        checkConnection();
        // Check every 30 seconds
        const interval = setInterval(checkConnection, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleSendMessage = async (text: string = inputMessage) => {
        if (!text.trim() || chatState.isLoading) return;

        const userMsg: Message = {
            role: 'user',
            content: text,
            id: Date.now().toString(),
            timestamp: new Date()
        };

        setChatState(prev => ({
            ...prev,
            messages: [...prev.messages, userMsg],
            isLoading: true
        }));
        setInputMessage('');

        try {
            const payload = {
                message: text,
                from_number: chatState.userType === 'patient' ? '+1234567890' : '+0987654321',
                user_type: chatState.userType,
                language: chatState.language,
                case_id: chatState.caseId || undefined
            };

            const response = await sendMessage(payload);

            if (response.status === 'success') {
                const botMsg: Message = {
                    role: 'bot',
                    content: response.data.bot_reply,
                    id: (Date.now() + 1).toString(),
                    timestamp: new Date(),
                    metadata: {
                        confidence_score: response.data.graph_state?.analysis?.confidence_score,
                        risk_level: response.data.graph_state?.analysis?.risk_level
                    }
                };

                setChatState(prev => ({
                    ...prev,
                    messages: [...prev.messages, botMsg],
                    graphState: response.data.graph_state,
                    caseId: response.data.case_id || prev.caseId,
                    isLoading: false
                }));
            } else {
                throw new Error(response.error || 'Unknown backend error');
            }
        } catch (error) {
            const errorMsg: Message = {
                role: 'bot',
                content: `❌ Error: ${error instanceof Error ? error.message : 'Connection failed'}`,
                id: (Date.now() + 1).toString(),
                timestamp: new Date()
            };

            setChatState(prev => ({
                ...prev,
                messages: [...prev.messages, errorMsg],
                isLoading: false
            }));
        }
    };

    return (
        <div className="flex h-screen max-h-screen bg-[#ECE5DD]">
            {/* Main Chat Area */}
            <div className="flex-1 flex flex-col">
                {/* WhatsApp Header */}
                <header className="bg-[#25D366] px-4 py-3 flex items-center justify-between shadow-md shrink-0">
                    <div className="flex items-center gap-3">
                        {/* Avatar */}
                        <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-[#25D366] font-bold text-lg">
                            PW
                        </div>
                        {/* Name and Status */}
                        <div>
                            <h1 className="text-white font-medium text-[16px]">PV Connect</h1>
                            <p className="text-white/90 text-xs flex items-center gap-1">
                                {isBackendConnected === null ? (
                                    <>Checking...</>
                                ) : isBackendConnected ? (
                                    <>✓ Online</>
                                ) : (
                                    <>⚠ Backend Offline</>
                                )}
                            </p>
                        </div>
                    </div>

                    {/* Action Icons */}
                    <div className="flex items-center gap-5">
                        <button className="text-white hover:opacity-80 transition-opacity">
                            <Video size={22} />
                        </button>
                        <button className="text-white hover:opacity-80 transition-opacity">
                            <Phone size={22} />
                        </button>
                        <button
                            onClick={() => setShowStateViewer(!showStateViewer)}
                            className="text-white hover:opacity-80 transition-opacity"
                            title="Toggle Developer State Viewer"
                        >
                            <Settings size={22} />
                        </button>
                        <button className="text-white hover:opacity-80 transition-opacity">
                            <MoreVertical size={22} />
                        </button>
                    </div>
                </header>

                {/* Chat Messages Area */}
                <div className="flex-1 overflow-y-auto px-6 py-4 custom-scrollbar whatsapp-bg">
                    {chatState.messages.map((msg) => (
                        <MessageBubble key={msg.id} message={msg} />
                    ))}
                    {chatState.isLoading && (
                        <div className="flex items-start gap-1 mb-2">
                            <div className="bg-white rounded-lg shadow-sm px-3 py-2 rounded-bl-none message-tail-left">
                                <div className="flex gap-1">
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* WhatsApp Input Area */}
                <div className="bg-[#F0F0F0] px-4 py-2 flex items-center gap-2 shrink-0">
                    {/* Emoji Button */}
                    <button className="text-[#667781] hover:text-[#303030] transition-colors p-2">
                        <Smile size={24} />
                    </button>

                    {/* Attachment Button */}
                    <button className="text-[#667781] hover:text-[#303030] transition-colors p-2">
                        <Paperclip size={24} />
                    </button>

                    {/* Input Field */}
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Type a message..."
                        disabled={chatState.isLoading}
                        className="flex-1 bg-white rounded-full px-4 py-2.5 text-[15px] focus:outline-none disabled:bg-gray-100 disabled:text-gray-400"
                    />

                    {/* Send or Mic Button */}
                    {inputMessage.trim() ? (
                        <button
                            onClick={() => handleSendMessage()}
                            disabled={chatState.isLoading}
                            className="bg-[#25D366] hover:bg-[#128C7E] disabled:bg-gray-300 text-white p-2.5 rounded-full transition-colors"
                        >
                            <Send size={20} />
                        </button>
                    ) : (
                        <button className="text-[#667781] hover:text-[#303030] transition-colors p-2">
                            <Mic size={24} />
                        </button>
                    )}
                </div>
            </div>

            {/* State Viewer Panel (Toggleable) */}
            {showStateViewer && (
                <div className="w-[400px] bg-slate-900 flex flex-col border-l border-slate-800 shadow-xl">
                    <div className="bg-slate-800 px-4 py-3 flex items-center justify-between">
                        <h2 className="text-white font-medium">Developer State</h2>
                        <button
                            onClick={() => setShowStateViewer(false)}
                            className="text-white hover:text-gray-300"
                        >
                            ✕
                        </button>
                    </div>
                    <StateViewer state={chatState.graphState} />
                </div>
            )}
        </div>
    );
}
