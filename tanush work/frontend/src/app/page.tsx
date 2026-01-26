
import type { Metadata } from 'next';
import ChatInterface from '../components/ChatInterface';

export const metadata: Metadata = {
  title: 'PV Backend Tester',
  description: 'Testing interface for Pharmacovigilance LangGraph Backend',
};

export default function Home() {
  return (
    <div className="min-h-screen">
      <ChatInterface />
    </div>
  );
}
