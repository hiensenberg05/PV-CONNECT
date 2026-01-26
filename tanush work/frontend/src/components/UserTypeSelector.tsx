
import React from 'react';
import { User, Stethoscope } from 'lucide-react';

interface UserTypeSelectorProps {
    userType: 'patient' | 'doctor';
    onUserTypeChange: (type: 'patient' | 'doctor') => void;
}

const UserTypeSelector: React.FC<UserTypeSelectorProps> = ({ userType, onUserTypeChange }) => {
    return (
        <div className="flex p-1 bg-slate-100 rounded-lg border border-slate-200">
            <button
                onClick={() => onUserTypeChange('patient')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-all ${userType === 'patient'
                        ? 'bg-white text-blue-600 shadow-sm border border-slate-100'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                    }`}
            >
                <User size={16} />
                Patient
            </button>
            <button
                onClick={() => onUserTypeChange('doctor')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md text-sm font-medium transition-all ${userType === 'doctor'
                        ? 'bg-white text-blue-600 shadow-sm border border-slate-100'
                        : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'
                    }`}
            >
                <Stethoscope size={16} />
                Doctor
            </button>
        </div>
    );
};

export default UserTypeSelector;
