
import React from 'react';
import { Message } from '../types';
import { Check, CheckCheck } from 'lucide-react';

interface MessageBubbleProps {
    message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={`flex w-full mb-2 ${isUser ? 'justify-end' : 'justify-start'} message-animate`}>
            <div className={`flex max-w-[75%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-end gap-1`}>
                <div
                    className={`relative px-3 py-2 rounded-lg shadow-sm ${isUser
                        ? 'bg-[#DCF8C6] text-[#303030] rounded-br-none message-tail-right'
                        : 'bg-white text-[#303030] rounded-bl-none message-tail-left'
                        }`}
                    style={{ maxWidth: '100%' }}
                >
                    <p className="whitespace-pre-wrap text-[14.2px] leading-[19px] break-words">
                        {message.content}
                    </p>

                    {/* Timestamp and metadata in message bubble */}
                    <div className={`flex items-center gap-1 mt-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
                        <span className="text-[11px] text-[#667781]" suppressHydrationWarning>
                            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>

                        {/* WhatsApp checkmarks for user messages */}
                        {isUser && (
                            <CheckCheck size={14} className="text-[#53BDEB]" />
                        )}

                        {/* Risk level badge for bot messages */}
                        {!isUser && message.metadata?.risk_level && (
                            <span className={`text-[9px] px-1.5 py-0.5 rounded-full uppercase font-bold ml-1 ${message.metadata.risk_level === 'high' ? 'bg-red-100 text-red-600' :
                                message.metadata.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                                    'bg-green-100 text-green-600'
                                }`}>
                                {message.metadata.risk_level}
                            </span>
                        )}

                        {/* Confidence score for bot messages */}
                        {!isUser && message.metadata?.confidence_score !== undefined && (
                            <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-500 ml-1">
                                {Math.round(message.metadata.confidence_score * 100)}%
                            </span>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
