
export interface Message {
  role: 'user' | 'bot';
  content: string;
  id: string;
  timestamp: Date;
  metadata?: {
    language?: string;
    risk_level?: string;
    confidence_score?: number;
  };
}

export interface ChatState {
  messages: Message[];
  userType: 'patient' | 'doctor';
  language: string;
  caseId?: string;
  graphState: any; // Latest graph state from backend
  isLoading: boolean;
}

export interface GraphState {
  session: {
    user_type: string;
    language: string;
    case_id: string;
  };
  extraction: {
    drug_name?: string;
    symptoms?: string[];
    severity?: string;
    [key: string]: any;
  };
  analysis: {
    is_complete: boolean;
    missing_fields: string[];
    risk_level?: string;
    confidence_score?: number;
  };
  [key: string]: any;
}

export interface BackendResponse {
  status: 'success' | 'error';
  data: {
    bot_reply: string;
    graph_state: GraphState;
    case_id?: string;
  };
  error?: string;
}
