"use client";
import { createContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useRouter } from 'next/navigation';

export const AuthContext = createContext({});

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const id = localStorage.getItem('id');
            const role = localStorage.getItem('role');
            const nome = localStorage.getItem('nome');
            setUser({ id, role, nome, preferencias: null });
        }
        setLoading(false);
    }, []);

    // Timeout de inatividade
    useEffect(() => {
        let timeoutId;
        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            if (user) {
                timeoutId = setTimeout(() => {
                    signOut();
                }, 10 * 60 * 1000); // 10 minutos
            }
        };
        const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove'];
        events.forEach(event => window.addEventListener(event, resetTimer));
        resetTimer();
        return () => {
            events.forEach(event => window.removeEventListener(event, resetTimer));
            if (timeoutId) clearTimeout(timeoutId);
        };
    }, [user]);

    async function signIn(email, senha) {
        try {
            const response = await api.post('/login', { email, senha });
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('role', response.data.role);
            localStorage.setItem('nome', response.data.nome);
            localStorage.setItem('id', response.data.id);
            setUser({ 
                id: response.data.id,
                role: response.data.role, 
                nome: response.data.nome,
                preferencias: null
            });
            router.push('/');
        } catch (error) {
            throw new Error("Credenciais inválidas");
        }
    }

    function signOut() {
        localStorage.clear();
        setUser(null);
        router.push('/login');
    }

    return (
        <AuthContext.Provider value={{ user, loading, setUser, signIn, signOut }}>
            {children}
        </AuthContext.Provider>
    );
}