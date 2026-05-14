"use client";
import { createContext, useState, useEffect } from 'react';
import api from '../services/api';
import { useRouter } from 'next/navigation';

export const AuthContext = createContext({});

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const role = localStorage.getItem('role');
            const nome = localStorage.getItem('nome');
            const prefStr = localStorage.getItem('preferencias');
            const preferencias = prefStr === '' || prefStr === 'null' ? null : prefStr;
            setUser({ role, nome, preferencias });
        }
    }, []);

    async function signIn(email, senha) {
        try {
            const response = await api.post('/login', { email, senha });
            const prefs = response.data.preferencias;
            
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('role', response.data.role);
            localStorage.setItem('nome', response.data.nome);
            localStorage.setItem('preferencias', prefs === null ? '' : prefs);
            
            setUser({ 
                role: response.data.role, 
                nome: response.data.nome,
                preferencias: prefs
            });
            router.push('/');
        } catch (error) {
            // Lança o erro para que a página de login capture e mostre o alerta do Bootstrap
            throw new Error("Credenciais inválidas"); 
        }
    }

    function signOut() {
        localStorage.clear();
        setUser(null);
        router.push('/login');
    }

    return (
        <AuthContext.Provider value={{ user, setUser, signIn, signOut }}>
            {children}
        </AuthContext.Provider>
    );
}